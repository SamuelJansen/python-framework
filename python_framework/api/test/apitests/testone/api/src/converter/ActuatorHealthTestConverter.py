from python_framework.api.src.service.flask.FlaskManager import Converter, ConverterMethod
from python_framework.api.src.model import ActuatorHealth
from python_framework.api.src.dto import ActuatorHealthDto

@Converter()
class ActuatorHealthTestConverter:

    @ConverterMethod(
        requestClass=[[ActuatorHealth.ActuatorHealth]],
        responseClass=[[ActuatorHealthDto.ActuatorHealthResponseDto]]
    )
    def fromModelListToResponseDtoList(self, modelList, dtoList) :
        return dtoList
