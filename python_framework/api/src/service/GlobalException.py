import datetime
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError, RevokedTokenError
from jwt import ExpiredSignatureError
from python_helper import Constant, log
from python_framework.api.src.annotation.MethodWrapper import Method
from python_framework.api.src.helper import Serializer
from python_framework.api.src.domain import HttpStatus
from python_framework.api.src.model import ErrorLog

DEFAULT_MESSAGE = 'Something bad happened. Please, try again later'
DEFAULT_STATUS = HttpStatus.INTERNAL_SERVER_ERROR
DEFAULT_LOG_MESSAGE = Constant.NOTHING

DEFAULT_LOG_RESOURCE = Constant.NOTHING
DEFAULT_LOG_RESOURCE_METHOD = Constant.NOTHING

DOT_SPACE_CAUSE = f'''{Constant.DOT_SPACE}{Constant.LOG_CAUSE}'''

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
        self.message = message if message else DEFAULT_MESSAGE
        self.status = status if status else DEFAULT_STATUS
        self.verb = request.method
        self.url = request.url
        self.logMessage = logMessage if logMessage else DEFAULT_LOG_MESSAGE
        self.logResource = logResource if logResource else DEFAULT_LOG_RESOURCE
        self.logResourceMethod = logResourceMethod if logResourceMethod else DEFAULT_LOG_RESOURCE_METHOD
        self.logPayload = self.getRequestBody()

    def __str__(self):
        return f'''[{self.timeStamp}] {GlobalException.__name__} thrown. Status: {self.status}, message: {self.message}, url: {self.url}{', logMessage: ' if self.logMessage else Constant.NOTHING}{self.logMessage}'''

    def getRequestBody(self) :
        try :
            requestBody = request.get_json()
        except :
            try :
                requestBody = request.get_data()
            except :
                requestBody = {}
        return requestBody

def validateArgs(self, method, objectRequest, expecteObjectClass):
    try :
        proceedValidation = True
        if Serializer.isList(expecteObjectClass) and Serializer.isList(objectRequest) :
            if len(objectRequest) == 0 :
                proceedValidation = False
        if proceedValidation and (objectRequest and not type(expecteObjectClass) == type(objectRequest.__class__) and expecteObjectClass.__name__ == objectRequest.__class__.__name__) :
            raise GlobalException(logMessage = f'Invalid args. {self.__class__}.{method} call got an unnexpected object request: {objectRequest.__class__}. It should be {expecteObjectClass}')
    except Exception as exception :
        log.error(expecteObjectClass.__class__, f'Failed to validate args of {resourceInstanceMethod.__name__} method', exception)
        raise GlobalException(logMessage = f'Failed to validate args of {resourceInstanceMethod.__name__} method{DOT_SPACE_CAUSE}{str(exception)}')

def handleLogErrorException(exception, resourceInstance, resourceInstanceMethod, apiInstance) :
    if not (isinstance(exception.__class__, GlobalException) or GlobalException.__name__ == exception.__class__.__name__) :
        log.error(resourceInstance.__class__, f'Failed to excecute {resourceInstanceMethod.__name__} method due to {exception.__class__.__name__} exception', exception)
        message = None
        status = None
        if (isinstance(exception.__class__, NoAuthorizationError) or NoAuthorizationError.__name__ == exception.__class__.__name__ or
            isinstance(exception.__class__, RevokedTokenError) or RevokedTokenError.__name__ == exception.__class__.__name__ or
            isinstance(exception.__class__, ExpiredSignatureError) or ExpiredSignatureError.__name__ == exception.__class__.__name__):
            if not message :
                message = Constant.NOTHING
            message += str(exception)
            status = HttpStatus.UNAUTHORIZED
        exception = GlobalException(message=message, logMessage=str(exception), logResource=resourceInstance, logResourceMethod=resourceInstanceMethod, status=status)
    try :
        if not exception.logResource or Constant.NOTHING == exception.logResource or not resourceInstance == exception.logResource :
            exception.logResource = resourceInstance
        if not exception.logResourceMethod or Constant.NOTHING == exception.logResourceMethod or not resourceInstanceMethod == exception.logResourceMethod :
            exception.logResourceMethod = resourceInstanceMethod
        httpErrorLog = ErrorLog.ErrorLog()
        httpErrorLog.override(exception)
        apiInstance.repository.saveAndCommit(httpErrorLog)
    except Exception as errorLogException :
        log.error(resourceInstance.__class__, f'Failed to persist {ErrorLog.ErrorLog.__name__}', errorLogException)
    return exception
