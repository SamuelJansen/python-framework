import webbrowser
from python_helper import Constant as c
from python_helper import log, StringHelper
from flask import Response, request
import flask_restful
from python_framework.api.src.annotation.MethodWrapper import Function, overrideSignatures
from python_framework.api.src.helper import Serializer
from python_framework.api.src.service import GlobalException
from python_framework.api.src.domain import HttpStatus
from python_framework.api.src.service import Security
from python_framework.api.src.service.openapi import OpenApiManager

KW_URL = 'url'
KW_DEFAULT_URL = 'defaultUrl'
KW_MODEL = 'model'
KW_API = 'api'

KW_METHOD = 'method'

KW_RESOURCE = 'resource'

KW_CONTROLLER_RESOURCE = 'Controller'
KW_SERVICE_RESOURCE = 'Service'
KW_REPOSITORY_RESOURCE = 'Repository'
KW_VALIDATOR_RESOURCE = 'Validator'
KW_MAPPER_RESOURCE = 'Mapper'
KW_HELPER_RESOURCE = 'Helper'
KW_CONVERTER_RESOURCE = 'Converter'
KW_RESOURCE_LIST = [
    KW_CONTROLLER_RESOURCE,
    KW_SERVICE_RESOURCE,
    KW_REPOSITORY_RESOURCE,
    KW_VALIDATOR_RESOURCE,
    KW_MAPPER_RESOURCE,
    KW_HELPER_RESOURCE,
    KW_CONVERTER_RESOURCE
]

LOCALHOST_URL = 'http://127.0.0.1:5000'

DOT_SPACE_CAUSE = f'''{c.DOT_SPACE}{c.LOG_CAUSE}'''

def printMyStuff(stuff):
    print()
    print(f'    type(stuff).__name__ = {type(stuff).__name__}')
    print(f'    type(stuff).__class__.__name__ = {type(stuff).__class__.__name__}')
    print(f'    stuff.__class__.__name__ = {stuff.__class__.__name__}')
    print(f'    stuff.__class__.__module__ = {stuff.__class__.__module__}')
    print(f'    stuff.__class__.__qualname__ = {stuff.__class__.__qualname__}')

def printClass(Class) :
    print(f'{2 * c.TAB}Class.__name__ = {Class.__name__}')
    print(f'{2 * c.TAB}Class.__module__ = {Class.__module__}')
    print(f'{2 * c.TAB}Class.__qualname__ = {Class.__qualname__}')

@Function
def isPresent(object) :
    if object or isinstance(type(object), dict) or {} == object :
        return True
    return False

@Function
def jsonifyResponse(object, contentType, status) :
    return Response(Serializer.jsonifyIt(object),  mimetype = contentType, status = status)

@Function
def getClassName(instance) :
    return instance.__class__.__name__

@Function
def getModuleName(instance) :
    return instance.__class__.__module__

@Function
def getQualitativeName(instance) :
    return instance.__class__.__qualname__

@Function
def appendArgs(args, argument, isControllerMethod=False) :
    if isControllerMethod and Serializer.isList(argument) :
        return args + argument
    args.append(argument)
    return args

@Function
def getArgsWithSerializerReturnAppended(argument, args, isControllerMethod=False) :
    args = [arg for arg in args]
    args = appendArgs(args, argument, isControllerMethod=isControllerMethod)
    return tuple(arg for arg in args)

@Function
def getArgsWithResponseClassInstanceAppended(args, responseClass) :
    if responseClass :
        resourceInstance = args[0]
        objectRequest = args[1]
        serializerReturn = Serializer.convertFromObjectToObject(objectRequest, responseClass)
        args = getArgsWithSerializerReturnAppended(serializerReturn, args)
    return args

@Function
def getResourceFinalName(resourceInstance, resourceName=None) :
    if not resourceName :
        resourceName = resourceInstance.__class__.__name__
    for kwAsset in KW_RESOURCE_LIST :
        if kwAsset in resourceName :
            resourceName = resourceName.replace(kwAsset, c.NOTHING)
    return f'{resourceName[0].lower()}{resourceName[1:]}'

@Function
def getResourceType(resourceInstance, resourceName = None) :
    if not resourceName :
        resourceName = resourceInstance.__class__.__name__
    for kwAsset in KW_RESOURCE_LIST :
        if kwAsset in resourceName :
            return kwAsset

@Function
def getAttributePointerList(object) :
    return [
        getattr(object, objectAttributeName)
        for objectAttributeName in dir(object)
        if (not objectAttributeName.startswith('__') and not objectAttributeName.startswith('_'))
    ]

