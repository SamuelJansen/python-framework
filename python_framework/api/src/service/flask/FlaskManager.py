from python_framework.api.src.service import WebBrowser
from python_helper import Constant as c
from python_helper import log, Function, ReflectionHelper, ObjectHelper, SettingHelper, EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.service import ExceptionHandler
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException
from python_framework.api.src.constant import ConfigurationKeyConstant, JwtConstant, HealthCheckConstant
import globals
import json


KW_URL = 'url'
KW_DEFAULT_URL = 'defaultUrl'
KW_MODEL = 'model'
KW_API = 'api'
KW_APP = 'app'

KW_METHOD = 'method'

KW_RESOURCE = 'resource'

PYTHON_FRAMEWORK_MODULE_NAME = 'python_framework'
PYTHON_FRAMEWORK_INTERNAL_MODULE_NAME_LIST = [
    PYTHON_FRAMEWORK_MODULE_NAME,
    'TestApi',
    'DevTestApi',
    'LocalTestApi',
    'SecurityManagerTestApi',
    'ApiKeyManagerTestApi',
    'SessionManagerTestApi',
    'SecurityManagerAndApiKeyManagerAndSessionManagerTestApi'
]
KW_CONTROLLER_RESOURCE = 'Controller'
KW_SCHEDULER_RESOURCE = 'Scheduler'
KW_SERVICE_RESOURCE = 'Service'
KW_CLIENT_RESOURCE = 'Client'
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

KW_PARAMETERS = 'params'
KW_HEADERS = 'headers'


