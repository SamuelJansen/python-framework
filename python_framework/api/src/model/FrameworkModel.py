import python_framework.api.src.service.SqlAlchemyProxy as sap
from python_framework.api.src.annotation.MethodWrapper import Function

ERROR_LOG = 'ErrorLog'
MODEL = sap.getNewModel()

@Function
def getModel() :
    return MODEL
