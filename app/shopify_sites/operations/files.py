import pathlib
from typing import Dict
from esc.data import *
from ..graphql import *
import requests
import magic
from xyz import settings

class FileDetails(object):
    url = None
    id = None
    alt = None
    filename = None
    def __init__(self,node:Searchable):
        if node is None:
            return self
        self.url = node.search("preview.image.url")
        if self.url is not None:
            self.filename = self.url.split("?")[0].split("/")[-1]
        self.id = node.get("id")
        self.alt = node.get("id")
        self.filename = node.get("filename")
    def dict(self):
        return {
            "url":self.url,
            "id":self.id,
            "filename":self.filename
        }

class Files(GraphQL):
    def __init__(self, debug=False, searchable=True, minThrottle=1000):
        super().__init__(debug, searchable, minThrottle)
    def getFileDetails(self,filename) -> FileDetails:
        filesList = GraphQL().run(
            """
            query getDBFIles($query:String) {
                files(first:10,query:$query) {
                    nodes {
                        id
                        alt
                        preview {
                            image {
                                url
                            }
                        }
                    }
                }
            }
            """,
            {
                "query":f"filename:{filename}"
            }
        )
        
        return next(
            filter(
                lambda image:image.filename==filename,
                [FileDetails(x) for x in filesList.nodes("data.files")]
            ),
            FileDetails(Searchable({}))
        )
        return file
    
        
    def createOne(self,url,filename,type,wait=False) -> FileDetails:

        fileId = self.getFileDetails(filename).id
        if fileId is not None:
            return fileId
        
        ret = fileOperation = GraphQL().run(
            """
            mutation fileCreate($files: [FileCreateInput!]!) {
                fileCreate(files: $files) {
                    files {
                        id
                        alt
                        fileStatus
                        preview {
                            image {
                                url
                            }
                        }
                    }
                    userErrors {
                        field
                        message
                        code
                    }
                }
            }
            """,
            {
                "files":[
                    {
                        "originalSource":url,
                        "filename":filename,
                        "contentType":type,
                        "alt":filename,
                        "duplicateResolutionMode":"REPLACE"
                    }
                ]
            }
        )
        fileDetails = FileDetails(ret.searchable("data.fileCreate.files[0]"))
        if fileDetails.id is None:
            ret.dump()
            return None
        if fileDetails.url is not None or wait is False:
            return fileDetails
        
        if wait:
            attemptsCount = 0
            while attemptsCount<5:
                imageDetails = self.getFileDetails(filename)
                
                if imageDetails.url is not None:
                    return imageDetails
                attemptsCount+=1
                time.sleep(1)    
        return imageDetails

    def create(self,files) -> Dict[str,FileDetails]:

        fileOperation = GraphQL().run(
                """
                mutation fileCreate($files: [FileCreateInput!]!) {
                    fileCreate(files: $files) {
                        files {
                            id
                            alt
                            fileStatus
                            preview {
                                image {
                                    url
                                }
                            }
                        }
                        userErrors {
                            field
                            message
                            code
                        }
                    }
                }
                """,
                {
                    "files":files
                }
            )
        
        return {
            image.filename:image for image in 
            map(
                lambda node:FileDetails(node),
                fileOperation.getAsSearchable("data.fileCreate.files",[])
            )
        }
    def update(self,files):
        fileOperation = GraphQL().run(
                """
                mutation fileUpdate($files: [FileUpdateInput!]!) {
                    fileUpdate(files: $files) {
                        files {
                            id
                            preview {
                                image {
                                    url
                                }
                            }
                            alt
                            fileStatus
                        }
                        userErrors {
                            field
                            message
                            code
                        }
                    }
                }
                """,
                {
                    "files":files
                }
            )
        return {
            image.filename:image for image in 
            map(
                lambda node:FileDetails(node),
                fileOperation.getAsSearchable("data.fileUpdate.files",[])
            )
        }
    def upload(self,file:pathlib.Path,update=False) -> FileDetails:
        filename = file.name
        file:FileDetails = self.getFileDetails(filename)

        if file.id is not None and not update:
            return file.id
        stageUpload = GraphQL().run(
            """
            mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
                stagedUploadsCreate(input: $input) {
                    stagedTargets {
                        url
                        resourceUrl
                        parameters {
                            name
                            value
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """,
            {
                "input":[
                    {
                        "filename":filename,
                        "mimeType":magic.from_file(file.filename),
                        "resource":"FILE",
                        "httpMethod":"PUT"
                    },
                ]
            }
        )
        stagedUpload = stageUpload.getAsSearchable("data.stagedUploadsCreate.stagedTargets[0]")
        stagedUploadUrl = stagedUpload.get("resourceUrl")
        headers = {x.get("name"):x.get("value") for x in stagedUpload.get("parameters")}
        
        response = requests.put(
            stagedUpload.get("url"),
            data=open(file,"rb"),
            headers=headers
        )
        
        fileOperation = None
        fileId = None
        if fileId is None:
            
            fileOperation = GraphQL().run(
                """
                mutation fileCreate($files: [FileCreateInput!]!) {
                    fileCreate(files: $files) {
                        files {
                            id
                            fileStatus
                            alt
                            createdAt
                        }
                        userErrors {
                            field
                            message
                        }
                    }
                }
                """,
                {
                    "files":[
                        {
                            "alt":fileName,
                            "contentType":"IMAGE" if "image" in magic.from_file(file) else "FILE",
                            "originalSource":stagedUploadUrl

                        }
                    ]
                }
            )
            imageId = fileOperation.search("data.fileCreate.files[0].id",None)
        else:
            
            fileOperation = GraphQL().run(
                    """
                    mutation fileUpdate($files: [FileUpdateInput!]!) {
                        fileUpdate(files: $files) {
                            files {
                                id
                                alt
                                fileStatus
                            }
                            userErrors {
                                field
                                message
                                code
                            }
                        }
                    }
                    """,
                    {
                        "files":[
                            {
                                "id":fileId,
                                "originalSource":stagedUploadUrl

                            }
                        ]
                    }
                )
            imageId = fileOperation.search("data.fileUpdate.files[0].id",None)

        return imageId
    