from python_framework.api.src.service.flask.FlaskManager import Repository
from python_framework.api.src.model import ActuatorHealth

@Repository(model = ActuatorHealth.ActuatorHealth)
class ActuatorHealthRepository:

    def save(self,model) :
        return self.repository.saveAndCommit(model)

    def findAll(self) :
        return self.repository.findAll(self.model)
