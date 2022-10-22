from flask import Response, request
import flask_restful

from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function
import globals

from python_framework.api.src.util import Serializer
from python_framework.api.src.enumeration.HttpStatus import HttpStatus


KEY_API_INSTANCE = 'apiInstance'
API_INSTANCE_HOLDER = {
    KEY_API_INSTANCE: None
}

KW_PARAMETERS = 'params'
KW_HEADERS = 'headers'

UNKNOWN_VERB = 'UNKNOWN'

CLIENT_RESPONSE_TEXT = '__clientResponseText__'
CLIENT_RESPONSE = '__clientResponse__'

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
def safellyGetRequestBodyOrRequestData():
    requestBody = safellyGetJson()
    if ObjectHelper.isEmpty(requestBody):
        requestData = safellyGetData()
    return requestBody if ObjectHelper.isNotNone(requestBody) else requestData if ObjectHelper.isNotNone(requestData) else dict()

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
def safellyGetFlaskResponseJson(response: Response):
    jsonBody = None
    try :
        jsonBody = response.get_json(force=True)
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetFlaskResponseJson, f'Not possible to get response body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

@Function
def safellyGetResponseJson(response):
    jsonBody = {
        CLIENT_RESPONSE_TEXT: c.BLANK,
        CLIENT_RESPONSE: response
    }
    if ObjectHelper.isNone(response):
        log.log(safellyGetResponseJson, f'Response is None. Returning {jsonBody} by default')

    try :
        jsonBody = response.json()
    except Exception as exception:
        try:
            jsonBody = {
                CLIENT_RESPONSE_TEXT: response.text,
                CLIENT_RESPONSE: response
            }
            log.log(safellyGetResponseJson, f'Not possible to get response body. Returning {jsonBody} by default', exception=exception)
        except Exception as innerException:
            log.log(safellyGetResponseJson, f'Not possible to get response body neither response data. Returning {jsonBody} by default', exception=innerException)
    return jsonBody

@Function
def safellyGetData():
    dataBody = None
    try :
        # dataBody = request.get_json(force=True)
        dataBody = request.data
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

def safellyGetHost():
    host = None
    try :
        path = str(request.host)
    except Exception as exception:
        host = c.FOWARD_SLASH
        log.log(safellyGetUrl, f'Not possible to get host. Returning {host} by default', exception=exception)
    return host

def safellyGetPath():
    path = None
    try :
        path = str(request.path)
    except Exception as exception:
        path = c.FOWARD_SLASH
        log.log(safellyGetPath, f'Not possible to get path. Returning {path} by default', exception=exception)
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
        requestHeaders = dict(request.headers)
        headers = {
            k: Serializer.getUncheckedKeyValue(k, v)
            for k, v in requestHeaders.items()
        }
    except Exception as exception:
        headers = {}
        log.log(safellyGetHeaders, f'Not possible to get request headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()


@Function
def safellyGetHeader(headerName):
    return safellyGetHeaders().get(headerName)


@Function
def safellyGetResponseHeaders(response):
    headers = None
    try:
        responseHeaders = dict(response.headers)
        headers = {
            k: Serializer.getUncheckedKeyValue(k, v)
            for k, v in responseHeaders.items()
        }
    except Exception as exception:
        headers = {}
        log.log(safellyGetResponseHeaders, f'Not possible to get response headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@Function
def safellyGetRequestHeadersFromResponse(response):
    headers = None
    try:
        requestHeaders = dict(response.request.headers)
        headers = {
            k: Serializer.getUncheckedKeyValue(k, v)
            for k, v in requestHeaders.items()
        }
    except Exception as exception:
        headers = {}
        log.log(safellyGetRequestHeadersFromResponse, f'Not possible to get request headers from response. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@Function
def safellyGetArgs():
    args = None
    try:
        requestArgs = dict(request.args)
        args = { k: Serializer.getUncheckedKeyValue(k, v)
        for k, v in requestArgs.items()
    }
    except Exception as exception:
        args = {}
        log.log(safellyGetArgs, f'Not possible to get args. Returning {args} by default', exception=exception)
    return args if ObjectHelper.isNotNone(args) else dict()

@Function
def safellyGetRequestJsonFromResponse(response):
    requestBody = None
    try:
        requestBody = response.request.body
    except Exception as exception:
        requestBody = {}
        log.log(safellyGetRequestJsonFromResponse, f'Not possible to get request body from response. Returning {requestBody} by default', exception=exception)
    return requestBody if ObjectHelper.isNotNone(requestBody) else dict()

@Function
def safellyGetRequestUrlFromResponse(response):
    url = None
    try:
        url = response.url
    except Exception as exception:
        url = c.BLANK
        log.log(safellyGetRequestUrlFromResponse, f'Not possible to get request url from response. Returning {url} by default', exception=exception)
    return url if ObjectHelper.isNotNone(url) else c.BLANK

@Function
def safellyGetRequestVerbFromResponse(response):
    verb = None
    try:
        verb = response.request.method
    except Exception as exception:
        verb = UNKNOWN_VERB
        log.log(safellyGetRequestUrlFromResponse, f'Not possible to get request verb from response. Returning {verb} by default', exception=exception)
    return verb

@Function
def safellyGetResponseStatus(response):
    status = None
    try:
        status = response.status_code
    except Exception as exception:
        status = HttpStatus.INTERNAL_SERVER_ERROR
        log.log(safellyGetResponseStatus, f'Not possible to get response status. Returning {status} by default', exception=exception)
    try:
        status = HttpStatus.map(status if ObjectHelper.isNotNone(status) else HttpStatus.INTERNAL_SERVER_ERROR)
    except Exception as exception:
        status = HttpStatus.INTERNAL_SERVER_ERROR
        log.log(safellyGetResponseStatus, f'Not possible to parse response status. Returning {status} by default', exception=exception)
    return status

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
        kwargs[key] = Serializer.convertFromJsonToObject(
            {
                k: Serializer.getUncheckedKeyValue(k, v)
                for k, v in valuesAsDictionary.items()
            },
            toClass
        )
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
def retrieveApiInstance(apiInstance=None, arguments=None, service=None):
    if isApiInstance(apiInstance):
        return apiInstance
    if ObjectHelper.isNotNone(service):
        try:
            api = service.globals.api
        except:
            log.log(retrieveApiInstance, f'''Not possible to retrieve api instance by {service} service. Going for another approach''', exception=exception, muteStackTrace=True)
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