def newApp(
    filePath
    , successStatus = True
    , failureStatus = True
    , errorStatus = True
    , settingStatus = True
    , statusStatus = True
    , infoStatus = True
    , debugStatus = False
    , warningStatus = False
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
        app = globals.importResource(KW_APP, resourceModuleName=globalsInstance.apiName, required=True)
    except Exception as exception:
        apiPath = f'{c.DOT}{EnvironmentHelper.OS_SEPARATOR}{globalsInstance.BASE_API_PATH}{globals.AttributeKey.API_NAME}.py'
        errorMessage = f"Not possible to load app. Make shure it's name is properlly configured at '{globalsInstance.apiName}' and it's instance is named 'app' at '{apiPath}'"
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
    innerDefaultUrl = getApiUrl(apiInstance)
    if defaultUrl :
        innerDefaultUrl = f'{innerDefaultUrl}{defaultUrl}'
    def inBetweenFunction(function,*argument,**keywordArgument):
        log.wrapper(initialize,f'''{function.__name__} method''')
        if (openInBrowser):
            log.debug(initialize,f'''Openning "{innerDefaultUrl}" url in rowser''')
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

def runApi(*args, api=None, **kwargs):
    if ObjectHelper.isNone(api):
        api = FlaskUtil.getApi()
    muteLogs(api)
    if 'host' not in kwargs and api.host :
        kwargs['host'] = api.host if not 'localhost' == api.host else '0.0.0.0'
    if 'port' not in kwargs and api.port :
        kwargs['port'] = api.port
    apiUrl = getApiUrl(api)
    documentationUrl = OpenApiManager.getDocumentationUrl(api)
    healthCheckUrl = f'{documentationUrl[:-len(OpenApiManager.DOCUMENTATION_ENDPOINT)]}{HealthCheckConstant.URI}'
    log.success(runApi, f'Api will run at {apiUrl}')
    log.success(runApi, f'Health check will be available at {healthCheckUrl}')
    log.success(runApi, f'Documentation will be available at {documentationUrl}')
    api.app.run(*args, **kwargs)

@Function
def getApiUrl(api):
    apiUrl = None
    try :
        apiUrl = f'{api.scheme}://{api.host}{c.BLANK if ObjectHelper.isEmpty(api.port) else f"{c.COLON}{api.port}"}{api.baseUrl}'
    except Exception as exception :
        log.error(getApiUrl.__class__, 'Not possible to parse pai url', exception)
    return apiUrl

@Function
def muteLogs(api):
    import logging
    from werkzeug.serving import WSGIRequestHandler
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.disabled = True
    api.app.logger.disabled = True
    apschedulerLoggerEnabled = api.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_ENABLE)
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
    muteStacktraceOnBusinessRuleException
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
            muteStacktraceOnBusinessRuleException
        )
    elif ObjectHelper.isNotEmptyCollection(apiKeyRequired):
        return handleLockedByApiKeyControllerMethod(
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
            muteStacktraceOnBusinessRuleException
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
            muteStacktraceOnBusinessRuleException
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
        muteStacktraceOnBusinessRuleException
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
    muteStacktraceOnBusinessRuleException
):
    contextList = SecurityManager.getContext()
    if not any(role in set(contextList) for role in roleRequired):
        raise GlobalException(
            message = 'Role not allowed',
            logMessage = f'''Roles {contextList} trying to access denied resourse. Allowed roles {roleRequired}''',
            status = HttpStatus.FORBIDDEN
        )
    elif ObjectHelper.isNotEmptyCollection(apiKeyRequired):
        return handleLockedByApiKeyControllerMethod(
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
            muteStacktraceOnBusinessRuleException
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
            muteStacktraceOnBusinessRuleException
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
        muteStacktraceOnBusinessRuleException
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
@ApiKeyManager.jwtAccessRequired
def handleLockedByApiKeyControllerMethod(
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
    muteStacktraceOnBusinessRuleException
):
    contextList = ApiKeyManager.getContext()
    if not any(apiKey in set(contextList) for apiKey in apiKeyRequired):
        raise GlobalException(
            message = 'ApiKey not allowed',
            logMessage = f'''ApiKey {contextList} trying to access denied resourse. Allowed apiKeys {apiKeyRequired}''',
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
            muteStacktraceOnBusinessRuleException
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
        muteStacktraceOnBusinessRuleException
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
    muteStacktraceOnBusinessRuleException
):
    contextList = SessionManager.getContext()
    if not any(context in set(contextList) for context in contextRequired):
        raise GlobalException(
            message = 'Session not allowed',
            logMessage = f'''Sessions {contextList} trying to access denied resourse. Allowed contexts: {contextRequired}''',
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
            muteStacktraceOnBusinessRuleException
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
    muteStacktraceOnBusinessRuleException
):
    completeResponse = None
    requestBodyAsJson = {}
    if resourceInstanceMethod.__name__ in OpenApiManager.ABLE_TO_RECIEVE_BODY_LIST and requestClass :
        requestBodyAsJson = getRequestBodyAsJson(contentType, requestClass)
        if Serializer.requestBodyIsPresent(requestBodyAsJson):
            serializerReturn = Serializer.convertFromJsonToObject(requestBodyAsJson, requestClass)
            args = getArgsWithSerializerReturnAppended(args, serializerReturn)
    headers = addToKwargs(KW_HEADERS, requestHeaderClass, FlaskUtil.safellyGetHeaders(), kwargs)
    query = addToKwargs(KW_PARAMETERS, requestParamClass, FlaskUtil.safellyGetArgs(), kwargs)
    log.info(resourceInstanceMethod, f'{FlaskUtil.safellyGetVerb()} - {FlaskUtil.safellyGetUrl()}')
    if logRequest :
        log.prettyJson(
        resourceInstanceMethod,
        'request',
        {
            'headers': dict(headers),
            # 'query': query, safellyGetUrl() returns query param
            'body': requestBodyAsJson
        },
        condition = logRequest,
        logLevel = log.INFO
        )
    completeResponse = resourceInstanceMethod(resourceInstance,*args[1:],**kwargs)
    if not (ObjectHelper.isNotNone(completeResponse) and Serializer.isSerializerCollection(completeResponse) and 2 == len(completeResponse)):
        raise GlobalException(logMessage=f'''Bad implementation of {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__class__.__name__}() controller method''')
    return completeResponse

def addToKwargs(key, givenClass, valuesAsDictionary, kwargs):
    if ObjectHelper.isNotEmpty(givenClass):
        toClass = givenClass if ObjectHelper.isNotList(givenClass) else givenClass[0]
        kwargs[key] = Serializer.convertFromJsonToObject({k:v for k,v in valuesAsDictionary.items()}, toClass)
    return valuesAsDictionary

@Function
def jsonifyResponse(response, contentType, status):
    return FlaskUtil.Response(Serializer.jsonifyIt(response),  mimetype=contentType, status=HttpStatus.map(status).enumValue)

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
        serializerReturn = Serializer.convertFromObjectToObject(objectRequest, responseClass)
        args = getArgsWithSerializerReturnAppended(args, serializerReturn)
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
def validateArgs(args, requestClass, method):
    if ObjectHelper.isNotNone(requestClass):
        resourceInstance = args[0]
        if Serializer.isSerializerList(requestClass):
            if 0 < len(requestClass):
                for index in range(len(requestClass)):
                    if Serializer.isSerializerList(args[index + 1]) and len(args[index + 1]) > 0 :
                        expecteObjectClass = requestClass[index][0]
                        for objectInstance in args[index + 1] :
                            ExceptionHandler.validateArgs(resourceInstance, method, objectInstance, expecteObjectClass)
                    else :
                        objectRequest = args[index + 1]
                        expecteObjectClass = requestClass[index]
                        ExceptionHandler.validateArgs(resourceInstance, method, objectRequest, expecteObjectClass)
        else :
            objectRequest = args[1]
            expecteObjectClass = requestClass
            ExceptionHandler.validateArgs(resourceInstance, method, objectRequest, expecteObjectClass)

def validateKwargs(kwargs, resourceInstance, innerResourceInstanceMethod, requestHeaderClass=None, requestParamClass=None):
    classListToValidate = []
    instanceListToValidate = []
    if ObjectHelper.isNotEmpty(requestHeaderClass):
        classListToValidate.append(requestHeaderClass if ObjectHelper.isNotList(requestHeaderClass) else requestHeaderClass[0])
        instanceListToValidate.append(kwargs.get(KW_HEADERS, {}))
    if ObjectHelper.isNotEmpty(requestParamClass):
        classListToValidate.append(requestParamClass if ObjectHelper.isNotList(requestParamClass) else requestParamClass[0])
        instanceListToValidate.append(kwargs.get(KW_PARAMETERS, {}))
    validateArgs([resourceInstance, *instanceListToValidate], classListToValidate, innerResourceInstanceMethod)

@Function
def Controller(
    url = c.SLASH,
    tag = 'Tag not defined',
    description = 'Controller not descripted'
):
    controllerUrl = url
    controllerTag = tag
    controllerDescription = description
    def Wrapper(OuterClass,*args,**kwargs):
        log.wrapper(Controller, f'''wrapping {OuterClass.__name__}''', None)
        class InnerClass(OuterClass, FlaskUtil.Resource):
            url = controllerUrl
            tag = controllerTag
            description = controllerDescription
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
    roleRequired = None,
    apiKeyRequired = None,
    contextRequired = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = False,
    logResponse = False,
    muteStacktraceOnBusinessRuleException = True
):
    controllerMethodUrl = url
    controllerMethodRequestHeaderClass = requestHeaderClass
    controllerMethodRequestParamClass = requestParamClass
    controllerMethodRequestClass = requestClass
    controllerMethodResponseClass = responseClass
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
            # r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            # r.headers["Pragma"] = "no-cache"
            # r.headers["Expires"] = "0"
            # r.headers['Cache-Control'] = 'public, max-age=0'
            resourceInstance = args[0]
            completeResponse = None
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
                # print(f'completeResponse: {completeResponse}')
                validateResponseClass(responseClass, completeResponse)
            except Exception as exception :
                # print(exception)
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
            controllerResponse = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : completeResponse[1].enumName}
            status = completeResponse[1]
            response = jsonifyResponse(controllerResponse, produces, status)
            if logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    'response',
                    {
                        'headers': dict(FlaskUtil.safellyGetResponseHeaders(response)),
                        'body': FlaskUtil.safellyGetResponseJson(response)
                    },
                    # json.loads(Serializer.jsonifyIt(controllerResponse)),
                    condition = logResponse,
                    logLevel = log.INFO
                )
            return response
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = controllerMethodUrl
        innerResourceInstanceMethod.requestHeaderClass = controllerMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = controllerMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = controllerMethodRequestClass
        innerResourceInstanceMethod.responseClass = controllerMethodResponseClass
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

