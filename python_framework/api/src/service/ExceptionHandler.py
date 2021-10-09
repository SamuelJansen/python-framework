import datetime
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError, RevokedTokenError
from jwt import ExpiredSignatureError, InvalidSignatureError
from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper
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
        status = None,
        message = None,
        logMessage = None,
        logResource = None,
        logResourceMethod = None
    ):
        self.timeStamp = datetime.datetime.now()
        self.status = status if ObjectHelper.isNotNone(status) else DEFAULT_STATUS
        self.message = message if ObjectHelper.isNotEmpty(message) and StringHelper.isNotBlank(message) else DEFAULT_MESSAGE if 500 <= self.status else self.status.enumName
        self.verb = safellyGetVerb()
        self.url = safellyGetUrl()
        self.logMessage = logMessage if ObjectHelper.isNotEmpty(logMessage) and StringHelper.isNotBlank(logMessage) else DEFAULT_LOG_MESSAGE
        self.logResource = logResource if ObjectHelper.isNotEmpty(logResource) else DEFAULT_LOG_RESOURCE
        self.logResourceMethod = logResourceMethod if ObjectHelper.isNotEmpty(logResourceMethod) else DEFAULT_LOG_RESOURCE_METHOD
        self.logPayload = self.getRequestBody()

    def __str__(self):
        return f'''{GlobalException.__name__} thrown at {self.timeStamp}. Status: {self.status}, message: {self.message}, verb: {self.verb}, url: {self.url}{', logMessage: ' if self.logMessage else c.NOTHING}{self.logMessage}'''

    def getRequestBody(self) :
        try :
            requestBody = request.get_json()
        except :
            try :
                requestBody = request.get_data()
            except :
                requestBody = {}
        return requestBody

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
def handleLogErrorException(exception, resourceInstance, resourceInstanceMethod, api = None, logMessage: str = None) :
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
            if ObjectHelper.isNone(logMessage):
                logMessage = str(exception)
            else:
                logMessage = f'{logMessage}{c.DOT_SPACE_CAUSE}{str(exception)}'
        else:
            if ObjectHelper.isNone(logMessage):
                logMessage = DEFAULT_LOG_MESSAGE
            else:
                logMessage = f'{logMessage}{c.DOT_SPACE_CAUSE}{str(exception)}'
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
        apiInstance.repository.saveAndCommit(httpErrorLog)
    except Exception as errorLogException :
        log.warning(resourceInstance.__class__, f'Failed to persist {ErrorLog.ErrorLog.__name__}', exception=errorLogException)
    return exception

def safellyGetUrl() :
    url = None
    try :
        url = request.url
    except Exception as exception :
        ...
    return url

def safellyGetVerb() :
    verb = None
    try :
        verb = request.method
    except Exception as exception :
        ...
    return verb
