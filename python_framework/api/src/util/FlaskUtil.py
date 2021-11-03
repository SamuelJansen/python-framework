from flask import request
from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function
import globals

def safellyGetRequestBody(self) :
    try :
        requestBody = request.get_json()
    except Exception as firstException:
        log.log(safellyGetVerb, 'Not possible to get body on first attempt. Going for a second attempt', exception=firstException)
        try :
            requestBody = request.get_data()
        except Exception as secondException:
            requestBody = {}
            log.log(safellyGetVerb, f'Not possible to get body on second attempt either. Returning {requestBody} by default', exception=secondException)
    return requestBody if ObjectHelper.isNotNone(requestBody) else dict()


def safellyGetUrl() :
    url = None
    try :
        url = request.url
    except Exception as exception :
        log.log(safellyGetVerb, 'Not possible to get url', exception=exception)
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
        log.log(safellyGetVerb, 'Not possible to get headers', exception=exception)
    return headers if ObjectHelper.isNotNone(headers) else dict()

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
    apiClassName = flask_restful.Api.__name__
    moduleName = flask_restful.__name__
    return apiClassName == getClassName(apiInstance) and apiClassName == getQualitativeName(apiInstance) and moduleName == getModuleName(apiInstance)

def validateFlaskApi(apiInstance) :
    if not isApiInstance(apiInstance) :
        raise Exception(f'Invalid "flask_restful.Api" instance. {apiInstance} is not an Api instance')

def validateResourceInstance(resourceInstance) :
    if ObjectHelper.isNone(resourceInstance) :
        raise Exception(f'Resource cannot be None')
