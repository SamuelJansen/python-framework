import json
from python_helper import Constant as c
from python_helper import StringHelper

def getDocumentationFilePath(globals):
    g = globals
    return f'{g.apiPath}api{g.OS_SEPARATOR}resource{g.OS_SEPARATOR}swaggerui{g.OS_SEPARATOR}swagger.json'

def loadDocumentationAsString(globals):
    documentationFilePath = getDocumentationFilePath(globals)
    with open(documentationFilePath, globals.READ, encoding=globals.ENCODING) as documentationFile :
        documentationAsString = c.NOTHING.join(documentationFile.readlines())
    return documentationAsString

def loadDocumentation(globals):
    documentationAsString = loadDocumentationAsString(globals)
    return json.loads(documentationAsString)

def overrideDocumentation(globals, documentation):
    documentationAsString = StringHelper.stringfyThisDictionary(documentation)
    documentationFilePath = getDocumentationFilePath(globals)
    with open(documentationFilePath, globals.OVERRIDE, encoding=globals.ENCODING) as documentationFile :
        documentationFile.write(documentationAsString)
