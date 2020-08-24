from python_framework.api.src.service.framework.SqlAlchemyProxy import *

ERROR_LOG = 'ErrorLog'
MODEL = getNewModel()

MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE = 16384
MAX_MESSAGE_SIZE = 512
MAX_URL_SIZE = 512
MAX_VERB_SIZE = 8
MAX_RESOURCE_NAME_SIZE = 128
MAX_RESOURCE_METHOD_NAME_SIZE = 128

def getNewErrorLogModel(baseModel)

class ErrorLog(MODEL):
    __tablename__ = ERROR_LOG

    id = Column(Integer(), Sequence(f'{__tablename__}{ID}{SEQ}'), primary_key=True)
    timeStamp = Column(DateTime())
    status = Column(Integer())
    verb = Column(String(MAX_VERB_SIZE))
    url = Column(String(MAX_URL_SIZE))
    message = Column(String(MAX_MESSAGE_SIZE))
    logMessage = Column(String(MAX_MESSAGE_SIZE))
    logPayload = Column(String(MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE))
    logResource = Column(String(MAX_RESOURCE_NAME_SIZE))
    logResourceMethod = Column(String(MAX_RESOURCE_METHOD_NAME_SIZE))

    def __init__(self,
        id = None,
        timeStamp = None,
        status = None,
        verb = None,
        url = None,
        message = None,
        logMessage = None,
        logPayload = None,
        logResource = None,
        logResourceMethod = None
    ):
        self.timeStamp = timeStamp
        self.status = status
        self.verb = str(verb)[:MAX_VERB_SIZE-1]
        self.url = str(url)[:MAX_URL_SIZE-1]
        self.message = str(message)[:MAX_MESSAGE_SIZE-1]
        self.logMessage = str(logMessage)[:MAX_MESSAGE_SIZE-1]
        self.logPayload = str(logPayload)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logResource = str(logResource)[:MAX_RESOURCE_NAME_SIZE-1]
        self.logResourceMethod = str(logResourceMethod)[:MAX_RESOURCE_METHOD_NAME_SIZE-1]
        self.id = id

    def override(self, globalException):
        self.timeStamp = globalException.timeStamp
        self.status = globalException.status
        self.verb = str(globalException.verb)[:MAX_VERB_SIZE-1]
        self.url = str(globalException.url)[:MAX_URL_SIZE-1]
        self.message = str(globalException.message)[:MAX_MESSAGE_SIZE-1]
        self.logMessage = str(globalException.logMessage)[:MAX_MESSAGE_SIZE-1]
        self.logPayload = str(globalException.logPayload)[:MAX_HTTP_ERROR_LOG_PAYLOAD_SIZE-1]
        self.logResource = str(globalException.logResource)[:MAX_RESOURCE_NAME_SIZE-1]
        self.logResourceMethod = str(globalException.logResourceMethod)[:MAX_RESOURCE_METHOD_NAME_SIZE-1]

    def __repr__(self):
        return f'{self.__tablename__}(verb={self.verb}, url={self.url}, status={self.status}, message={self.message}, id={self.id})'
