from python_helper import ObjectHelper
from python_framework.api.src.annotation.RepositoryAnnotation import Repository
from python_framework.api.src.model import ActuatorHealth

@Repository(model = ActuatorHealth.ActuatorHealth)
class ActuatorHealthTestRepository:

    def findAllByStatus(self, status) :
        modelList = []
        if ObjectHelper.isNotNone(status) :
            modelList = self.repository.session.query(self.model).filter(self.model.status == status).all()
        self.repository.session.commit()
        return modelList
