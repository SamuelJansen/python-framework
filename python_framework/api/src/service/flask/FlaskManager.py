import globals
import json

from python_helper import Constant as c
from python_helper import log, Function, ReflectionHelper, ObjectHelper, SettingHelper, EnvironmentHelper, StringHelper

from python_framework.api.src.annotation.EnumAnnotation import EnumItem
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException
from python_framework.api.src.constant import ConfigurationKeyConstant, JwtConstant
from python_framework.api.src.domain import HttpDomain
from python_framework.api.src.constant import StaticConstant
from python_framework.api.src.constant import LogConstant
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service import WebBrowser
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.service import ExceptionHandler
from python_framework.api.src.service import SqlAlchemyProxy
from python_framework.api.src.service import SchedulerManager
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service.openapi import OpenApiManager


KW_URL = 'url'
KW_DEFAULT_URL = 'defaultUrl'
KW_MODEL = 'model'
KW_API = 'api'
KW_APP = 'app'

KW_METHOD = 'method'

KW_RESOURCE = 'resource'
KW_STATIC_RESOURCE_PREFIX = 'Static'

PYTHON_FRAMEWORK_MODULE_NAME = 'python_framework'
KW_MANAGER = 'Manager'

PYTHON_FRAMEWORK_INTERNAL_MODULE_NAME_LIST = [
    PYTHON_FRAMEWORK_MODULE_NAME,
    'TestApi',
    'DevTestApi',
    'PrdTestApi',
    'LocalTestApi',
    'SecurityManagerTestApi',
    'ApiKeyManagerTestApi',
    'SessionManagerTestApi',
    'SecurityManagerAndApiKeyManagerAndSessionManagerTestApi',
    'ClientTestApi'
]
KW_CONTROLLER_RESOURCE = 'Controller'
KW_SCHEDULER_RESOURCE = 'Scheduler'
KW_SERVICE_RESOURCE = 'Service'
KW_CLIENT_RESOURCE = 'Client'
KW_LISTENER_RESOURCE = 'Listener'
KW_EMITTER_RESOURCE = 'Emitter'
KW_REPOSITORY_RESOURCE = 'Repository'
KW_VALIDATOR_RESOURCE = 'Validator'
KW_MAPPER_RESOURCE = 'Mapper'
KW_HELPER_RESOURCE = 'Helper'
KW_CONVERTER_RESOURCE = 'Converter'
PYTHON_FRAMEWORK_RESOURCE_NAME_DICTIONARY = {
    KW_CONTROLLER_RESOURCE : [
        'ActuatorHealthController',
        'DocumentationController'
    ],
    KW_SCHEDULER_RESOURCE : [],
    KW_SERVICE_RESOURCE : [
        'ActuatorHealthService',
        'DocumentationService'
    ],
    KW_CLIENT_RESOURCE : [],
    KW_LISTENER_RESOURCE : [],
    KW_EMITTER_RESOURCE : [],
    KW_REPOSITORY_RESOURCE : [
        'ActuatorHealthRepository',
        'DocumentationRepository'
    ],
    KW_VALIDATOR_RESOURCE : [],
    KW_MAPPER_RESOURCE : [],
    KW_HELPER_RESOURCE : [],
    KW_CONVERTER_RESOURCE : [
        'ActuatorHealthConverter'
    ]
}
KW_RESOURCE_LIST = list(PYTHON_FRAMEWORK_RESOURCE_NAME_DICTIONARY.keys())


def raiseBadResponseImplementation(cause):
    raise Exception(f'Bad response implementation. {cause}')


def newApp(
    filePath
    , successStatus = True
    , errorStatus = True
    , failureStatus = True
    , warningStatus = True
    , settingStatus = True
    , statusStatus = True
    , infoStatus = True
    , debugStatus = False
    , wrapperStatus = False
    , testStatus = False
    , logStatus = False
):
    globalsInstance = globals.newGlobalsInstance(
        filePath
        , successStatus = successStatus
        , errorStatus = errorStatus
        , failureStatus = failureStatus
        , settingStatus = settingStatus
        , statusStatus = statusStatus
        , infoStatus = infoStatus
        , debugStatus = debugStatus
        , warningStatus = warningStatus
        , wrapperStatus = wrapperStatus
        , testStatus = testStatus
        , logStatus = logStatus
    )
    try:
        app = globals.importResource(
            KW_APP,
            resourceModuleName = StaticConverter.getValueOrDefault(
                globalsInstance.apiName,
                StringHelper.join(EnvironmentHelper.listDirectoryContent(f'{globalsInstance.BASE_API_PATH}')[0].split(c.DOT)[:-1],character = c.DOT)
            ),
            required = True
        )
    except Exception as exception:
        apiPath = f'{c.DOT}{EnvironmentHelper.OS_SEPARATOR}{globalsInstance.BASE_API_PATH}{globalsInstance.apiName}.py'
        errorMessage = f"Not possible to load app. Make shure it's name is properlly configured at '{globalsInstance.settingFilePath}' and it's instance is named 'app' at '{apiPath}'"
        log.error(newApp, errorMessage, exception)
        raise exception
    if ObjectHelper.isNone(app):
        app = globals.importResource(KW_APP, resourceModuleName=globalsInstance.apiName)
        raise Exception('Not possible to load app. Check logs for more details')
    return app


