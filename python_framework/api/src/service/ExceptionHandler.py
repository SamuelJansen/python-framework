from flask_jwt_extended.exceptions import NoAuthorizationError, RevokedTokenError
from jwt import ExpiredSignatureError, InvalidSignatureError
from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, StringHelper, DateTimeHelper
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
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

class GlobalException(Exception):
    def __init__(self,
        message = None,
        logMessage = None,
        status = None,
        logResource = None,
        logResourceMethod = None,
        verb = None,
        url = None,
        logPayload = None
    ):
        self.timeStamp = DateTimeHelper.now()
        self.status = HttpStatus.map(DEFAULT_STATUS if ObjectHelper.isNone(status) else status).enumValue
        self.message = message if ObjectHelper.isNotEmpty(message) and StringHelper.isNotBlank(message) else DEFAULT_MESSAGE if 500 <= self.status else self.status.enumName
        self.verb = self.getRequestVerb()
        self.url = self.getRequestUrl()
        self.logMessage = DEFAULT_LOG_MESSAGE if ObjectHelper.isNone(logMessage) or StringHelper.isBlank(logMessage) else logMessage
        self.logResource = DEFAULT_LOG_RESOURCE if ObjectHelper.isNone(logResource) else logResource
        self.logResourceMethod = DEFAULT_LOG_RESOURCE_METHOD if ObjectHelper.isNone(logResourceMethod) else logResourceMethod
        self.logPayload = self.getRequestBody()

    def __str__(self):
        return f'''{GlobalException.__name__} thrown at {self.timeStamp}. Status: {self.status}, message: {self.message}, verb: {self.verb}, url: {self.url}{', logMessage: ' if self.logMessage else c.NOTHING}{self.logMessage}'''

    def getRequestBody(self) :
        return FlaskUtil.safellyGetRequestBody()

    def getRequestVerb(self) :
        return FlaskUtil.safellyGetVerb()

    def getRequestUrl(self) :
        return FlaskUtil.safellyGetUrl()


@Function
def validateArgs(self, method, objectRequest, expecteObjectClass):
    try :
        proceedValidation = True
        if ObjectHelper.isList(expecteObjectClass) and ObjectHelper.isList(objectRequest) :
            if len(objectRequest) == 0 :
                proceedValidation = False
        if proceedValidation and (objectRequest and not type(expecteObjectClass) == type(objectRequest.__class__) and expecteObjectClass.__name__ == objectRequest.__class__.__name__) :
            raise GlobalException(logMessage = f'Invalid args. {self.__class__}.{method} call got an unnexpected object request: {objectRequest.__class__}. It should be {expecteObjectClass}')
    except Exception as exception :
        log.failure(expecteObjectClass.__class__, f'Failed to validate args of {method.__name__} method', exception)
        raise GlobalException(logMessage = f'Failed to validate args of {method.__name__} method{DOT_SPACE_CAUSE}{str(exception)}')

@Function
def handleLogErrorException(exception, resourceInstance, resourceInstanceMethod, apiInstance = None) :
    if not (isinstance(exception.__class__, GlobalException) or GlobalException.__name__ == exception.__class__.__name__) :
        log.debug(handleLogErrorException, f'Failed to excecute {resourceInstanceMethod.__name__} method due to {exception.__class__.__name__} exception', exception=exception)
        message = None
        status = None
        logMessage = None
        if (isinstance(exception.__class__, NoAuthorizationError) or NoAuthorizationError.__name__ == exception.__class__.__name__ or
            isinstance(exception.__class__, RevokedTokenError) or RevokedTokenError.__name__ == exception.__class__.__name__ or
            isinstance(exception.__class__, InvalidSignatureError) or InvalidSignatureError.__name__ == exception.__class__.__name__ or
            isinstance(exception.__class__, ExpiredSignatureError) or ExpiredSignatureError.__name__ == exception.__class__.__name__):
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
            status = status
        )
    try :
        if not exception.logResource or c.NOTHING == exception.logResource or not resourceInstance == exception.logResource :
            exception.logResource = resourceInstance
        if not exception.logResourceMethod or c.NOTHING == exception.logResourceMethod or not resourceInstanceMethod == exception.logResourceMethod :
            exception.logResourceMethod = resourceInstanceMethod
        httpErrorLog = ErrorLog.ErrorLog()
        httpErrorLog.override(exception)
        if ObjectHelper.isNone(apiInstance):
            from python_framework import FlaskManager
            apiInstance = FlaskManager.getApi()
        else:
            apiInstance = apiInstance
            try:
                apiInstance.repository.commit()
            except Exception as preCommitException:
                log.warning(handleLogErrorException, f'Failed to pre commit before persist {ErrorLog.ErrorLog.__name__}', exception=preCommitException)
        apiInstance.repository.saveAndCommit(httpErrorLog)
    except Exception as errorLogException :
        log.warning(handleLogErrorException, f'Failed to persist {ErrorLog.ErrorLog.__name__}', exception=errorLogException)
    return exception
