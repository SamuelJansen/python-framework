from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.annotation.ClientAnnotation import Client, ClientMethod
from python_framework.api.src.dto import ActuatorHealthDto

import EnumAsQueryDto

from dto import TestRequestDto

@Client(url='http://localhost:5010/local-test-api')
class SomeClient:

    @ClientMethod(
        url = f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}',
        requestHeaderClass = [TestRequestDto.TestRequestHeaderDto],
        requestParamClass = [TestRequestDto.TestRequestParamDto],
        requestClass = ActuatorHealthDto.ActuatorHealthResponseDto,
        responseClass = TestRequestDto.TestResponseDto,
        logResponse = True,
        logRequest = True
    )
    def getOnActuatorHealth(self, dto, headers=None, params=None):
        # print(dto.__dict__)
        # print(headers.__dict__)
        # print(params.__dict__)
        import requests
        from python_framework.api.src.util import Serializer
        response = requests.put(
            f'{self.url}{self.getOnActuatorHealth.url}',
            data = Serializer.jsonifyIt(dto),
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Content-Type': self.getOnActuatorHealth.consumes, **Serializer.getObjectAsDictionary(headers)}
        )
        # print(response.text)
        return TestRequestDto.TestResponseDto(
            status = Serializer.convertFromJsonToObject(response.json(), [[ActuatorHealthDto.ActuatorHealthResponseDto]])[0].status,
            first = params.first,
            second = params.second,
            firstHeader = headers.firstHeader,
            secondHeader = headers.secondHeader
        ), HttpStatus.map(response.status_code)
