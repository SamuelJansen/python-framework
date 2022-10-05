import json
from python_helper import Constant as c
from python_helper import StringHelper, EnvironmentHelper
from python_helper import log

KW_UI = 'ui'
KW_JSON = 'json'
KW_API = 'api'
KW_OPEN_API = 'swagger'
DOCUMENTATION_FILE_SUFIX = f'{c.DASH}{KW_OPEN_API}{c.DOT}{KW_JSON}'

def getDocumentationFolderPath(apiInstance):
    return f'{apiInstance.globals.staticPackage}{EnvironmentHelper.OS_SEPARATOR}{KW_OPEN_API}'[1:]

def getDocumentationFileName(apiInstance):
    return f'{apiInstance.globals.apiName}{DOCUMENTATION_FILE_SUFIX}'

def getDocumentationFilePath(apiInstance):
    return f'{getDocumentationFolderPath(apiInstance)}{EnvironmentHelper.OS_SEPARATOR}{getDocumentationFileName(apiInstance)}'

def loadDocumentationAsString(apiInstance):
    with open(getDocumentationFilePath(apiInstance), c.READ, encoding=c.ENCODING) as documentationFile :
        documentationAsString = c.NOTHING.join(documentationFile.readlines())
    return documentationAsString

def loadDocumentation(apiInstance):
    documentationAsString = loadDocumentationAsString(apiInstance)
    return json.loads(documentationAsString)

def overrideDocumentation(apiInstance):
    try :
        documentationAsString = StringHelper.prettyJson(apiInstance.documentation)
        documentationFolderPath = getDocumentationFolderPath(apiInstance)
        documentationFilePath = getDocumentationFilePath(apiInstance)
        try:
            if not EnvironmentHelper.isDirectory(documentationFolderPath) :
                accessRights = 0o777 # define the access rights. write and read
                EnvironmentHelper.makeDirectory(documentationFolderPath, accessRights)
        except OSError as exception:
            exceptionMessage = f'Creation of the directory {documentationFilePath} failed'
            log.log(overrideDocumentation, exceptionMessage, exception=exception)
            raise Exception(exceptionMessage)
        with open(getDocumentationFilePath(apiInstance), c.OVERRIDE, encoding=c.ENCODING) as documentationFile :
            documentationFile.write(documentationAsString)
    except Exception as exception :
        log.log(overrideDocumentation,"Error while overriding OpenApi documentation file",exception)
        raise exception