@Function
def initialize(
    apiInstance
    , defaultUrl = None
    , openInBrowser = False
):
    innerDefaultUrl = getInternalUrl(apiInstance)
    if defaultUrl :
        innerDefaultUrl = f'{innerDefaultUrl}{defaultUrl}'
    def inBetweenFunction(function,*argument,**keywordArgument):
        log.wrapper(initialize, f'''{function.__name__} method''')
        if (openInBrowser):
            log.debug(initialize, f'''Openning "{innerDefaultUrl}" url in rowser''')
            # WebBrowser.openUrlInChrome(innerDefaultUrl)
            WebBrowser.openUrl(innerDefaultUrl)
        def innerFunction(*args,**kwargs):
            try :
                functionReturn = function(*args,**kwargs)
            except Exception as exception :
                raise Exception(f'Failed to initialize. Cause: {str(exception)}')
            return functionReturn
        return innerFunction
    return inBetweenFunction


def runApi(*args, api=None, debug=False, **kwargs):
    if ObjectHelper.isNone(api):
        api = FlaskUtil.getApi()
    muteLogs(api, debug)
    if 'host' not in kwargs and api.host :
        kwargs['host'] = api.host if not 'localhost' == api.host else '0.0.0.0'
    if 'port' not in kwargs and api.port :
        kwargs['port'] = api.port
    log.status(runApi, f'{api.globals.apiName} api will run at {api.internalUrl}')
    log.status(runApi, f'Health check will be available at {api.healthCheckUrl}')
    log.status(runApi, f'Documentation will be available at {api.documentationUrl}')
    log.status(runApi, f'Api static content will be available at {api.exposedStaticUrl}')
    for manager in api.managerList:
        manager.onRun(api, api.app)
    log.success(runApi, f'{api.globals.apiName} api will be available at {api.exposedUrl}')
    try:
        api.app.run(*args, debug=debug, **kwargs)
    except Exception as exception:
        log.debug(runApi, 'Error while running api. Initiating shutdown', exception=exception, muteStackTrace=True)
    log.success(runApi, f'{api.globals.apiName} api is successfully shuting down')
    for manager in api.managerList[::-1]:
        manager.onShutdown(api, api.app)
    # SessionManager.onShutdown(api, api.app)
    # ApiKeyManager.onShutdown(api, api.app)
    # SecurityManager.onShutdown(api, api.app)
    # SchedulerManager.onShutdown(api, api.app)
    SqlAlchemyProxy.onShutdown(api, api.app)


@Function
def getInternalUrl(apiInstance):
    apiUrl = None
    try :
        apiUrl = f'{apiInstance.scheme}://{apiInstance.host}{c.BLANK if ObjectHelper.isEmpty(apiInstance.port) else f"{c.COLON}{apiInstance.port}"}{apiInstance.baseUrl}'
    except Exception as exception :
        log.error(getInternalUrl, 'Not possible to parse api url', exception)
    return apiUrl


@Function
def muteLogs(apiInstance, debug):
    if not debug:
        import logging
        from werkzeug.serving import WSGIRequestHandler
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.disabled = True
        apiInstance.app.logger.disabled = True
        apschedulerLoggerEnabled = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_ENABLE)
        apscheduler_logger = logging.getLogger('apscheduler.scheduler')
        default_apscheduler_logger = logging.getLogger('apscheduler.executors.default')
        apscheduler_logger.disabled = True if ObjectHelper.isNone(apschedulerLoggerEnabled) else not apschedulerLoggerEnabled
        apscheduler_logger.propagate = not apscheduler_logger.disabled
        default_apscheduler_logger.disabled = apscheduler_logger.disabled
        default_apscheduler_logger.propagate = not apscheduler_logger.disabled
        WSGIRequestHandler.log = lambda self, type, message, *args: None ###- getattr(werkzeug_logger, type)('%s %s' % (self.address_string(), message % args))