@Function
def SimpleClient():
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(SimpleClient,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = FlaskUtil.getApi().globals
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SimpleClientMethod(requestClass=None):
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs):
        log.wrapper(SimpleClientMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs):
            resourceInstance = args[0]
            try :
                validateArgs(args,requestClass,innerResourceInstanceMethod)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper

def getGlobalException(
    exception,
    resourceInstance,
    resourceInstanceMethod,
    apiInstance = None
):
    return ExceptionHandler.handleLogErrorException(
        exception,
        resourceInstance,
        resourceInstanceMethod,
        apiInstance = apiInstance if ObjectHelper.isNotNone(apiInstance) else FlaskUtil.getNullableApi()
    )

def raiseGlobalException(exception, resourceInstance, resourceInstanceMethod):
    raise getGlobalException(exception, resourceInstance, resourceInstanceMethod)

def getCompleteResponseByException(
    exception,
    resourceInstance,
    resourceInstanceMethod,
    muteStacktraceOnBusinessRuleException
):
    exception = getGlobalException(exception, resourceInstance, resourceInstanceMethod)
    completeResponse = [{'message':exception.message, 'timestamp':str(exception.timeStamp)}, exception.status]
    try :
        logErrorMessage = f'Error processing {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__name__} request'
        if HttpStatus.INTERNAL_SERVER_ERROR <= HttpStatus.map(exception.status):
            log.error(resourceInstance.__class__, logErrorMessage, exception)
        else :
            log.failure(resourceInstance.__class__, logErrorMessage, exception=exception, muteStackTrace=muteStacktraceOnBusinessRuleException)
    except Exception as logErrorMessageException :
        log.debug(getCompleteResponseByException, 'Error logging exception at controller', exception=logErrorMessageException)
        log.error(log.error, 'Error processing request', exception)
    return completeResponse

