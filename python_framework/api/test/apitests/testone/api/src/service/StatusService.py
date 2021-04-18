from python_framework.api.src.service.flask.FlaskManager import Service, ServiceMethod

import EnumAsQueryDto

@Service()
class StatusService :

    @ServiceMethod(requestClass=[EnumAsQueryDto.EnumAsQueryRequestDto])
    def findAllByStatus(self, dto):
        modelList = self.repository.actuatorHealthTest.findAllByStatus(dto.status)
        return self.converter.actuatorHealthTest.fromModelListToResponseDtoList(modelList)