@Function
def getRequestBodyAsJson(contentType, requestClass):
    try :
        if OpenApiManager.DEFAULT_CONTENT_TYPE == contentType :
            requestBodyAsJson = FlaskUtil.safellyGetJson()
        elif OpenApiManager.MULTIPART_X_MIXED_REPLACE in contentType :
            requestBodyAsJson = FlaskUtil.safellyGetData()
        else :
            raise Exception(f'Content type "{contentType}" not implemented')
    except Exception as exception :
        raise GlobalException(message='Not possible to parse the request', logMessage=str(exception), status=HttpStatus.BAD_REQUEST)
    validateBodyAsJson(requestBodyAsJson, requestClass)
    return requestBodyAsJson

@Function
def validateBodyAsJson(requestBodyAsJson, requestClass):
    if ObjectHelper.isNotNone(requestClass):
        requestBodyAsJsonIsList = ObjectHelper.isList(requestBodyAsJson)
        requestClassIsList = ObjectHelper.isList(requestClass) and ObjectHelper.isList(requestClass[0])
        if not ((requestBodyAsJsonIsList and requestClassIsList) or (not requestBodyAsJsonIsList and not requestClassIsList)):
            raise GlobalException(message='Bad request', logMessage='Bad request', status=HttpStatus.BAD_REQUEST)

