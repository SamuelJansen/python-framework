from jwt import ExpiredSignatureError, InvalidSignatureError

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, StringHelper, DateTimeHelper, ReflectionHelper

from python_framework.api.src.domain import HttpDomain
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.model import ErrorLog


DEFAULT_MESSAGE = 'Something bad happened. Please, try again later'
DEFAULT_STATUS = HttpStatus.INTERNAL_SERVER_ERROR
DEFAULT_LOG_MESSAGE = 'Log message not present'

DEFAULT_LOG_RESOURCE = 'ResourceNotInformed'
DEFAULT_LOG_RESOURCE_METHOD = 'resourceMethodNotInformed'

DOT_SPACE_CAUSE = f'''{c.DOT_SPACE}{c.LOG_CAUSE}'''

KW_GET = 'get'
KW_POST = 'post'
KW_PUT = 'put'
KW_PATCH = 'patch'
KW_DELETE = 'delete'

ABLE_TO_RECIEVE_BODY_LIST = [
    KW_POST,
    KW_PUT,
    KW_PATCH
]

def getDefaultBodyException(exception=None):
    try:
        bodyErrorResponse = {
            'message': exception.message,
            'timestamp': str(exception.timeStamp)
        }
    except:
        bodyErrorResponse = {
            'message': DEFAULT_MESSAGE,
            'timestamp': str(DateTimeHelper.now())
        }
    uriIfAny = FlaskUtil.safellyGetPath()
    if ObjectHelper.isNotNone(uriIfAny) and StringHelper.isNotBlank(uriIfAny):
        bodyErrorResponse['uri'] = uriIfAny
    return bodyErrorResponse


class ExceptionManager:
    ...


class GlobalException(Exception):
    def __init__(self,
        message = None,
        logMessage = None,
        status = None,
        logResource = None,
        logResourceMethod = None,
        verb = None,
        url = None,
        logPayload = None,
        logHeaders = None,
        context = None,
        originalException = None
    ):
        self.timeStamp = DateTimeHelper.now()
        self.status = HttpStatus.map(DEFAULT_STATUS if ObjectHelper.isNone(status) else status).enumValue
        self.message = message if ObjectHelper.isNotEmpty(message) and StringHelper.isNotBlank(message) else DEFAULT_MESSAGE if 500 <= self.status else StringHelper.toText(self.status.enumName)
        self.verb = verb if ObjectHelper.isNotNone(verb) else self.getRequestVerb()
        self.url = url if ObjectHelper.isNotNone(url) else self.getRequestUrl()
        self.logMessage = DEFAULT_LOG_MESSAGE if ObjectHelper.isNone(logMessage) or StringHelper.isBlank(logMessage) else logMessage
        self.logResource = DEFAULT_LOG_RESOURCE if ObjectHelper.isNone(logResource) else logResource
        self.logResourceMethod = DEFAULT_LOG_RESOURCE_METHOD if ObjectHelper.isNone(logResourceMethod) else logResourceMethod
        self.logPayload = logPayload if ObjectHelper.isNotNone(logPayload) else self.getRequestBody()
        self.logHeaders = logHeaders if ObjectHelper.isNotNone(logHeaders) else self.getRequestHeaders()
        self.context = HttpDomain.CONTROLLER_CONTEXT if ObjectHelper.isNone(context) else context
        self.originalException = originalException

    def __str__(self):
        return f'''{GlobalException.__name__} thrown at {self.timeStamp}. Status: {self.status}, message: {self.message}, verb: {self.verb}, url: {self.url}{', logMessage: ' if self.logMessage else c.NOTHING}{self.logMessage}'''

    def getRequestBody(self) :
        return FlaskUtil.safellyGetRequestBodyOrRequestData()

    def getRequestVerb(self) :
        return FlaskUtil.safellyGetVerb()

    def getRequestUrl(self) :
        return FlaskUtil.safellyGetUrl()

    def getRequestHeaders(self):
        return FlaskUtil.safellyGetHeaders()


@Function
def validateArgs(resourceInstance, resourceInstanceMethod, objectRequest, expecteObjectClass):
    try :
        if ObjectHelper.isNotNone(objectRequest) and (
            not (
                ObjectHelper.isList(expecteObjectClass) and Serializer.isSerializerList(objectRequest) and len(objectRequest) == 0
            )
        ) and (
            (
                ObjectHelper.isList(expecteObjectClass) and Serializer.isNotSerializerList(objectRequest)
            ) or (
                ObjectHelper.isNotList(expecteObjectClass) and Serializer.isSerializerList(objectRequest)
            ) or (
                (
                    Serializer.isNotSerializerList(expecteObjectClass) and (
                        (
                            not ReflectionHelper.getClassName(objectRequest) == ReflectionHelper.getName(expecteObjectClass)
                        ) or (
                            not isinstance(objectRequest, expecteObjectClass)
                        )
                    )
                ) and (
                    Serializer.isSerializerList(expecteObjectClass) and Serializer.isSerializerList(objectRequest) and not isinstance(objectRequest[0], expecteObjectClass[0])
                )
            )
        ):
            typeComparison = f'type(objectRequest: {objectRequest}): {type(objectRequest)}'
            resourceCompleteName = getCompleteName(resourceInstance, resourceInstanceMethod)
            expectedClassName = f'{ReflectionHelper.getClassName(expecteObjectClass) if Serializer.isSerializerList(expecteObjectClass) else ReflectionHelper.getName(expecteObjectClass)}'
            raise GlobalException(logMessage = f'Invalid args{c.DOT_SPACE}{resourceCompleteName} call got an unnexpected object request class: {ReflectionHelper.getClassName(objectRequest)}{c.DOT_SPACE}It should be of type(requestClass{expecteObjectClass}): {expectedClassName}{c.DOT_SPACE}Object request: {typeComparison}')
    except GlobalException as globalException:
        raise globalException
    except Exception as exception:
        typeComparison = f'type(objectRequest: {objectRequest}): {type(objectRequest)}'
        resourceCompleteName = getCompleteName(resourceInstance, resourceInstanceMethod)
        expectedClassName = f'{ReflectionHelper.getClassName(expecteObjectClass) if Serializer.isSerializerList(expecteObjectClass) else ReflectionHelper.getName(expecteObjectClass)}'
        errorMessage = f'Failed to validate args of {resourceCompleteName} method{c.DOT_SPACE}Object request: {typeComparison}{c.DOT_SPACE}Expected request type(requestClass{expecteObjectClass}): {expectedClassName}'
        raise GlobalException(logMessage = f'{errorMessage}{c.DOT_SPACE_CAUSE}{str(exception)}')

