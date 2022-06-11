import requests
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper

from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.constant import HttpClientConstant
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service.openapi import OpenApiManager


@Function
def Client(url=c.BLANK, headers=None, timeout=HttpClientConstant.DEFAULT_TIMEOUT, logRequest=False, logResponse=False) :
    clientUrl = url
    clientHeaders = StaticConverter.getValueOrDefault(headers, dict())
    clientTimeout = timeout
    clientLogRequest = logRequest
    clientLogResponse = logResponse
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Client,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            url = clientUrl
            headers = clientHeaders
            timeout = clientTimeout
            logRequest = clientLogRequest
            logResponse = clientLogResponse
            def __init__(self,*args, **kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args, **kwargs)
                self.globals = apiInstance.globals
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ClientMethod(
    url = c.BLANK,
    headers = None,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    returnOnlyBody = True,
    timeout = None,
    propagateAuthorization = False,
    propagateApiKey = False,
    propagateSession = False,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = False,
    logResponse = False
):
    clientMethodUrl = url
    clientMethodHeaders = headers
    clientMethodRequestHeaderClass = requestHeaderClass
    clientMethodRequestParamClass = requestParamClass
    clientMethodRequestClass = requestClass
    clientMethodResponseClass = responseClass
    clientMethodReturnOnlyBody = returnOnlyBody
    clientMethodTimeout = timeout
    clientMethodPropagateAuthorization = propagateAuthorization
    clientMethodPropagateApiKey = propagateApiKey
    clientMethodPropagateSession = propagateSession
    clientMethodProduces = produces
    clientMethodConsumes = consumes
    clientMethodLogRequest = logRequest
    clientMethodLogResponse = logResponse
    def innerMethodWrapper(resourceInstanceMethod,*args, **kwargs) :
        log.wrapper(ClientMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args, **kwargs):
            resourceInstance = args[0]
            completeResponse = None
            try :
                FlaskManager.validateArgs(args, requestClass, resourceInstanceMethod)
                completeResponse = resourceInstanceMethod(*args, **kwargs)
                ###- This simple client cannot handle headers or anything this much elegant
                if ObjectHelper.isTuple(completeResponse) and 0 < len(completeResponse):
                    completeResponse = completeResponse[0]
            except Exception as exception :
                log.log(innerResourceInstanceMethod, 'Failure at client method execution', exception=exception, muteStackTrace=True)
                raise exception
            return completeResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = clientMethodUrl
        innerResourceInstanceMethod.headers = clientMethodHeaders
        innerResourceInstanceMethod.requestHeaderClass = clientMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = clientMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = clientMethodRequestClass
        innerResourceInstanceMethod.responseClass = clientMethodResponseClass
        innerResourceInstanceMethod.returnOnlyBody = clientMethodReturnOnlyBody
        innerResourceInstanceMethod.timeout = clientMethodTimeout
        innerResourceInstanceMethod.propagateAuthorization = clientMethodPropagateAuthorization
        innerResourceInstanceMethod.propagateApiKey = clientMethodPropagateApiKey
        innerResourceInstanceMethod.propagateSession = clientMethodPropagateSession
        innerResourceInstanceMethod.produces = clientMethodProduces
        innerResourceInstanceMethod.consumes = clientMethodConsumes
        innerResourceInstanceMethod.logRequest = clientMethodLogRequest
        innerResourceInstanceMethod.logResponse = clientMethodLogResponse
        return innerResourceInstanceMethod
    return innerMethodWrapper
