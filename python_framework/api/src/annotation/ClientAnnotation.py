import json
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.helper import Serializer

@Function
def Client(url=c.SLASH) :
    controllerUrl = url
    def Wrapper(OuterClass, *args, **kwargs):
        log.debug(Client,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            url = controllerUrl
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
    controllerMethodUrl = url
    controllerMethodRequestHeaderClass = requestHeaderClass
    controllerMethodRequestParamClass = requestParamClass
    controllerMethodRequestClass = requestClass
    controllerMethodResponseClass = responseClass
    controllerMethodRoleRequired = roleRequired
    controllerMethodProduces = produces
    controllerMethodConsumes = consumes
    controllerMethodLogRequest = logRequest
    controllerMethodLogResponse = logResponse
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
                    logLevel = log.DEBUG
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
                log.warning(innerResourceInstanceMethod, 'Not posssible to complete request', exception=exception)
                raise exception
            controllerResponse = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : completeResponse[1].enumName}
            if logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    'bodyResponse',
                    json.loads(Serializer.jsonifyIt(controllerResponse)),
                    condition = logResponse,
                    logLevel = log.DEBUG
                )
            return completeResponse[0]
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = controllerMethodUrl
        innerResourceInstanceMethod.requestHeaderClass = controllerMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = controllerMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = controllerMethodRequestClass
        innerResourceInstanceMethod.responseClass = controllerMethodResponseClass
        innerResourceInstanceMethod.roleRequired = controllerMethodRoleRequired
        innerResourceInstanceMethod.produces = controllerMethodProduces
        innerResourceInstanceMethod.consumes = controllerMethodConsumes
        innerResourceInstanceMethod.logRequest = controllerMethodLogRequest
        innerResourceInstanceMethod.logResponse = controllerMethodLogResponse
        return innerResourceInstanceMethod
    return innerMethodWrapper
