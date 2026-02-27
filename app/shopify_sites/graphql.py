import math
import urllib.error
import shopify
import json
from home.lmno import *
import logging
import urllib
import time
import signal
import http.client
import traceback
logger = logging.getLogger(__name__)

def sigInt(signal,frame):
    sys.exit()

signal.signal(signal.SIGINT,sigInt)

def log(message):
    print(message,flush=True)

class GqlReturn(SearchableDict):
    def errors(self,dump=False):
        if not hasattr(self,"errorDetails"):
            errorDetails = self.findErrors(self.data)
            setattr(self,"errorDetails",errorDetails)
            
               
        return self.errorDetails
        
    def findErrors(self,object):
        if isinstance(object, dict):
            if "userErrors" in object:
                return object["userErrors"]
            elif "errors" in object:
                return [{"message":x.get("message"),"code":"NA","field":SearchableDict(x).search("problems[0].path[-1]")} for x in object.get("errors")]
            for key in object:
                item = self.findErrors(object[key])
                if item is not None:
                    return item
            
        elif isinstance(object, list):  
            for element in object:
                item = self.findErrors(element)
                if item is not None:
                    return item
        return None
    def errorMessages(self):
        if self.errors() is None:
            return []
        return [x.get("message") for x in self.errors()]
    def errorCodes(self):
        if self.errors() is None:
            return []
        return [x.get("code") for x in self.errors()]
    def hasErrorCode(self,code):
        return code in self.errorCodes()
    def hasErrors(self):
        return self.errors() is not None and  len(self.errors())>0
    def nodes(self,path):
        return [GqlReturn(x) for x in self.search(f"{path}.nodes",[])]
    def throttleRemaining(self):
        return self.search("extensions.cost.throttleStatus.currentlyAvailable",0)
    def maxThrottle(self):
        return self.search("extensions.cost.throttleStatus.maximumAvailable",0)    
    
    def isDevThrottled(self):
        errors = self.findErrors(self.data)
        if errors is not None:
            for error in errors:
                
                if "Too many attempts" in error.get("message",error.get("code")):
                    return True
        return False
    def getDataRoot(self):
        actualData = None
        if self.data.get("data") is None:
            return self
        
        for key,value in self.data.get("data").items():
            if key not in ["errors","userErrors"]:
                actualData = value        
                break
        if actualData is not None:
            self.data = actualData
        return SearchableDict(self.data)
    def isUnauthorized(self):
        if "Unauthorized" in self.errorMessages():
            return True
        return False
    def asGql(self,path):
        return GqlReturn(self.search(path))


def log(message):
    logger.error(message)
    

def catchNetWorkError(fn):
    def wrapper(self, *args, **kwargs):
        retry = True
        retryCount = 0
        while retry and retryCount<10:
            try:
                ret:GqlReturn = fn(self,*args, **kwargs)
                
                if ret.isDevThrottled():
                    retry = True
                    retryCount = retryCount + 1
                    log(f"dev throttle: retrying {retryCount}/10")
                    time.sleep(20)
                else:
                    retry = False
                    return ret
            except urllib.error.HTTPError as e:
                logger.error(e.status)
                if e.status==401:
                    return GqlReturn(
                        {
                            "data":{},
                            "errors":[
                                {
                                    "code":401,
                                    "message":"Unauthorized"
                                }
                            ]
                        }
                    )
                retryCount = retryCount + 1
                log(f"retrying {retryCount}/10")
                time.sleep(3)
            except urllib.error.URLError as e:
                logger.error(e)
                return GqlReturn(
                        {
                            "data":{},
                            "errors":[
                                {
                                    "code":401,
                                    "message":"Unauthorized"
                                }
                            ]
                        }
                    )
                retryCount = retryCount + 1
                log(f"retrying {retryCount}/10")
                time.sleep(3)
            except http.client.RemoteDisconnected:
                logger.error(e)
                retryCount = retryCount + 1
                log(f"retrying {retryCount}/10")
                time.sleep(3)
            except KeyboardInterrupt:
                sys.exit()
            except SystemExit:
                sys.exit()
            
    
            except Exception as e:
                traceback.print_exc()
                logger.error(e.__class__)
                retryCount = retryCount + 1
                log(f"retrying {retryCount}/10")
                time.sleep(3)
    wrapper.__name__ = fn.__name__
    return wrapper
    
class GraphQL:
    def __init__(self,debug=False,searchable=True,minThrottle=1000):
        self.debugging = debug
        self.debuggingIndent=1
        self.searchable = searchable
        self.minThrottleAvailable=minThrottle
    def debug(self,value=True,level=1):
        self.debugging = value
        self.debuggingIndent = level
        
    @catchNetWorkError    
    def run(self,query,variables={},searchable=True,throttle=5000) -> GqlReturn:
        retVal = None
        ret = None
        try:
            jsonReturn = shopify.GraphQL().execute(query,variables)
            ret = json.loads(jsonReturn)
        except SystemExit:
            sys.exit()    
        except KeyboardInterrupt:
            sys.exit()
        except:
            traceback.print_exc()
            
            return GqlReturn(
                {
                    "data":{},
                    "errors":[
                        {
                            "code":401,
                            "message":"Unauthorized"
                        }
                    ]
                }
            )
        
        retVal = GqlReturn(ret)
        try:
            remaining = retVal.throttleRemaining()
            max = retVal.maxThrottle()
            percentageRemaining = math.ceil((remaining/max)*100)
            if percentageRemaining<25:
                log(f"throttling at {remaining}")
                time.sleep(5)
        except:
            logger.error(json.dumps(retVal.data,indent=1))
        return retVal
    def iterable(self,query,params,dataroot="data.products"):
        return GraphQlIterable(query,params,dataroot=dataroot)
        pass
    
        
class GraphQlIterable(GraphQL):
    def __init__(self, query,params,dataroot="data.products"):
        super().__init__(searchable=True,debug=False)
        self.cursor = None
        self.hasNext = True
        self.query = query
        self.params = params
        self.dataroot = dataroot
    def __iter__(self):
        return self
    def __next__(self):
        if not self.hasNext:
            raise StopIteration
        self.params["after"] = self.cursor
        ret = self.run(self.query,self.params)
        if ret.get("data") is not None:
            try:
                self.dataroot = f'data.{next(iter(ret.search("data").keys()),None)}'
            except:
                ret.dump()
        
        
        values = [GqlReturn(x) for x in ret.search(f"{self.dataroot}.nodes",[])]
        
        if ret.search(f"{self.dataroot}.pageInfo.hasNextPage"):
            self.hasNext = True
            self.cursor = ret.search(f"{self.dataroot}.pageInfo.endCursor")
            
        else:
            self.hasNext = False
        return values
        
        
