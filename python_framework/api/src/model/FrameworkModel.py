import python_framework.api.src.service.SqlAlchemyProxy as sap
from python_helper import Function

ERROR_LOG = 'ErrorLog'
ACTUATOR_HEALTH = 'ActuatorHealth'
MODEL = sap.getNewModel()

@Function
def getModel() :
    return MODEL
