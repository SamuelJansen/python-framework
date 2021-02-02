import datetime
from python_helper import ObjectHelper, log
from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus
from python_framework.api.src.model import ActuatorHealth
from python_framework.api.src.service.flask.FlaskManager import Service, ServiceMethod

@Service()
class ActuatorHealthService:

    @ServiceMethod()
    def getStatus(self):
        actuatorHealthList = self.repository.actuatorHealth.findAll()
        if ObjectHelper.isList(actuatorHealthList) and 1 == len(actuatorHealthList) :
            model = actuatorHealthList[0]
        else :
            try :
                model = self.repository.actuatorHealth.save(ActuatorHealth.ActuatorHealth(status=ActuatorHealthStatus.UP))
            except Exception as exception :
                log.error(self.getStatus, 'Api cannot reach database', exception)
                model = ActuatorHealth.ActuatorHealth()
        model.laskCheck = datetime.datetime.utcnow()
        self.repository.actuatorHealth.save(model)
        return self.converter.actuatorHealth.fromModelToResponseDto(model)
