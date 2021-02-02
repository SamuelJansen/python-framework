import datetime
import python_framework.api.src.service.SqlAlchemyProxy as sap
from python_framework.api.src.model.FrameworkModel import ACTUATOR_HEALTH, MODEL
from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus

MAX_STATUS_SIZE = 62

class ActuatorHealth(MODEL):
    __tablename__ = ACTUATOR_HEALTH

    laskCheck = sap.Column(sap.DateTime(), default=datetime.datetime.utcnow)
    status = sap.Column(sap.String(MAX_STATUS_SIZE), default=ActuatorHealthStatus.DOWN)
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)

    def __init__(self,
        status = ActuatorHealthStatus.DOWN,
        laskCheck = None,
        id = None
    ):
        self.status = status
        self.laskCheck = laskCheck
        self.id = id

    def __repr__(self):
        return f'{self.__tablename__}(id={self.id}, laskCheck={self.laskCheck}, status={self.status})'
