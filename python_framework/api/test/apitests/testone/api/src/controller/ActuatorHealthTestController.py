from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod
from python_framework.api.src.dto import ActuatorHealthDto

import EnumAsQueryDto

@Controller(url='/test/actuator/health', tag='HealthCheckTest', description='HealthCheck controller test')
class ActuatorHealthTestController:

    @ControllerMethod(
        requestClass=EnumAsQueryDto.EnumAsQueryRequestDto,
        # requestClass=[dict],
        responseClass=[[ActuatorHealthDto.ActuatorHealthResponseDto]],
        logResponse=True
    )
    def post(self, dto):
        # HttpStatus.map(dto['status'])
        # EnumAsQueryDto.EnumAsQueryRequestDto(HttpStatus.map(dto['status']))
        return self.service.status.findAllByStatus(dto), HttpStatus.OK
