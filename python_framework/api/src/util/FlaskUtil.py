from flask import Response, request
import flask_restful
from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function
import globals
from python_framework.api.src.util import Serializer


KEY_API_INSTANCE = 'apiInstance'
API_INSTANCE_HOLDER = {
    KEY_API_INSTANCE: None
}

KW_PARAMETERS = 'params'
KW_HEADERS = 'headers'


Response = Response
request = request
Resource = flask_restful.Resource

@Function
def safellyGetRequestBody():
    requestBody = safellyGetJson()
    if ObjectHelper.isNone(requestBody):
        requestBody = safellyGetData()
    return requestBody if ObjectHelper.isNotNone(requestBody) else dict()

@Function
def safellyGetJson():
    jsonBody = None
    try :
        jsonBody = request.get_json(force=True)
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetJson, f'Not possible to get request body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

@Function
def safellyGetResponseJson(response):
    jsonBody = None
    try :
        jsonBody = response.get_json(force=True)
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetResponseJson, f'Not possible to get response body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

@Function
def safellyGetData():
    dataBody = None
    try :
        dataBody = request.get_json(force=True)
    except Exception as exception:
        dataBody = {}
        log.log(safellyGetData, f'Not possible to get data. Returning {dataBody} by default', exception=exception)
    return dataBody

@Function
def safellyGetUrl():
    url = None
    try :
        url = str(request.url)
    except Exception as exception:
        log.log(safellyGetUrl, 'Not possible to get url', exception=exception)
    return url

def safellyGetPath():
    path = None
    try :
        path = str(request.path)
    except Exception as exception:
        path = c.FOWARD_SLASH
        log.log(safellyGetUrl, f'Not possible to get path. Returning {path} by default', exception=exception)
    return path

@Function
def safellyGetVerb():
    verb = None
    try :
        verb = str(request.method)
    except Exception as exception:
        log.log(safellyGetVerb, 'Not possible to get verb', exception=exception)
    return verb

@Function
def safellyGetHeaders():
    headers = None
    try:
        headers= dict(request.headers)
    except Exception as exception:
        headers = {}
        log.log(safellyGetHeaders, f'Not possible to get request headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@Function
def safellyGetResponseHeaders(response):
    headers = None
    try:
        headers= dict(response.headers)
    except Exception as exception:
        headers = {}
        log.log(safellyGetResponseHeaders, f'Not possible to get response headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@Function
def safellyGetArgs():
    args = None
    try:
        args = dict(request.args)
    except Exception as exception:
        args = {}
        log.log(safellyGetArgs, f'Not possible to get args. Returning {args} by default', exception=exception)
    return args if ObjectHelper.isNotNone(args) else dict()

@Function
def buildHttpResponse(additionalResponseHeaders, controllerResponseBody, status, contentType):
    httpResponse = Response(Serializer.jsonifyIt(controllerResponseBody),  mimetype=contentType, status=status)
    for key, value in additionalResponseHeaders.items():
        httpResponse.headers[key] = value
    return httpResponse

@Function
def addToKwargs(key, givenClass, valuesAsDictionary, kwargs):
    if ObjectHelper.isNotEmpty(givenClass):
        toClass = givenClass if ObjectHelper.isNotList(givenClass) else givenClass[0]
        kwargs[key] = Serializer.convertFromJsonToObject({k:v for k,v in valuesAsDictionary.items()}, toClass)
    return valuesAsDictionary

@Function
def getGlobals():
    return globals.getGlobalsInstance()

@Function
def getApi():
    api = None
    try:
        api = getGlobals().api
    except Exception as exception:
        raise Exception(f'Failed to return api from "globals" instance. Cause: {str(exception)}')
    return api

def getNullableApi():
    api = None
    try :
        api = getApi()
    except Exception as exception:
        log.warning(getNullableApi, 'Not possible to get api', exception=exception)
    return api

@Function
def getClassName(instance):
    return instance.__class__.__name__

@Function
def getModuleName(instance):
    return instance.__class__.__module__

@Function
def getQualitativeName(instance):
    return instance.__class__.__qualname__

@Function
def isApiInstance(apiInstance):
    if ObjectHelper.isNone(apiInstance):
        return False
    apiClassName = flask_restful.Api.__name__
    moduleName = flask_restful.__name__
    return apiClassName == getClassName(apiInstance) and apiClassName == getQualitativeName(apiInstance) and moduleName == getModuleName(apiInstance)

def validateFlaskApi(apiInstance):
    if not isApiInstance(apiInstance):
        raise Exception(f'Invalid "flask_restful.Api" instance. {apiInstance} is not an Api instance')

def validateResourceInstance(resourceInstance):
    if ObjectHelper.isNone(resourceInstance):
        raise Exception(f'Resource cannot be None')

@Function
def retrieveApiInstance(apiInstance=None, arguments=None):
    if isApiInstance(apiInstance):
        return apiInstance
    if isApiInstance(API_INSTANCE_HOLDER.get(KEY_API_INSTANCE)):
        return API_INSTANCE_HOLDER.get(KEY_API_INSTANCE)
    if ObjectHelper.isNone(apiInstance) and ObjectHelper.isNotNone(arguments):
        try:
            apiInstance = arguments[0].globals.api
        except Exception as exception:
            log.warning(retrieveApiInstance, f'''Not possible to retrieve api instance by {arguments}. Going for another approach''', exception=exception)
    if not isApiInstance(apiInstance):
        log.warning(retrieveApiInstance, f'''Not possible to retrieve api instance. Going for a slower approach''')
        apiInstance = getNullableApi()
    if ObjectHelper.isNone(apiInstance):
        raise Exception('Not possible to retrieve api instance')
    API_INSTANCE_HOLDER[KEY_API_INSTANCE] = apiInstance
    return apiInstance
