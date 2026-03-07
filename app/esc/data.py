from decimal import Decimal
import json
from django.forms import model_to_dict
from django.db import models
from jmespath import search as jpath
import datetime
from dict_recursive_update import recursive_update
from pathlib import Path
import sys

from bs4 import BeautifulSoup
import phonenumbers




class Data:
    @staticmethod
    def jsonify(value):
        if isinstance(value,dict):
            ret = {}
            for key,value in value.items():
                if isinstance(value,Decimal):
                    ret[key] = float(value)
                elif isinstance(value,datetime.datetime):
                    ret[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value,datetime.date):
                    ret[key] = value.strftime("%Y-%m-%d")
                elif hasattr(value,'dict'):
                    return value.data
                elif isinstance(value,bytes):
                    ret[key] = str(value)
                else:
                    ret[key] = Data.jsonify(value)
            return ret
        elif isinstance(value,list):
            return [Data.jsonify(x) for x in value]
        elif isinstance(value,Searchable):
            return value.data
        else:
            return value
    @staticmethod
    def formatPhone(phone):
        try:
            return phonenumbers.format_number(phonenumbers.parse(phone,'US'),phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            print(f"well this number just wrecked everything: {phone}",file=sys.stderr)
        return ""
    @staticmethod
    def partition(allrows,chunksize=4):
        ret = []
        
        total = len(allrows)
        
        if (total<chunksize):
            return [allrows]
            
        chunks = int(len(allrows)/chunksize)+ 1 if total%chunksize>0 else int(len(allrows)/chunksize)
        
        for i in range(chunks):
            slicer = slice
            ret.append(allrows[:chunksize])
            
            allrows = allrows[chunksize:]
        return ret
class Html(object):
    @staticmethod
    def extractLinks(html,tag):
        soup = BeautifulSoup(html, "html.parser")
        return [
            {"url":tag.attrs.get("href"),"label":tag.string}
            for tag in soup.find_all(tag)
        ]
    @staticmethod
    def extractLinkUrls(html,tag):
        return [x.get("url") for x in Html.extractLinks(html,tag)]
    @staticmethod
    def extractSources(html,tagName):
        if html is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        return [
            tag.attrs.get("src") for tag in soup.find_all(tagName)
        ]
    @staticmethod
    def extractHtmlImages(html,tagName):
        return [
            tag.split("?")[0].split("/")[-1] for tag in Html.extractSources(html,tagName)
        ]
    @staticmethod
    def htmlToRichtext(html):
        soup = BeautifulSoup(html, "html.parser")
        root = {"type": "root", "children": []}
        for element in soup.children:
            parsed_element = Html.parseHtml(soup,element)
            if parsed_element:
                root["children"].append(parsed_element)
        return root
    
    @staticmethod
    def htmlToText(html):
        soup = BeautifulSoup(html,'html.parser')
        return soup.get_text(html)
    
    @staticmethod
    def parseHtml(soup,element):
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                return {
                    "type": "heading",
                    "children": [{"type": "text", "value": element.get_text(strip=True)}],
                    "level": int(element.name[1])
                }
            
            elif element.name == "p":
                children = []
                for child in element.children:
                    if child.name == "em":
                        children.append({"type": "text", "value": child.get_text(strip=True), "italic": True})
                    elif child.name == "strong":
                        children.append({"type": "text", "value": child.get_text(strip=True), "bold": True})
                    elif child.name == "a":
                        if child.has_attr("target"):
                            if child.has_attr("title"):
                                children.append({"type": "link", "url": child["href"], "target": child["target"], "title": child["title"], "children": [{"type": "text", "value": child.get_text(strip=True)}]})
                            else:
                                children.append({"type": "link", "url": child["href"], "children": [{"type": "text", "value": child.get_text(strip=True)}]})
                        else:
                            if child.has_attr("title"):
                                children.append({"type": "link", "url": child["href"], "title": child["title"], "children": [{"type": "text", "value": child.get_text(strip=True)}]})
                            else:
                               children.append({"type": "link", "url": child["href"], "children": [{"type": "text", "value": child.get_text(strip=True)}]})
                    elif child.name is None:
                        children.append({"type": "text", "value": child.strip()})
                return {"type": "paragraph", "children": children}
            
            elif element.name in ["ul", "ol"]:
                list_type = "unordered" if element.name == "ul" else "ordered"
                children = []
                for li in element.find_all("li", recursive=False):
                    children.append(Html.parseHtml(soup,li))
                return {"listType": list_type, "type": "list", "children": children}
            
            elif element.name == "li":
                children = []
                for child in element.children:
                    if child.name == "i":
                        children.append({"type": "text", "value": child.get_text(strip=True), "italic": True})
                    elif child.name == "strong":
                        children.append({"type": "text", "value": child.get_text(strip=True), "bold": True})
                    elif child.name is None:
                        children.append({"type": "text", "value": child.strip()})
                return {"type": "list-item", "children": children}
            
            return None
    @staticmethod
    def replaceAttributes(html,tagName,attribute,replacements:dict,removeInvalid=False):
        soup = BeautifulSoup(html,'html.parser')
        for tag in soup.find_all(tagName):
            source = tag.attrs.get(attribute)
            if source is not None:
                sourceFilename = source.split("?")[0].split("/")[-1]
                replacementValue = replacements.get(sourceFilename)
                
                if replacementValue is not None:
                    tag[attribute] = replacementValue
                else:
                    tag.decompose()
        return soup.prettify()
        

class Searchable(object):
    def __init__(self,data=None):
        self.data = None
        if data is None:
            data = {}
        elif isinstance(data,dict):
            data = Data.jsonify(data)
        elif isinstance(data,Searchable):
            self.data = data.data
        elif isinstance(data,models.Model):
            data = Data.jsonify(model_to_dict(data))
        self.data = data

    def dict(self):
        return self.data
    def dumps(self):
        return json.dumps(Data.jsonify(self.dict()))
    def valid(self):
        return self.data is not None
    def search(self,path,default=None):
        ret =  jpath(path,self.data)
        if ret is None:
            return default
        return ret
    def has(self,key):
        return hasattr(self,key)
    def get(self,key,default=None):
        if self.data is None:
            return None
        return self.data.get(key,default)
        
    def valueOf(self,key):
        ret = self.get(key)
        if ret is dict and self.search(f"{key}.refName"):
            return self.search(f"{key}.refName")
        else:
            return ret
    def dump(self,printIt=True,handle=sys.stdout):
        if printIt:
            print(json.dumps(Data.jsonify(self.data),indent=1),file=handle)
        else:
            return self.data
    def null(self):
        return self.data is None
    def empty(self):
        if self.null():
            return True
        if len(self.data)<1:
            return True
        return False
    def set(self,key,value):
        
        paths = list(reversed(key.split(".")))
        if isinstance(value,Searchable):
            value = value.data
        elif isinstance(value,list):
            value = [Data.jsonify(x) for x in value]
        elif isinstance(value,dict):
            value = Data.jsonify(value)
        if len(paths)>1:
            object = value
            for k in paths:
                object = {k:object}
            self.data = recursive_update(self.data,object)
        else:
            if self.data is not None:
                self.data[key] = value
    def clear(self,path):
        paths = list(reversed(path.split(".")))
        if len(paths)>1:
            object = self.data
            for path in paths[0:-1]:
                if path in object:
                    object = object[path]
            finalKey = paths[-1]
            if isinstance(object,dict):
                if finalKey in object:
                    del object[finalKey]
        else:
            if self.data is not None:
                del self.data[path]
                
    def searchable(self,key,default=None):
        return self.getAsSearchable(key,default)
    
    def getAsSearchable(self,key,default={}):
        val = self.search(key)
        if isinstance(val,list):
            return [Searchable(x) for x in val]
        if isinstance(val,dict):
            return Searchable(val)
        if val is None:
            return Searchable(None)
        return val
    
    def append(self,key,value):
        myValue = self.search(key,[])
        myValue.append(value)
        self.set(key,myValue)
        return
        if key not in self.data:
            self.data[key] = value
        elif type(self.data[key]) is not list:
            self.data[key] = [self.data[key],value]
        else:
            self.data[key].append(value)
    def concat(self,key,value=[]):
        myValue = self.search(key,[])
        myValue+=value
        self.set(key,myValue)
        return
    @staticmethod
    def fromList(list):
        return [Searchable(x) for x in list]
    def dumpField(self,path):
        ret = self.search(path)
        if ret is None:
            print("None")
        else:
            if isinstance(ret,dict) or isinstance(ret,list):
                print(json.dumps(ret,indent=1))
            else:
                print(ret)
    def __str__(self):
        return json.dumps(self.data)
    @staticmethod
    def load(path:Path):
        if path.exists():
            return Searchable(json.load(open(path)))
        else:
            with open(path,"w") as initfile:
                json.dump({},initfile)
            return Searchable

class Vars:
    def __init__(self):
        self.path = Path("./.project_vars.json")
        file = Path(self.path)
        if file.exists():
            with open(file) as jsonFile:
                self.data = Searchable(json.load(jsonFile))
        else:
            self.data = {}
            self.write(self.data)
        
    def write(self):
        with open(self.path,"w") as jsonFile:
            json.dump(self.data.dict(),jsonFile)
    def get(self,path,default=None):
        return self.data.search(path,default)
    
    @staticmethod
    def value(path,default=None):
        return Vars().get(path,default)
    @staticmethod
    def set(path,value):
        vars = Vars()
        vars.data.set(path,value)
        vars.write()

def modelToJson(model):
    return model_to_dict(model)|{"id":str(model.id)}