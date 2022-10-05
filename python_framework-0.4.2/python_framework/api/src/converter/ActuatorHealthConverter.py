from python_framework.api.src.annotation.ConverterAnnotation import Converter, ConverterMethod
from python_framework.api.src.model import ActuatorHealth
from python_framework.api.src.dto import ActuatorHealthDto

@Converter()
class ActuatorHealthConverter:

    @ConverterMethod(
        requestClass=ActuatorHealth.ActuatorHealth,
        responseClass=ActuatorHealthDto.ActuatorHealthResponseDto
    )
    def fromModelToResponseDto(self, model, dto) :
        return dto
