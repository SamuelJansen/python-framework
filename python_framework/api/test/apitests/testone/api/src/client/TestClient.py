from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.annotation.ClientAnnotation import Client, ClientMethod
from python_framework.api.src.util import Serializer
from python_framework.api.src.dto import ActuatorHealthDto

import ClientTestDto


@Client(url='http://localhost:5022/client-test-api')
class TestClient:

    @ClientMethod(
        # url = f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def getMethod(self, url, headers=None, params=None):
        return self.get(
            self.getMethod,
            f'{self.url}{url}',
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Content-Type': self.getMethod.consumes, **Serializer.getObjectAsDictionary(headers)}
        )
