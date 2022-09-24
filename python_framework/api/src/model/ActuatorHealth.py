import datetime
from python_helper import log
import python_framework.api.src.service.SqlAlchemyProxy as sap
from python_framework.api.src.model.FrameworkModel import ACTUATOR_HEALTH, MODEL
from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus

MAX_STATUS_SIZE = 62
DEFAULT_STATUS = ActuatorHealthStatus.DOWN

class ActuatorHealth(MODEL):
    __tablename__ = ACTUATOR_HEALTH

    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    status = sap.Column(sap.String(MAX_STATUS_SIZE), default=DEFAULT_STATUS)
    laskCheck = sap.Column(sap.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self,
        id = None,
        status = DEFAULT_STATUS,
        laskCheck = None
    ):
        self.id = id
        self.status = status
        self.laskCheck = laskCheck
        return self.onChange(eventType=sap.OnORMChangeEventType.SELF)

    def onChange(self, *args, **kwagrs):
        if str(sap.OnORMChangeEventType.UNKNOWN) is not str(kwagrs.get('eventType')):
            self.status = ActuatorHealthStatus.map(self.status)
        else:
            log.warning(self.onChange, f'{str(sap.OnORMChangeEventType.UNKNOWN)} change event received. Ignoring it by default')
        return self

    def __repr__(self):
        return f'{self.__tablename__}(id={self.id}, laskCheck={self.laskCheck}, status={self.status})'