def handleAnyControllerMethodRequest(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    contextRequired,
    apiKeyRequired,
    roleRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest,
    muteStacktraceOnBusinessRuleException,
    verb = None,
    requestHeaders = None,
    requestParams = None,
    requestBody = None,
    logRequestMessage = LogConstant.CONTROLLER_REQUEST
):
    if ObjectHelper.isNotEmptyCollection(roleRequired):
        return handleSecuredControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            apiKeyRequired,
            roleRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    elif ObjectHelper.isNotEmptyCollection(apiKeyRequired):
        return handleByApiKeyControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            apiKeyRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    elif ObjectHelper.isNotEmptyCollection(contextRequired):
        return handleSessionedControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    return handleControllerMethod(
        args,
        kwargs,
        contentType,
        resourceInstance,
        resourceInstanceMethod,
        requestHeaderClass,
        requestParamClass,
        requestClass,
        logRequest,
        muteStacktraceOnBusinessRuleException,
        verb = verb,
        requestHeaders = requestHeaders,
        requestParams = requestParams,
        requestBody = requestBody,
        logRequestMessage = logRequestMessage
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
@SecurityManager.jwtAccessRequired
def handleSecuredControllerMethod(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    contextRequired,
    apiKeyRequired,
    roleRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest,
    muteStacktraceOnBusinessRuleException,
    verb = None,
    requestHeaders = None,
    requestParams = None,
    requestBody = None,
    logRequestMessage = LogConstant.CONTROLLER_REQUEST
):
    contextList = SecurityManager.getContext()
    if not any(role in set(contextList) for role in roleRequired):
        raise GlobalException(
            message = 'Role not allowed',
            logMessage = f'''Roles {contextList} trying to access denied resource. Allowed roles {roleRequired}''',
            status = HttpStatus.FORBIDDEN
        )
    elif ObjectHelper.isNotEmptyCollection(apiKeyRequired):
        return handleByApiKeyControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            apiKeyRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    elif ObjectHelper.isNotEmptyCollection(contextRequired):
        return handleSessionedControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    return handleControllerMethod(
        args,
        kwargs,
        contentType,
        resourceInstance,
        resourceInstanceMethod,
        requestHeaderClass,
        requestParamClass,
        requestClass,
        logRequest,
        muteStacktraceOnBusinessRuleException,
        verb = verb,
        requestHeaders = requestHeaders,
        requestParams = requestParams,
        requestBody = requestBody,
        logRequestMessage = logRequestMessage
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
@ApiKeyManager.jwtAccessRequired
def handleByApiKeyControllerMethod(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    contextRequired,
    apiKeyRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest,
    muteStacktraceOnBusinessRuleException,
    verb = None,
    requestHeaders = None,
    requestParams = None,
    requestBody = None,
    logRequestMessage = LogConstant.CONTROLLER_REQUEST
):
    contextList = ApiKeyManager.getContext(requestHeaders=requestHeaders)
    if not any(apiKey in set(contextList) for apiKey in apiKeyRequired):
        raise GlobalException(
            message = 'ApiKey not allowed',
            logMessage = f'''ApiKey {contextList} trying to access denied resource. Allowed apiKeys {apiKeyRequired}''',
            status = HttpStatus.FORBIDDEN
        )
    elif ObjectHelper.isNotEmptyCollection(contextRequired):
        return handleSessionedControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            contextRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
    return handleControllerMethod(
        args,
        kwargs,
        contentType,
        resourceInstance,
        resourceInstanceMethod,
        requestHeaderClass,
        requestParamClass,
        requestClass,
        logRequest,
        muteStacktraceOnBusinessRuleException,
        verb = verb,
        requestHeaders = requestHeaders,
        requestParams = requestParams,
        requestBody = requestBody,
        logRequestMessage = logRequestMessage
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
@SessionManager.jwtAccessRequired
def handleSessionedControllerMethod(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    contextRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest,
    muteStacktraceOnBusinessRuleException,
    verb = None,
    requestHeaders = None,
    requestParams = None,
    requestBody = None,
    logRequestMessage = LogConstant.CONTROLLER_REQUEST
):
    contextList = SessionManager.getContext(requestHeaders=requestHeaders)
    if not any(context in set(contextList) for context in contextRequired):
        raise GlobalException(
            message = 'Session not allowed',
            logMessage = f'''Sessions {contextList} trying to access denied resource. Allowed contexts: {contextRequired}''',
            status = HttpStatus.FORBIDDEN
        )
    else:
        return handleControllerMethod(
            args,
            kwargs,
            contentType,
            resourceInstance,
            resourceInstanceMethod,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            logRequest,
            muteStacktraceOnBusinessRuleException,
            verb = verb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )


def isAbleToHaveRequestBody(resourceInstanceMethod, requestClass, verb):
    return ObjectHelper.isNotNone(requestClass) and (
        resourceInstanceMethod.__name__ in OpenApiManager.ABLE_TO_RECIEVE_BODY_LIST or
        str(verb).lower() in OpenApiManager.ABLE_TO_RECIEVE_BODY_LIST
    )


@EncapsulateItWithGlobalException()
def handleControllerMethod(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest,
    muteStacktraceOnBusinessRuleException,
    verb = None,
    requestHeaders = None,
    requestParams = None,
    requestBody = None,
    logRequestMessage = LogConstant.CONTROLLER_REQUEST
):
    requestBodyAsJson = {}
    if isAbleToHaveRequestBody(resourceInstanceMethod, requestClass, verb):
        if ObjectHelper.isNotNone(requestBody):
            requestBodyAsJson = requestBody
        else:
            requestBodyAsJson = getRequestBodyAsJson(contentType, requestClass)
        if Serializer.requestBodyIsPresent(requestBodyAsJson):
            requestBodyAsJsonSerialized = Serializer.convertFromJsonToObject(requestBodyAsJson, requestClass)
            args = getArgsWithSerializerReturnAppended(args, requestBodyAsJsonSerialized)
    if ObjectHelper.isNotNone(requestBody):
        requestHeadersAsJson = requestHeaders
    else:
        requestHeadersAsJson = FlaskUtil.safellyGetHeaders()
    if ObjectHelper.isNotNone(requestBody):
        requestParamAsJson = requestParams
    else:
        requestParamAsJson = FlaskUtil.safellyGetArgs()
    headers = FlaskUtil.addToKwargs(FlaskUtil.KW_HEADERS, requestHeaderClass, requestHeadersAsJson, kwargs)
    query = FlaskUtil.addToKwargs(FlaskUtil.KW_PARAMETERS, requestParamClass, requestParamAsJson, kwargs)
    try:
        if resourceInstance.logRequest and logRequest :
            log.prettyJson(
                resourceInstanceMethod,
                logRequestMessage,
                {
                    'headers': headers,
                    'query': query, ###- FlaskUtil.addToKwargs(FlaskUtil.KW_PARAMETERS, requestParamClass, FlaskUtil.safellyGetArgs(), kwargs), ###- safellyGetUrl() returns query param
                    'body': requestBodyAsJson
                },
                condition = True,
                logLevel = log.INFO
            )
    except Exception as exception:
        log.failure(handleControllerMethod, 'Not possible to log request properly', exception)
    return validateAndReturnResponse(handleAdditionalResponseHeadersIfNeeded(resourceInstanceMethod(resourceInstance,*args[1:],**kwargs)))

@Function
def getArgsWithSerializerReturnAppended(args, argument):
    args = [arg for arg in args]
    args.append(argument)
    # return [arg for arg in args]
    return args

@Function
def getArgumentInFrontOfArgs(args, argument):
    return [argument, *args]

@Function
def getArgsWithResponseClassInstanceAppended(args, responseClass):
    if responseClass :
        resourceInstance = args[0]
        objectRequest = args[1]
        objectRequestSerialized = Serializer.convertFromObjectToObject(objectRequest, responseClass)
        return getArgsWithSerializerReturnAppended(args, objectRequestSerialized)
    return args

@Function
def getResourceFinalName(resourceInstance, resourceName=None):
    if not resourceName :
        resourceName = resourceInstance.__class__.__name__
    for resourceType in KW_RESOURCE_LIST :
        if resourceName.endswith(resourceType):
            resourceName = resourceName[:-len(resourceType)]
            break
    return f'{resourceName[0].lower()}{resourceName[1:]}'

@Function
def getResourceType(resourceInstance, resourceName = None):
    if not resourceName :
        resourceName = resourceInstance.__class__.__name__
    for resourceType in KW_RESOURCE_LIST :
        if resourceName.endswith(resourceType):
            return resourceType

@Function
def setResource(apiInstance, resourceInstance, resourceName=None):
    resourceName = getResourceFinalName(resourceInstance, resourceName=resourceName)
    ReflectionHelper.setAttributeOrMethod(apiInstance,resourceName,resourceInstance)

@Function
def bindResource(apiInstance,resourceInstance):
    FlaskUtil.validateFlaskApi(apiInstance)
    FlaskUtil.validateResourceInstance(resourceInstance)
    setResource(ReflectionHelper.getAttributeOrMethod(apiInstance.resource, getResourceType(resourceInstance).lower()), resourceInstance)

@Function
def validateArgs(args, requestClass, resourceInstanceMethod):

    ###- import inspect
    
    ###- def enforce_type_annotation(fn):
    ###-     parameters = inspect.signature(fn).parameters
    ###-     param_keys = list(parameters.keys())
    ###-     def wrapper(*args, **kwargs):
    ###-         errors = list()
    ###-         # -- iterate over positionals
    ###-         for i in range(len(args)):
    ###-             param = parameters[param_keys[i]]
    ###-             value = args[i]
    ###-             # -- if the parameter is not annotated, don't validate.
    ###-             if not param.annotation:
    ###-                 continue
    ###-             if not isinstance(value, param.annotation):
    ###-                 errors.append(
    ###-                     f'Positional argument {param} was given type {type(value)} but expected {param.annotation}!'
    ###-                 )
    ###-         # -- this might throw a KeyError if an incorrect argument is provided
    ###-         for key, value in kwargs.items():
    ###-             param = parameters[key]
    ###-             value = kwargs[key]
    ###-             # -- if the parameter is not annotated, don't validate.
    ###-             if not param.annotation:
    ###-                 continue
    ###-             if not isinstance(value, param.annotation):
    ###-                 errors.append(
    ###-                     f'Keyword argument {param} was given type {type(value)} but expected {param.annotation}!'
    ###-                 )
    ###-         if len(errors):
    ###-             raise TypeError('\n'.join(errors))
    ###-         return fn(*args, **kwargs)
    ###-     return wrapper
    
    ###- @enforce_type_annotation
    ###- def foo(bar: bool, barry: str = None):
    ###-     return "hello world"
    
    ###- # -- works - keyword arguments remain optional
    ###- print(foo(True))
    ###- # -- works - all types were passed correctly
    ###- print(foo(True, 'Hello'))
    ###- # -- does not work, keyword arguments may also be passed as positional
    ###- print(foo(True, 1))
    ###- # -- does not work, "barry" expects a string
    ###- print(foo(True, barry=1))

    if ObjectHelper.isNotNone(requestClass):
        if Serializer.isSerializerList(requestClass):
            if 0 < len(requestClass):
                resourceInstance = args[0]
                for index in range(len(requestClass)):
                    objectRequest = args[index + 1]
                    expecteObjectClass = requestClass[index]
                    ExceptionHandler.validateArgs(resourceInstance, resourceInstanceMethod, objectRequest, expecteObjectClass)
                    if Serializer.isSerializerList(args[index + 1]) and len(args[index + 1]) > 0:
                        expecteObjectClass = requestClass[index][0]
                        for objectRequest in args[index + 1]:
                            ExceptionHandler.validateArgs(resourceInstance, resourceInstanceMethod, objectRequest, expecteObjectClass)
        else:
            validateArgs(args, [requestClass], resourceInstanceMethod)

def validateKwargs(kwargs, resourceInstance, resourceInstanceMethod, requestHeaderClass, requestParamClass):
    classListToValidate = []
    instanceListToValidate = []
    if ObjectHelper.isNotEmpty(requestHeaderClass):
        classListToValidate.append(requestHeaderClass if ObjectHelper.isNotList(requestHeaderClass) else requestHeaderClass[0])
        instanceListToValidate.append(kwargs.get(FlaskUtil.KW_HEADERS, {}))
    if ObjectHelper.isNotEmpty(requestParamClass):
        classListToValidate.append(requestParamClass if ObjectHelper.isNotList(requestParamClass) else requestParamClass[0])
        instanceListToValidate.append(kwargs.get(FlaskUtil.KW_PARAMETERS, {}))
    validateArgs([resourceInstance, *instanceListToValidate], classListToValidate, resourceInstanceMethod)

@Function
def Controller(
    url = c.SLASH,
    responseHeaders = None,
    tag = 'Tag not defined',
    description = 'Controller not descripted',
    logRequest = False,
    logResponse = False
):
    controllerUrl = url
    controllerTag = tag
    controllerDescription = description
    controllerResponseHeaders = responseHeaders
    controllerLogRequest = logRequest
    controllerLogResponse = logResponse
    def Wrapper(OuterClass,*args,**kwargs):
        log.wrapper(Controller, f'''wrapping {OuterClass.__name__}''', None)
        class InnerClass(OuterClass, FlaskUtil.Resource):
            url = controllerUrl
            responseHeaders = controllerResponseHeaders
            tag = controllerTag
            description = controllerDescription
            logRequest = controllerLogRequest
            logResponse = controllerLogResponse
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass, f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})', None)
                apiInstance = FlaskUtil.getApi()
                OuterClass.__init__(self)
                FlaskUtil.Resource.__init__(self,*args,**kwargs)
                self.service = apiInstance.resource.service
                self.globals = apiInstance.globals
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ControllerMethod(
    url = c.SLASH,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    responseHeaders = None,
    roleRequired = None,
    apiKeyRequired = None,
    contextRequired = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = True,
    logResponse = True,
    muteStacktraceOnBusinessRuleException = True
):
    controllerMethodUrl = url
    controllerMethodRequestHeaderClass = requestHeaderClass
    controllerMethodRequestParamClass = requestParamClass
    controllerMethodRequestClass = requestClass
    controllerMethodResponseClass = responseClass
    controllerMethodResponseHeaders = responseHeaders
    controllerMethodRoleRequired = roleRequired
    controllerMethodApiKeyRequired = apiKeyRequired
    controllerMethodSessionRequired = contextRequired
    controllerMethodProduces = produces
    controllerMethodConsumes = consumes
    controllerMethodLogRequest = logRequest
    controllerMethodLogResponse = logResponse
    controllerMethodMuteStacktraceOnBusinessRuleException = muteStacktraceOnBusinessRuleException
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs):
        log.wrapper(ControllerMethod, f'''wrapping {resourceInstanceMethod.__name__}''', None)
        def innerResourceInstanceMethod(*args,**kwargs):
            f'''(*args, {FlaskUtil.KW_HEADERS}={{}}, {FlaskUtil.KW_PARAMETERS}={{}}, **kwargs)'''
            # r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            # r.headers["Pragma"] = "no-cache"
            # r.headers["Expires"] = "0"
            # r.headers['Cache-Control'] = 'public, max-age=0'
            resourceInstance = args[0]
            completeResponse = None
            log.info(resourceInstanceMethod, f'{LogConstant.CONTROLLER_SPACE}{FlaskUtil.safellyGetVerb()}{c.SPACE_DASH_SPACE}{FlaskUtil.safellyGetUrl()}')
            try :
                completeResponse = handleAnyControllerMethodRequest(
                    args,
                    kwargs,
                    consumes,
                    resourceInstance,
                    resourceInstanceMethod,
                    contextRequired,
                    apiKeyRequired,
                    roleRequired,
                    requestHeaderClass,
                    requestParamClass,
                    requestClass,
                    logRequest,
                    muteStacktraceOnBusinessRuleException
                )
                validateCompleteResponse(responseClass, completeResponse)
            except Exception as exception :
                log.log(innerResourceInstanceMethod, 'Failure at controller method execution. Getting complete response as exception', exception=exception, muteStackTrace=True)
                completeResponse = getCompleteResponseByException(
                    exception,
                    resourceInstance,
                    resourceInstanceMethod,
                    muteStacktraceOnBusinessRuleException
                )
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
            try:
                status = HttpStatus.map(completeResponse[-1])
                additionalResponseHeaders = completeResponse[1]
                if ObjectHelper.isNotNone(resourceInstance.responseHeaders):
                    additionalResponseHeaders = {**resourceInstance.responseHeaders, **additionalResponseHeaders}
                if ObjectHelper.isNotNone(responseHeaders):
                    additionalResponseHeaders = {**responseHeaders, **additionalResponseHeaders}
                responseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : status.enumName}
                httpResponse = FlaskUtil.buildHttpResponse(additionalResponseHeaders, responseBody, status.enumValue, produces)
            except Exception as exception:
                log.failure(innerResourceInstanceMethod, f'Failure while parsing complete response: {completeResponse}. Returning simplified version of it', exception, muteStackTrace=True)
                completeResponse = getCompleteResponseByException(
                    Exception('Not possible to handle complete response'),
                    resourceInstance,
                    resourceInstanceMethod,
                    muteStacktraceOnBusinessRuleException
                )
                httpResponse = FlaskUtil.buildHttpResponse(completeResponse[1], completeResponse[0], completeResponse[-1].enumValue, produces)

            try:
                if resourceInstance.logResponse and logResponse :
                    log.prettyJson(
                        resourceInstanceMethod,
                        LogConstant.CONTROLLER_RESPONSE,
                        {
                            'headers': FlaskUtil.safellyGetResponseHeaders(httpResponse),
                            'body': FlaskUtil.safellyGetFlaskResponseJson(httpResponse), ###- json.loads(Serializer.jsonifyIt(responseBody))
                            'status': status
                        },
                        condition = True,
                        logLevel = log.INFO
                    )
            except Exception as exception:
                log.failure(innerResourceInstanceMethod, 'Not possible to log response properly', exception)

            return httpResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = controllerMethodUrl
        innerResourceInstanceMethod.requestHeaderClass = controllerMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = controllerMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = controllerMethodRequestClass
        innerResourceInstanceMethod.responseClass = controllerMethodResponseClass
        innerResourceInstanceMethod.responseHeaders = controllerMethodResponseHeaders
        innerResourceInstanceMethod.roleRequired = controllerMethodRoleRequired
        innerResourceInstanceMethod.apiKeyRequired = controllerMethodApiKeyRequired
        innerResourceInstanceMethod.contextRequired = controllerMethodSessionRequired
        innerResourceInstanceMethod.produces = controllerMethodProduces
        innerResourceInstanceMethod.consumes = controllerMethodConsumes
        innerResourceInstanceMethod.logRequest = controllerMethodLogRequest
        innerResourceInstanceMethod.logResponse = controllerMethodLogResponse
        innerResourceInstanceMethod.muteStacktraceOnBusinessRuleException = controllerMethodMuteStacktraceOnBusinessRuleException
        return innerResourceInstanceMethod
    return innerMethodWrapper


