from python_framework.api.src.annotation.ServiceAnnotation import Service, ServiceMethod

import EnumAsQueryDto

@Service()
class StatusService :

    @ServiceMethod(requestClass=[EnumAsQueryDto.EnumAsQueryRequestDto])
    def findAllByStatus(self, dto):
        if dto.status is None:
            raise Exception(f'do Enum still remains as enum? --> dto.status: {dto.status}')
        modelList = self.repository.actuatorHealthTest.findAllByStatus(dto.status)
        return self.converter.actuatorHealthTest.fromModelListToResponseDtoList(modelList), {
            'added': 'header',
            'booleanFalse': False,
            'booleanTrue': True,
            'int': 1,
            'otherInt': -34,
            'float': 1.0,
            'otherFloat': 2.3334
        }
