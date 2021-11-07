from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.constant import HealthCheckConstant
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod
from python_framework.api.src.dto import ActuatorHealthDto

@Controller(url=HealthCheckConstant.URI, tag='HealthCheck', description='HealthCheck controller')
class ActuatorHealthController:

    @ControllerMethod(
        responseClass=ActuatorHealthDto.ActuatorHealthResponseDto
    )
    def get(self):
        return self.service.actuatorHealth.getStatus(), HttpStatus.OK
