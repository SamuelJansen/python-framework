import globals
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.constant import HealthCheckConstant, ConfigurationKeyConstant
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod
from python_framework.api.src.dto import ActuatorHealthDto


@Controller(url=HealthCheckConstant.URI, tag='HealthCheck', description='HealthCheck controller')
class ActuatorHealthController:

    @ControllerMethod(
        responseClass=ActuatorHealthDto.ActuatorHealthResponseDto
        # , logResponse=globals.getGlobalsInstance().getApiSetting(ConfigurationKeyConstant.HEALTH_CHECK_LOG_RESPONSE)
    )
    def get(self):
        return self.service.actuatorHealth.getStatus(), HttpStatus.OK