def getAndHandleGlobalException(
    exception,
    resourceInstance,
    resourceInstanceMethod,
    apiInstance = None,
    context = HttpDomain.CONTROLLER_CONTEXT
):
    return ExceptionHandler.handleLogErrorException(
        exception,
        resourceInstance,
        resourceInstanceMethod,
        context,
        apiInstance = apiInstance if ObjectHelper.isNotNone(apiInstance) else FlaskUtil.getNullableApi()
    )


def raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=HttpDomain.CONTROLLER_CONTEXT):
    raise getAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=context)

###- reprecated
getAndPersistGlobalException = getAndHandleGlobalException
###- reprecated
raiseAndPersistGlobalException = raiseAndHandleGlobalException

def getCompleteResponseByException(
    exception,
    resourceInstance,
    resourceInstanceMethod,
    muteStacktraceOnBusinessRuleException,
    context = HttpDomain.CONTROLLER_CONTEXT
):
    try:
        exception = getAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=context)
        completeResponse = (ExceptionHandler.getDefaultBodyException(exception=exception), {}, exception.status)
        try :
            logErrorMessage = f'Error processing {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__name__} {context.lower()} request'
            if HttpStatus.INTERNAL_SERVER_ERROR <= HttpStatus.map(exception.status):
                log.error(resourceInstance.__class__, logErrorMessage, exception)
            else :
                log.failure(resourceInstance.__class__, logErrorMessage, exception=exception, muteStackTrace=muteStacktraceOnBusinessRuleException)
        except Exception as logErrorMessageException :
            log.debug(getCompleteResponseByException, f'Error logging exception at {context.lower()}', exception=logErrorMessageException, muteStackTrace=True)
            log.error(getCompleteResponseByException, f'Error processing {context.lower()} request', exception)
        return validateAndReturnResponse(handleAdditionalResponseHeadersIfNeeded(completeResponse))
    except Exception as unexpectedException:
        log.debug(getCompleteResponseByException, f'Error while building exception {context.lower()} return', exception=unexpectedException, muteStackTrace=True)
        log.error(getCompleteResponseByException, f'Error processing {context.lower()} request', exception)
        return validateAndReturnResponse((ExceptionHandler.getDefaultBodyException(), {}, ExceptionHandler.DEFAULT_STATUS))

