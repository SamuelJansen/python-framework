from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.util import Serializer
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod

import ClientTestDto


BASE_CONTROLLER_URL = f'/test/{EnvironmentHelper.get("URL_VARIANT")}'


@Controller(url=f'{BASE_CONTROLLER_URL}/<string:urlParam>/<string:otherUrlParam>', tag='ClientTestController', description='Client Controller test')
class ClientTestController:

    @ControllerMethod(
        url = f'/get',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        responseClass = ClientTestDto.ClientTestResponseDto,
        logRequest = True,
        logResponse = True
    )
    def get(self, urlParam=None, otherUrlParam=None, params=None, headers=None):
        return self.globals.api.resource.client.test.getMethod(
            f'{BASE_CONTROLLER_URL}/{urlParam}/{otherUrlParam}/get/all',
            headers = headers,
            params = params
        ), {'get': 'headers'}, HttpStatus.OK


@Controller(url=f'{BASE_CONTROLLER_URL}', tag='ClientTestController', description='Client Controller test')
class ClientTestBatchController:

    @ControllerMethod(
        url = f'/<string:urlParam>/<string:otherUrlParam>/get/all',
        requestHeaderClass = [ClientTestDto.ClientTestRequestHeaderDto],
        requestParamClass = [ClientTestDto.ClientTestRequestParamDto],
        responseClass = ClientTestDto.ClientTestResponseDto,
        logRequest = True,
        logResponse = True
    )
    def get(self, urlParam=None, otherUrlParam=None, params=None, headers=None):
        return ClientTestDto.ClientTestResponseDto(
            someBody = urlParam + otherUrlParam,
            someOtherBody = {**Serializer.getObjectAsDictionary(headers), **Serializer.getObjectAsDictionary(params)}
        ), {'getAll': 'headers'}, HttpStatus.OK