@Function
def setMethod(resourceInstance, newMethod, methodName = None) :
    def buildNewClassMethod(resourceInstance, newMethod) :
        def myInnerMethod(*args, **kwargs) :
            return newMethod(resourceInstance,*args, **kwargs)
        overrideSignatures(myInnerMethod, newMethod)
        return myInnerMethod
    if not type(newMethod).__name__ == KW_METHOD :
        newMethod = buildNewClassMethod(resourceInstance, newMethod)
    if not methodName :
        methodName = newMethod.__name__
    setattr(resourceInstance, methodName, newMethod)
    return resourceInstance

@Function
def getGlobals() :
    try :
        from app import globals
    except Exception as exception :
        raise Exception('Failed to get "globals" instance from app.py')
    return globals

@Function
def getApi() :
    try:
        api = getGlobals().api
    except Exception as exception :
        raise Exception(f'Failed to return api from "globals" instance. Cause: {str(exception)}')
    return api

@Function
def getNullableApi() :
    try :
        api = getApi()
    except :
        api = None
    return api

@Function
def raiseBadResponseImplementetion(cause):
    raise Exception(f'Bad response implementation. {cause}')

@Function
def validateFlaskApi(instance) :
    apiClassName = flask_restful.Api.__name__
    moduleName = flask_restful.__name__
    if not apiClassName == getClassName(instance) and apiClassName == getQualitativeName(instance) and moduleName == getModuleName(instance) :
        raise Exception(f'Globals can only be added to a "flask_restful.Api" instance. Not to {apiInstance}')

@Function
def validateResponseClass(responseClass, controllerResponse) :
    if responseClass :
        if not isPresent(controllerResponse) and not isinstance(controllerResponse, list):
            raiseBadResponseImplementetion(f'Response not present')
        if isinstance(responseClass, list) :
            if 0 == len(responseClass) :
                raiseBadResponseImplementetion(f'"responseClass" was not defined')
            elif len(responseClass) == 1 :
                if not isinstance(responseClass[0], list)  :
                    if not isinstance(controllerResponse, responseClass[0]) :
                        raiseBadResponseImplementetion(f'Response class does not match expected class. Expected "{responseClass[0].__name__}", response "{controllerResponse.__class__.__name__}"')
                elif not isinstance(responseClass[0][0], list) :
                    if not isinstance(controllerResponse, list)  :
                        raiseBadResponseImplementetion(f'Response is not a list. Expected "{responseClass[0].__class__.__name__}", but found "{controllerResponse.__class__.__name__}"')
                    elif isinstance(controllerResponse, list) and len(controllerResponse) > 0 and not isinstance(controllerResponse[0], responseClass[0][0]):
                        # print(f'responseClass = {responseClass}')
                        # print(f'responseClass[0] = {responseClass[0]}')
                        # print(f'responseClass[0][0] = {responseClass[0][0]}')
                        raiseBadResponseImplementetion(f'Response element class does not match expected element class. Expected "{responseClass[0][0].__name__}", response "{controllerResponse[0].__class__.__name__}"')
        else :
            if not isinstance(controllerResponse, responseClass) :
                raiseBadResponseImplementetion(f'Response class does not match expected class. Expected "{responseClass.__name__}", response "{controllerResponse.__class__.__name__}"')


@Function
def setResource(apiInstance, resourceInstance, resourceName=None) :
    resourceName = getResourceFinalName(resourceInstance, resourceName=resourceName)
    setattr(apiInstance,resourceName,resourceInstance)

@Function
def bindResource(apiInstance,resourceInstance) :
    validateFlaskApi(apiInstance)
    setResource(getattr(apiInstance.resource, getResourceType(resourceInstance).lower()), resourceInstance)

@Function
def getGlobalException(exception, resourceInstance, resourceInstanceMethod):
    apiInstance = getNullableApi()
    return GlobalException.handleLogErrorException(exception, resourceInstance, resourceInstanceMethod, apiInstance)

@Function
def raiseGlobalException(exception, resourceInstance, resourceInstanceMethod) :
    raise getGlobalException(exception, resourceInstance, resourceInstanceMethod)

@Function
def getCompleteResponseByException(exception, resourceInstance, resourceInstanceMethod) :
    exception = getGlobalException(exception, resourceInstance, resourceInstanceMethod)
    completeResponse = [{'message':exception.message, 'timestamp':str(exception.timeStamp)},exception.status]
    log.error(resourceInstance.__class__, f'Error processing {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__name__} request', exception)
    return completeResponse