def validateAndReturnResponse(completeResponse):
    if (
        ObjectHelper.isNotTuple(completeResponse) or not 3 == len(completeResponse)
    ) or (
        ObjectHelper.isNotDictionary(completeResponse[1])
    ) or (
        not isinstance(HttpStatus.map(completeResponse[-1]), EnumItem)
    ):
        log.debug(validateAndReturnResponse, f'Invalid completeResponse: {completeResponse}')
        raise Exception('Invalid complete response')
    return completeResponse

def handleAdditionalResponseHeadersIfNeeded(completeResponse):
    # log.log(handleAdditionalResponseHeadersIfNeeded, f'Complete response: {completeResponse}')
    if ObjectHelper.isTuple(completeResponse):
        if 3 == len(completeResponse):
            if ObjectHelper.isTuple(completeResponse[0]):
                ###- ((serviceResponse, serviceHeader), controllerHeader, status)
                return completeResponse[0][0], {**completeResponse[1][0], **completeResponse[0][1]}, completeResponse[1][1]
            return completeResponse
        elif 2 == len(completeResponse):
            if ObjectHelper.isTuple(completeResponse[0]) and 2 == len(completeResponse[0]):
                ###- ((serviceResponse, serviceHeader), status)
                return completeResponse[0][0], completeResponse[0][1], completeResponse[1]
            elif ObjectHelper.isTuple(completeResponse[1]) and 2 == len(completeResponse[1]):
                ###- (serviceResponse, (serviceHeader, status)) --> this case should never happens
                return completeResponse[0], completeResponse[1][0], completeResponse[1][1]
            else:
                ###- (serviceResponse, status) --> missing header
                return completeResponse[0], dict(), completeResponse[1]
    elif ObjectHelper.isList(completeResponse) and 2 == len(completeResponse):
        ###- it can only be guessed at this point
        ###- (serviceResponse, status) --> missing header
        return completeResponse[0], dict(), completeResponse[1]
    ###- totally lost at this point
    return completeResponse


def validateCompleteResponse(responseClass, completeResponse):
    if isNotPythonFrameworkHttpsResponseBody(completeResponse):
        raiseBadResponseImplementation(f'It should be a tuple like this: ({"RESPONSE_CLASS" if ObjectHelper.isNone(responseClass) else responseClass if ObjectHelper.isNotList(responseClass) else responseClass[0]}, HEADERS, HTTPS_CODE). But it is: {completeResponse}')
    if ObjectHelper.isNotNone(responseClass):
        if Serializer.isSerializerList(responseClass):
            if 0 == len(responseClass):
                log.log(validateCompleteResponse, f'"responseClass" was not defined')
            elif 1 == len(responseClass):
                if ObjectHelper.isNotList(responseClass[0])  :
                    if not isinstance(completeResponse[0], responseClass[0]):
                        raiseBadResponseImplementation(f'Response does not match expected class. Expected "{responseClass[0].__name__}", but got "{completeResponse[0].__class__.__name__}"')
                elif ObjectHelper.isNotList(responseClass[0][0]):
                    if ObjectHelper.isNotList(completeResponse[0]):
                        raiseBadResponseImplementation(f'Response is not a list. Expected "{responseClass[0].__class__.__name__}", but found "{completeResponse[0].__class__.__name__}"')
                    elif Serializer.isSerializerList(completeResponse[0]) and 0 < len(completeResponse[0]) and not isinstance(completeResponse[0][0], responseClass[0][0]):
                        raiseBadResponseImplementation(f'Response element class does not match expected element class. Expected "{responseClass[0][0].__name__}", response "{completeResponse[0][0].__class__.__name__}"')
        else :
            if not isinstance(completeResponse[0], responseClass):
                raiseBadResponseImplementation(f'Response does not match expected class. Expected "{responseClass.__name__}", but got "{completeResponse[0].__class__.__name__}"')
    else :
        log.log(validateCompleteResponse, f'"responseClass" was not defined')