def validateResponseClass(responseClass, controllerResponse):
    if isNotPythonFrameworkHttpsResponse(controllerResponse):
        raiseBadResponseImplementation(f'Python Framework response cannot be null. It should be a list like this: [{"RESPONSE_CLASS" if ObjectHelper.isNone(responseClass) else responseClass if ObjectHelper.isNotList(responseClass) else responseClass[0]}, HTTPS_CODE]')
    if ObjectHelper.isNotNone(responseClass):
        if Serializer.isSerializerList(responseClass):
            if 0 == len(responseClass):
                log.log(validateResponseClass,f'"responseClass" was not defined')
            elif 1 == len(responseClass):
                if ObjectHelper.isNotList(responseClass[0])  :
                    if not isinstance(controllerResponse[0], responseClass[0]):
                        raiseBadResponseImplementation(f'Response class does not match expected class. Expected "{responseClass[0].__name__}", response "{controllerResponse[0].__class__.__name__}"')
                elif ObjectHelper.isNotList(responseClass[0][0]):
                    if ObjectHelper.isNotList(controllerResponse[0]):
                        raiseBadResponseImplementation(f'Response is not a list. Expected "{responseClass[0].__class__.__name__}", but found "{controllerResponse[0].__class__.__name__}"')
                    elif Serializer.isSerializerList(controllerResponse[0]) and 0 < len(controllerResponse[0]) and not isinstance(controllerResponse[0][0], responseClass[0][0]):
                        raiseBadResponseImplementation(f'Response element class does not match expected element class. Expected "{responseClass[0][0].__name__}", response "{controllerResponse[0][0].__class__.__name__}"')
        else :
            if not isinstance(controllerResponse[0], responseClass):
                raiseBadResponseImplementation(f'Response class does not match expected class. Expected "{responseClass.__name__}", response "{controllerResponse[0].__class__.__name__}"')
    else :
        log.log(validateResponseClass,f'"responseClass" was not defined')

def isPythonFrameworkHttpsResponse(controllerResponse):
    return (ObjectHelper.isTuple(controllerResponse) or ObjectHelper.isList(controllerResponse)) and 2 == len(controllerResponse)

def isNotPythonFrameworkHttpsResponse(controllerResponse):
    return not isPythonFrameworkHttpsResponse(controllerResponse)

def raiseBadResponseImplementation(cause):
    raise Exception(f'Bad response implementation. {cause}')

@Function
def getGlobals():
    return FlaskUtil.getGlobals()

def getApi():
    return FlaskUtil.getApi()

def getNullableApi():
    return FlaskUtil.getNullableApi()
