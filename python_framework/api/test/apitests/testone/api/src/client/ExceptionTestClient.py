from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.annotation.client.HttpClientAnnotation import HttpClient, HttpClientMethod
from python_framework.api.src.util import Serializer
from python_framework.api.src.dto import ActuatorHealthDto

import ClientTestDto


BASE_CONTROLLER_URL = f'/exception/test/{EnvironmentHelper.get("URL_VARIANT")}'


@HttpClient(url='http://localhost:5022/client-test-api')
class ExceptionTestClient:

    @HttpClientMethod(
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
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )

    @HttpClientMethod(
        url = f'{BASE_CONTROLLER_URL}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str, ClientTestDto.ClientTestRequestDto],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def postMethod(self, uri, dto, headers=None, params=None):
        return self.post(
            Serializer.getObjectAsDictionary(dto),
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )

    @HttpClientMethod(
        url = f'{BASE_CONTROLLER_URL}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str, ClientTestDto.ClientTestRequestDto],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def putMethod(self, uri, dto, headers=None, params=None):
        return self.put(
            Serializer.getObjectAsDictionary(dto),
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )

    @HttpClientMethod(
        url = f'{BASE_CONTROLLER_URL}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str, ClientTestDto.ClientTestRequestDto],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def patchMethod(self, uri, dto, headers=None, params=None):
        return self.patch(
            Serializer.getObjectAsDictionary(dto),
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )

    @HttpClientMethod(
        url = f'{BASE_CONTROLLER_URL}',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        requestClass = [str, ClientTestDto.ClientTestRequestDto],
        responseClass = [[ClientTestDto.ClientTestResponseDto]],
        logResponse = True,
        logRequest = True
    )
    def deleteMethod(self, uri, dto, headers=None, params=None):
        return self.delete(
            Serializer.getObjectAsDictionary(dto),
            aditionalUrl = uri,
            params = Serializer.getObjectAsDictionary(params),
            headers = {'Some-Cool-Header': 'cool-value', **Serializer.getObjectAsDictionary(headers)}
        )
