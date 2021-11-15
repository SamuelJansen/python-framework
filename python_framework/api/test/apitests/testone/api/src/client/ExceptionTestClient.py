from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.annotation.ClientAnnotation import Client, ClientMethod
from python_framework.api.src.util import Serializer
from python_framework.api.src.dto import ActuatorHealthDto

import ClientTestDto


BASE_CONTROLLER_URL = f'/exception/test/{EnvironmentHelper.get("URL_VARIANT")}'


@Client(url='http://localhost:5022/client-test-api')
class ExceptionTestClient:

    @ClientMethod(
        url = f'{BASE_CONTROLLER_URL}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def getMethod(self, uri, headers=None, params=None):
        return self.get(
            self.getMethod,
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )
