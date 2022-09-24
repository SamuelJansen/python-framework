from python_helper import ObjectHelper
from python_framework.api.src.annotation.RepositoryAnnotation import Repository
from python_framework.api.src.model import ActuatorHealth

@Repository(model = ActuatorHealth.ActuatorHealth)
class ActuatorHealthTestRepository:

    def findAllByStatus(self, status) :
        return self.repository.findByStatusAndCommit(status)
