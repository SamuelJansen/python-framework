import json
from python_helper import Constant as c
from python_helper import StringHelper


KW_UI = 'ui'
KW_JSON = 'json'
KW_API = 'api'
KW_RESOURCE = 'resource'
KW_OPEN_API = 'swagger'
DOCUMENTATION_FILE = f'{KW_OPEN_API}{c.DOT}{KW_JSON}'

def getDocumentationFolderPath(apiInstance):
    globals = apiInstance.globals
    return f'{globals.currentPath}{KW_API}{globals.OS_SEPARATOR}{KW_RESOURCE}{globals.OS_SEPARATOR}{KW_OPEN_API}{KW_UI}'
    # return f'{apiInstance.documentationFolder}{g.OS_SEPARATOR}{DOCUMENTATION_FILE}'

def getDocumentationFilePath(apiInstance):
    # return f'{g.apiPath}api{g.OS_SEPARATOR}resource{g.OS_SEPARATOR}swaggerui{g.OS_SEPARATOR}swagger.json'
    return f'{getDocumentationFolderPath(apiInstance)}{globals.OS_SEPARATOR}{DOCUMENTATION_FILE}'

def loadDocumentationAsString(apiInstance):
    documentationFilePath = getDocumentationFilePath(apiInstance)
    with open(documentationFilePath, globals.READ, encoding=globals.ENCODING) as documentationFile :
        documentationAsString = c.NOTHING.join(documentationFile.readlines())
    return documentationAsString

def loadDocumentation(apiInstance):
    documentationAsString = loadDocumentationAsString(apiInstance)
    return json.loads(documentationAsString)

def overrideDocumentation(apiInstance):
    globals = apiInstance.globals
    documentationAsString = StringHelper.stringfyThisDictionary(apiInstance.documentation)
    documentationFilePath = getDocumentationFilePath(apiInstance)
    with open(documentationFilePath, globals.OVERRIDE, encoding=globals.ENCODING) as documentationFile :
        documentationFile.write(documentationAsString)
