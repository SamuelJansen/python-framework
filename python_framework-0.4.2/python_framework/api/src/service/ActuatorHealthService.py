from python_helper import ObjectHelper, log, DateTimeHelper
from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus
from python_framework.api.src.model import ActuatorHealth
from python_framework.api.src.annotation.ServiceAnnotation import Service, ServiceMethod

@Service()
class ActuatorHealthService:

    @ServiceMethod()
    def getStatus(self):
        try:
            actuatorHealthList = self.repository.actuatorHealth.findAll()
            if ObjectHelper.isList(actuatorHealthList) and 1 == len(actuatorHealthList) :
                model = actuatorHealthList[0]
            else :
                try :
                    model = self.repository.actuatorHealth.save(ActuatorHealth.ActuatorHealth(status=ActuatorHealthStatus.UP))
                except Exception as exception :
                    log.error(self.getStatus, 'Api cannot reach database', exception)
                    model = ActuatorHealth.ActuatorHealth()
            model.laskCheck = DateTimeHelper.dateTimeNow()
            self.repository.actuatorHealth.save(model)
        except Exception as exception:
            model = ActuatorHealth.ActuatorHealth(
                status = ActuatorHealthStatus.DOWN,
                laskCheck = DateTimeHelper.dateTimeNow()
            )
            log.error(self.getStatus, f'Api is {model.status}', exception)
        return self.converter.actuatorHealth.fromModelToResponseDto(model)
