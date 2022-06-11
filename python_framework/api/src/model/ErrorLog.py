import datetime
from python_helper import Constant as c
import python_framework.api.src.service.SqlAlchemyProxy as sap
from python_framework.api.src.model.FrameworkModel import ERROR_LOG, MODEL
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.converter.static import StaticConverter

MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE = 16384
MAX_MESSAGE_SIZE = 512
MAX_URL_SIZE = 512
MAX_VERB_SIZE = 8
MAX_RESOURCE_NAME_SIZE = 128
MAX_RESOURCE_METHOD_NAME_SIZE = 128

DEFAULT_STATUS: HttpStatus = HttpStatus.INTERNAL_SERVER_ERROR

class ErrorLog(MODEL):
    __tablename__ = ERROR_LOG

    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    status = sap.Column(sap.Integer(), default=DEFAULT_STATUS.enumValue)
    verb = sap.Column(sap.String(MAX_VERB_SIZE))
    url = sap.Column(sap.String(MAX_URL_SIZE))
    message = sap.Column(sap.String(MAX_MESSAGE_SIZE))
    logMessage = sap.Column(sap.String(MAX_MESSAGE_SIZE))
    logHeaders = sap.Column(sap.String(MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE))
    logPayload = sap.Column(sap.String(MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE))
    logResource = sap.Column(sap.String(MAX_RESOURCE_NAME_SIZE))
    logResourceMethod = sap.Column(sap.String(MAX_RESOURCE_METHOD_NAME_SIZE))
    timeStamp = sap.Column(sap.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self,
        id = None,
        status = None,
        verb = None,
        url = None,
        message = None,
        logMessage = None,
        logHeaders = None,
        logPayload = None,
        logResource = None,
        logResourceMethod = None,
        timeStamp = None
    ):
        self.id = id
        self.status = HttpStatus.map(StaticConverter.getValueOrDefault(status, DEFAULT_STATUS)).enumValue
        self.verb = str(verb)[:MAX_VERB_SIZE-1]
        self.url = str(url)[:MAX_URL_SIZE-1]
        self.message = str(message)[:MAX_MESSAGE_SIZE-1]
        self.logMessage = str(logMessage)[:MAX_MESSAGE_SIZE-1]
        self.logHeaders = str(logPayload)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logPayload = str(logPayload)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logResource = str(logResource)[:MAX_RESOURCE_NAME_SIZE-1]
        self.logResourceMethod = str(logResourceMethod)[:MAX_RESOURCE_METHOD_NAME_SIZE-1]
        self.timeStamp = timeStamp

    def override(self, globalException):
        self.status = HttpStatus.map(StaticConverter.getValueOrDefault(globalException.status, DEFAULT_STATUS)).enumValue
        self.verb = str(globalException.verb)[:MAX_VERB_SIZE-1]
        self.url = str(globalException.url)[:MAX_URL_SIZE-1]
        self.message = str(globalException.message)[:MAX_MESSAGE_SIZE-1]
        self.logMessage = str(globalException.logMessage)[:MAX_MESSAGE_SIZE-1]
        self.logHeaders = str(globalException.logHeaders)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logPayload = str(globalException.logPayload)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logResource = str(globalException.logResource)[:MAX_RESOURCE_NAME_SIZE-1]
        self.logResourceMethod = str(globalException.logResourceMethod)[:MAX_RESOURCE_METHOD_NAME_SIZE-1]
        self.timeStamp = globalException.timeStamp

    def __repr__(self):
        return f'{self.__tablename__}(verb={self.verb}, url={self.url}, status={self.status}, message={self.message}, id={self.id})'
