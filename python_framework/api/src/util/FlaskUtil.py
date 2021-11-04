from flask import Response, request
import flask_restful
from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function
import globals

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
        jsonBody = request.get_json()
    except Exception as exception:
        jsonBody = {}
        log.log(safellyGetJson, f'Not possible to get body. Returning {jsonBody} by default', exception=exception)
    return jsonBody

def safellyGetData():
    dataBody = None
    try :
        dataBody = request.get_json()
    except Exception as exception:
        dataBody = {}
        log.log(safellyGetJson, f'Not possible to get data. Returning {dataBody} by default', exception=exception)
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
        log.log(safellyGetHeaders, 'Not possible to get headers. Returning {headers} by default', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

def safellyGetArgs():
    args = None
    try:
        args = request.args
    except Exception as exception :
        args = {}
        log.log(safellyGetHeaders, f'Not possible to get args. Returning {args} by default', exception=exception)
    return args if ObjectHelper.isNotNone(args) else dict()

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