@Function
def initialize(apiInstance, defaultUrl=None, openInBrowser=False) :
    defaultUrl = defaultUrl
    openInBrowser = openInBrowser
    url = f'{apiInstance.host}{apiInstance.baseUrl}'
    if defaultUrl :
        url = f'{url}{defaultUrl}'
    def inBetweenFunction(function,*argument,**keywordArgument) :
        log.debug(initialize,f'''{function.__name__} method''')
        if (openInBrowser) :
            log.debug(initialize,f'''Openning "{url}" url in rowser''')
            webbrowser.open_new(url)
        def innerFunction(*args,**kwargs) :
            try :
                functionReturn = function(*args,**kwargs)
            except Exception as exception :
                raise Exception(f'Failed to initialize. Cause: {str(exception)}')
            return functionReturn
        return innerFunction
    return inBetweenFunction

@Function
def Controller(
    url=c.SLASH,
    tag='Tag not defined',
    description='Controller not descripted'
) :
    controllerUrl = url
    controllerTag = tag
    controllerDescription = description
    def Wrapper(OuterClass,*args,**kwargs):
        apiInstance = getApi()
        log.debug(Controller,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass,flask_restful.Resource):
            url = controllerUrl
            tag = controllerTag
            description = controllerDescription
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self)
                flask_restful.Resource.__init__(self,*args,**kwargs)
                self.service = apiInstance.resource.service
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def getRequestBodyAsJson(contentType) :
    try :
        if OpenApiManager.DEFAULT_CONTENT_TYPE == contentType :
            requestBodyAsJson = request.get_json()
        else :
            raise Exception(f'Content type "{contentType}" not implemented')
    except Exception as exception :
        raise GlobalException.GlobalException(message='Not possible to parse the request', logMessage=str(exception), status=HttpStatus.BAD_REQUEST)
    return requestBodyAsJson

@Function
@Security.jwtRequired
def securedMethod(args, kwargs, contentType, resourceInstance, resourceInstanceMethod, requestClass, roleRequired) :
    if not Security.getRole() in roleRequired :
        raise GlobalException.GlobalException(message='Role not allowed', logMessage=f'''Role {Security.getRole()} trying to access denied resourse''', status=HttpStatus.FORBIDEN)
    return notSecuredMethod(args, kwargs, contentType, resourceInstance, resourceInstanceMethod, requestClass)

@Function
def notSecuredMethod(args, kwargs, contentType, resourceInstance, resourceInstanceMethod, requestClass) :
    if resourceInstanceMethod.__name__ in OpenApiManager.ABLE_TO_RECIEVE_BODY_LIST and requestClass :
        requestBodyAsJson = getRequestBodyAsJson(contentType)
        if resourceInstanceMethod.logBodyRequest :
            log.debug(resourceInstanceMethod, f'"bodyRequest" : {Serializer.prettyPrint(requestBodyAsJson)}')
        if  isPresent(requestBodyAsJson) :
            serializerReturn = Serializer.convertFromJsonToObject(requestBodyAsJson, requestClass)
            args = getArgsWithSerializerReturnAppended(serializerReturn, args, isControllerMethod=True)
    return resourceInstanceMethod(resourceInstance,*args[1:],**kwargs)

