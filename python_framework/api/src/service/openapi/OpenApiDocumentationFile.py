import json
from python_helper import Constant as c
from python_helper import StringHelper

KW_UI = 'ui'
KW_JSON = 'json'
KW_API = 'api'
KW_RESOURCE = 'resource'
KW_OPEN_API = 'swagger'
DOCUMENTATION_FILE_SUFIX = f'{c.DASH}{KW_OPEN_API}{c.DOT}{KW_JSON}'

def getDocumentationFolderPath(apiInstance):
    return apiInstance.documentationFolderPath

def getDocumentationFileName(apiInstance):
    return f'{apiInstance.globals.apiName}{DOCUMENTATION_FILE_SUFIX}'

def getDocumentationFilePath(apiInstance):
    return f'{apiInstance.documentationFolderPath}{getDocumentationFileName(apiInstance)}'

def loadDocumentationAsString(apiInstance):
    globals = apiInstance.globals
    with open(getDocumentationFilePath(apiInstance), globals.READ, encoding=globals.ENCODING) as documentationFile :
        documentationAsString = c.NOTHING.join(documentationFile.readlines())
    return documentationAsString

def loadDocumentation(apiInstance):
    documentationAsString = loadDocumentationAsString(apiInstance)
    return json.loads(documentationAsString)

def overrideDocumentation(apiInstance):
    globals = apiInstance.globals
    documentationAsString = StringHelper.stringfyThisDictionary(apiInstance.documentation)
    with open(getDocumentationFilePath(apiInstance), globals.OVERRIDE, encoding=globals.ENCODING) as documentationFile :
        documentationFile.write(documentationAsString)