@Function
def handleLogErrorException(exception, resourceInstance, resourceInstanceMethod, context, apiInstance = None) :
    try :
        exception = getGeneralGlobalException(exception, resourceInstance, resourceInstanceMethod, context, apiInstance = None)
        if ObjectHelper.isNone(apiInstance):
            from python_framework import FlaskManager
            apiInstance = FlaskManager.getApi()
        httpErrorLog = ErrorLog.ErrorLog()
        httpErrorLog.override(exception)
        apiInstance.resource.manager.exception.handleErrorLog(httpErrorLog)
    except Exception as errorLogException :
        log.warning(handleLogErrorException, f'Failed to handle {ErrorLog.ErrorLog.__name__}', exception=errorLogException)
    return exception


@Function
def getGeneralGlobalException(exception, resourceInstance, resourceInstanceMethod, context, apiInstance = None):
    originalException = exception
    if not (isinstance(exception, GlobalException) or GlobalException.__name__ == exception.__class__.__name__):
        log.debug(getGeneralGlobalException, f'Failed to excecute {getCompleteName(resourceInstance, resourceInstanceMethod)} method due to {exception.__class__.__name__} exception', exception=exception)
        message = None
        status = None
        logMessage = None
        if (isinstance(exception, InvalidSignatureError) or InvalidSignatureError.__name__ == exception.__class__.__name__ or
            isinstance(exception, ExpiredSignatureError) or ExpiredSignatureError.__name__ == exception.__class__.__name__):
            message = 'Unauthorized' if ObjectHelper.isNone(exception) or StringHelper.isBlank(str(exception)) else str(exception)
            status = HttpStatus.UNAUTHORIZED
        if ObjectHelper.isNotNone(exception) and StringHelper.isNotBlank(str(exception)) :
            logMessage = str(exception)
        else:
            logMessage = DEFAULT_LOG_MESSAGE
        exception = GlobalException(
            message = message,
            logMessage = logMessage,
            logResource = resourceInstance,
            logResourceMethod = resourceInstanceMethod,
            status = status,
            originalException = originalException
        )
    try :
        if not context == exception.context:
            exception = GlobalException(
                message = exception.message,
                logMessage = exception.logMessage,
                logResource = resourceInstance,
                logResourceMethod = resourceInstanceMethod,
                status = exception.status,
                context = context,
                originalException = originalException
            )
        else:
            if not exception.logResource or c.NOTHING == exception.logResource or not resourceInstance == exception.logResource :
                exception.logResource = resourceInstance
            if not exception.logResourceMethod or c.NOTHING == exception.logResourceMethod or not resourceInstanceMethod == exception.logResourceMethod :
                exception.logResourceMethod = resourceInstanceMethod
    except Exception as globalExceptionHandlingException :
        exception = GlobalException(originalException = originalException)
        log.warning(getGeneralGlobalException, f'Failed to get GlobalException', exception=globalExceptionHandlingException)
    return exception


@Function
def getClientGlobalException(clientResponse, context, logMessage, exception=None, status=DEFAULT_STATUS, message=DEFAULT_MESSAGE):
    return GlobalException(
        message = message,
        logMessage = logMessage,
        url = FlaskUtil.safellyGetRequestUrlFromResponse(clientResponse),
        status = status if ObjectHelper.isNotNone(status) else FlaskUtil.safellyGetResponseStatus(clientResponse),
        logHeaders = {
            HttpDomain.REQUEST_HEADERS_KEY: FlaskUtil.safellyGetRequestHeadersFromResponse(clientResponse),
            HttpDomain.RESPONSE_HEADERS_KEY: FlaskUtil.safellyGetResponseHeaders(clientResponse)
        },
        logPayload = {
            HttpDomain.REQUEST_BODY_KEY: FlaskUtil.safellyGetRequestJsonFromResponse(clientResponse),
            HttpDomain.RESPONSE_BODY_KEY: FlaskUtil.safellyGetResponseJson(clientResponse)
        },
        context = context,
        originalException = exception
    )


def getCompleteName(resourceInstance, resourceInstanceMethod):
    return f'{ReflectionHelper.getClassName(resourceInstance)}{c.DOT}{ReflectionHelper.getName(resourceInstanceMethod)}'