def isPythonFrameworkHttpsResponseBody(completeResponse):
    return (
        ObjectHelper.isTuple(completeResponse)
    ) and (
        3 == len(completeResponse)
    ) and (
        isinstance(completeResponse[1], dict)
    ) and (
        isinstance(completeResponse[-1], EnumItem) or isinstance(completeResponse[-1], int)
    )


def isNotPythonFrameworkHttpsResponseBody(completeResponse):
    return not isPythonFrameworkHttpsResponseBody(completeResponse)


def getResourceSelf(apiInstance, resourceType, resourceInstanceName):
    return ReflectionHelper.getAttributeOrMethodByNamePath(
        apiInstance,
        StringHelper.join(
            [
                KW_RESOURCE.lower(),
                resourceType.lower(),
                resourceInstanceName
            ],
            character = c.DOT
        )
    )


@Function
def getGlobals():
    return FlaskUtil.getGlobals()


def getApi():
    return FlaskUtil.getApi()


def getNullableApi():
    return FlaskUtil.getNullableApi()


def defaultResourceInterceptor(*args, **kwargs):
    def defaultInterceptor(resourceInstanceMethod, *defaultInnerArgs, **defaultInnerKwargs):
        def defaultInnerInterceptor(*defaultInnerInterceptorArgs, **defaultInnerInterceptorKwargs):
            # the reason we have to take self out here is because resource annotation adds it back later on
            return resourceInstanceMethod(*defaultInnerInterceptorArgs[1:], **defaultInnerInterceptorKwargs)
        ReflectionHelper.overrideSignatures(defaultInnerInterceptor, resourceInstanceMethod)
        return defaultInnerInterceptor
    return defaultInterceptor
