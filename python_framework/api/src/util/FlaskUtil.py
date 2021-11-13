from flask import Response, request
import flask_restful
from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function
import globals


KEY_API_INSTANCE = 'apiInstance'
API_INSTANCE_HOLDER = {
    KEY_API_INSTANCE: None
}


Response = Response
request = request
Resource = flask_restful.Resource

def safellyGetRequestBody() :
    requestBody = safellyGetJson()
    if ObjectHelper.isNone(requestBody):
        requestBody = safellyGetData()
    return requestBody if ObjectHelper.isNotNone(requestBody) else dict()

def safellyGetJson():
    jsonBody = None
    try :
        jsonBody = request.get_json(force=True)
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetJson, f'Not possible to get request body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

def safellyGetResponseJson(response):
    jsonBody = None
    try :
        jsonBody = response.get_json(force=True)
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetResponseJson, f'Not possible to get response body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

def safellyGetData():
    dataBody = None
    try :
        dataBody = request.get_json(force=True)
    except Exception as exception:
        dataBody = {}
        log.log(safellyGetData, f'Not possible to get data. Returning {dataBody} by default', exception=exception)
    return dataBody

def safellyGetUrl() :
    url = None
    try :
        url = request.url
    except Exception as exception :
        log.log(safellyGetUrl, 'Not possible to get url', exception=exception)
    return url

def safellyGetVerb() :
    verb = None
    try :
        verb = request.method
    except Exception as exception :
        log.log(safellyGetVerb, 'Not possible to get verb', exception=exception)
    return verb

def safellyGetHeaders():
    headers = None
    try:
        headers= request.headers
    except Exception as exception :
        headers = {}
        log.log(safellyGetHeaders, 'Not possible to get request headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

def safellyGetResponseHeaders(response):
    headers = None
    try:
        headers= response.headers
    except Exception as exception :
        headers = {}
        log.log(safellyGetResponseHeaders, 'Not possible to get response headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

def safellyGetArgs():
    args = None
    try:
        args = request.args
    except Exception as exception :
        args = {}
        log.log(safellyGetArgs, f'Not possible to get args. Returning {args} by default', exception=exception)
    return args if ObjectHelper.isNotNone(args) else dict()

def buildHttpResponse(additionalResponseHeaders, controllerResponseBody, status, contentType):
    httpResponse = Response(Serializer.jsonifyIt(controllerResponseBody),  mimetype=contentType, status=status)
    for key, value in additionalResponseHeaders.items():
        httpResponse.headers[key] = value
    return httpResponse

@Function
def getGlobals() :
    return globals.getGlobalsInstance()

def getApi() :
    api = None
    try:
        api = getGlobals().api
    except Exception as exception :
        raise Exception(f'Failed to return api from "globals" instance. Cause: {str(exception)}')
    return api

def getNullableApi() :
    api = None
    try :
        api = getApi()
    except Exception as exception :
        log.warning(getNullableApi, 'Not possible to get api', exception=exception)
    return api

def getClassName(instance) :
    return instance.__class__.__name__

def getModuleName(instance) :
    return instance.__class__.__module__

def getQualitativeName(instance) :
    return instance.__class__.__qualname__

def isApiInstance(apiInstance):
    if ObjectHelper.isNone(apiInstance):
        return False
    apiClassName = flask_restful.Api.__name__
    moduleName = flask_restful.__name__
    return apiClassName == getClassName(apiInstance) and apiClassName == getQualitativeName(apiInstance) and moduleName == getModuleName(apiInstance)

def validateFlaskApi(apiInstance) :
    if not isApiInstance(apiInstance) :
        raise Exception(f'Invalid "flask_restful.Api" instance. {apiInstance} is not an Api instance')

def validateResourceInstance(resourceInstance) :
    if ObjectHelper.isNone(resourceInstance) :
        raise Exception(f'Resource cannot be None')

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