@Function
def ControllerMethod(
    url = c.SLASH,
    requestClass = None,
    responseClass = None,
    roleRequired = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logBodyRequest = False,
    logBodyResponse = False
):
    controllerMethodUrl = url
    controllerMethodRequestClass = requestClass
    controllerMethodResponseClass = responseClass
    controllerMethodRoleRequired = roleRequired
    controllerMethodProduces = produces
    controllerMethodConsumes = consumes
    controllerMethodLogBodyRequest = logBodyRequest
    controllerMethodLogBodyResponse = logBodyResponse
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(ControllerMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                if roleRequired and (type(list()) == type(roleRequired) and not [] == roleRequired) :
                    completeResponse = securedMethod(args, kwargs, consumes, resourceInstance, resourceInstanceMethod, requestClass, roleRequired)
                else :
                    completeResponse = notSecuredMethod(args, kwargs, consumes, resourceInstance, resourceInstanceMethod, requestClass)
                validateResponseClass(responseClass, completeResponse[0])

            except Exception as exception :
                completeResponse = getCompleteResponseByException(exception, resourceInstance, resourceInstanceMethod)
                ###- request.method:              GET
                ###- request.url:                 http://127.0.0.1:5000/alert/dingding/test?x=y
                ###- request.base_url:            http://127.0.0.1:5000/alert/dingding/test
                ###- request.url_charset:         utf-8
                ###- request.url_root:            http://127.0.0.1:5000/
                ###- str(request.url_rule):       /alert/dingding/test
                ###- request.host_url:            http://127.0.0.1:5000/
                ###- request.host:                127.0.0.1:5000
                ###- request.script_root:
                ###- request.path:                /alert/dingding/test
                ###- request.full_path:           /alert/dingding/test?x=y
                ###- request.args:                ImmutableMultiDict([('x', 'y')])
                ###- request.args.get('x'):       y

            controllerResponse = completeResponse[0]
            status = completeResponse[1]
            if logBodyResponse :
                log.debug(innerResourceInstanceMethod, f'"bodyResponse" : {Serializer.prettyPrint(controllerResponse)}')
            return jsonifyResponse(controllerResponse, produces, status)
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = controllerMethodUrl
        innerResourceInstanceMethod.requestClass = controllerMethodRequestClass
        innerResourceInstanceMethod.responseClass = controllerMethodResponseClass
        innerResourceInstanceMethod.roleRequired = controllerMethodRoleRequired
        innerResourceInstanceMethod.produces = controllerMethodProduces
        innerResourceInstanceMethod.consumes = controllerMethodConsumes
        innerResourceInstanceMethod.logBodyRequest = controllerMethodLogBodyRequest
        innerResourceInstanceMethod.logBodyResponse = controllerMethodLogBodyResponse
        return innerResourceInstanceMethod
    return innerMethodWrapper

@Function
def validateArgs(args, requestClass, method) :
    if requestClass :
        resourceInstance = args[0]
        if Serializer.isList(requestClass) :
            for index in range(len(requestClass)) :
                if Serializer.isList(args[index + 1]) and len(args[index + 1]) > 0 :
                    expecteObjectClass = requestClass[index][0]
                    for objectInstance in args[index + 1] :
                        GlobalException.validateArgs(resourceInstance, method, objectInstance, expecteObjectClass)
                else :
                    objectRequest = args[index + 1]
                    expecteObjectClass = requestClass[index]
                    GlobalException.validateArgs(resourceInstance, method, objectRequest, expecteObjectClass)
        else :
            objectRequest = args[1]
            expecteObjectClass = requestClass
            GlobalException.validateArgs(resourceInstance, method, objectRequest, expecteObjectClass)

@Function
def Service() :
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Service,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.repository = apiInstance.resource.repository
                self.validator = apiInstance.resource.validator
                self.mapper = apiInstance.resource.mapper
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ServiceMethod(requestClass=None):
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(ServiceMethod,f'''innerMethodWrapper wraped {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                validateArgs(args,requestClass,innerResourceInstanceMethod)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper

@Function
def Repository(model = None) :
    repositoryModel = model
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Repository,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            model = repositoryModel
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.repository = apiInstance.repository
                self.globals = apiInstance.globals
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def Validator() :
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Validator,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.service = apiInstance.resource.service
                self.validator = apiInstance.resource.validator
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ValidatorMethod(requestClass=None, message=None, logMessage=None) :
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(ValidatorMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                validateArgs(args,requestClass,innerResourceInstanceMethod)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper


@Function
def Mapper() :
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Mapper,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.service = apiInstance.resource.service
                self.validator = apiInstance.resource.validator
                self.mapper = apiInstance.resource.mapper
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def MapperMethod(requestClass=None, responseClass=None) :
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(MapperMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                validateArgs(args,requestClass,innerResourceInstanceMethod)
                args = getArgsWithResponseClassInstanceAppended(args, responseClass)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper

@Function
def Helper() :
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Helper,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass,flask_restful.Resource):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def HelperMethod(requestClass=None, responseClass=None) :
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(HelperMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                validateArgs(args,requestClass,innerResourceInstanceMethod)
                args = getArgsWithResponseClassInstanceAppended(args, responseClass)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper

@Function
def Converter() :
    def Wrapper(OuterClass, *args, **kwargs):
        apiInstance = getApi()
        noException = None
        log.debug(Converter,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ConverterMethod(requestClass=None, responseClass=None) :
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        noException = None
        log.debug(ConverterMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                validateArgs(args, requestClass, innerResourceInstanceMethod)
                args = getArgsWithResponseClassInstanceAppended(args, responseClass)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper
