import json
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.util import FlaskHelper

@Function
def Client(url=c.SLASH) :
    clientUrl = url
    def Wrapper(OuterClass, *args, **kwargs):
        log.debug(Client,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            url = clientUrl
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ClientMethod(
    url = c.SLASH,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    roleRequired = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = False,
    logResponse = False
):
    clientMethodUrl = url
    clientMethodRequestHeaderClass = requestHeaderClass
    clientMethodRequestParamClass = requestParamClass
    clientMethodRequestClass = requestClass
    clientMethodResponseClass = responseClass
    clientMethodRoleRequired = roleRequired
    clientMethodProduces = produces
    clientMethodConsumes = consumes
    clientMethodLogRequest = logRequest
    clientMethodLogResponse = logResponse
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        log.debug(ClientMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            completeResponse = None
            if logRequest :
                log.prettyJson(
                    resourceInstanceMethod,
                    'bodyRequest',
                    json.loads(Serializer.jsonifyIt(args[1:])),
                    condition = logRequest,
                    logLevel = log.INFO
                )
            try :
                FlaskManager.validateKwargs(
                    kwargs,
                    resourceInstance,
                    innerResourceInstanceMethod,
                    requestHeaderClass = requestHeaderClass,
                    requestParamClass = requestParamClass
                )
                FlaskManager.validateArgs(args, requestClass, innerResourceInstanceMethod)
                completeResponse = resourceInstanceMethod(*args,**kwargs)
                FlaskManager.validateResponseClass(responseClass, completeResponse)
            except Exception as exception :
                log.debug(innerResourceInstanceMethod, 'Not posssible to complete request', exception=exception)
                raise exception
            clientResponse = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : completeResponse[1].enumName}
            if logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    'bodyResponse',
                    json.loads(Serializer.jsonifyIt(clientResponse)),
                    condition = logResponse,
                    logLevel = log.INFO
                )
            return completeResponse[0]
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = clientMethodUrl
        innerResourceInstanceMethod.requestHeaderClass = clientMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = clientMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = clientMethodRequestClass
        innerResourceInstanceMethod.responseClass = clientMethodResponseClass
        innerResourceInstanceMethod.roleRequired = clientMethodRoleRequired
        innerResourceInstanceMethod.produces = clientMethodProduces
        innerResourceInstanceMethod.consumes = clientMethodConsumes
        innerResourceInstanceMethod.logRequest = clientMethodLogRequest
        innerResourceInstanceMethod.logResponse = clientMethodLogResponse
        return innerResourceInstanceMethod
    return innerMethodWrapper
