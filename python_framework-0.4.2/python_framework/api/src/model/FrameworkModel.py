from python_helper import Constant as c
from python_helper import Function
import python_framework.api.src.service.SqlAlchemyProxy as sap

ERROR_LOG = 'ErrorLog'
ACTUATOR_HEALTH = 'ActuatorHealth'
MODEL = sap.getNewModel()

@Function
def getModel() :
    return MODEL
