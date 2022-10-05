from python_helper import EnvironmentHelper, ReflectionHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod, getCompleteResponseByException
from python_framework.api.src.annotation.EnumAnnotation import EnumItem, EnumItemStr
from python_framework.api.src.dto import ActuatorHealthDto
from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus
from python_framework.api.src.model import ActuatorHealth

from dto import EnumAsQueryDto

from dto import TestRequestDto

@Controller(url='/test/actuator/health', tag='HealthCheckTest', description='HealthCheck controller test')
class ActuatorHealthTestController:

    @ControllerMethod(
        requestClass = EnumAsQueryDto.EnumAsQueryRequestDto,
        responseClass = [[ActuatorHealthDto.ActuatorHealthResponseDto]],
        logResponse = True
    )
    def post(self, dto):
        return self.service.status.findAllByStatus(dto), HttpStatus.OK

    @ControllerMethod(
        requestClass = EnumAsQueryDto.EnumAsQueryRequestDto,
        responseClass = [[ActuatorHealthDto.ActuatorHealthResponseDto]],
        logResponse = True
    )
    def patch(self, dto):
        someModel = ActuatorHealth.ActuatorHealth(status='UP')
        assert EnumItemStr == type(someModel.status), f'{EnumItemStr} == {type(someModel.status)}'
        model = ActuatorHealth.ActuatorHealth(status=ActuatorHealthStatus.UP)
        assert EnumItemStr == type(model.status), f'{EnumItemStr} == {type(model.status)}'
        modelList = self.service.status.globals.api.resource.repository.actuatorHealthTest.findAllByStatus(EnumAsQueryDto.EnumAsQueryRequestDto(status=model.status).status)
        assert EnumItemStr == type(modelList[0].status), f'{EnumItemStr} == {type(modelList[0].status)}'
        ###- ReflectionHelper.getItNaked(self.service.status.globals.api.resource.repository.actuatorHealthTest.repository.session)
        try:
            myReturn = self.service.status.findAllByStatus(dto), HttpStatus.OK
        except Exception as exception:
            ignoredResponse = getCompleteResponseByException(exception, self, self.patch, False)
        ###- ReflectionHelper.getItNaked(self.service.status.globals.api.resource.repository.actuatorHealthTest.repository.session)
        assert EnumItemStr == type(someModel.status), f'{EnumItemStr} == {type(someModel.status)}'
        assert EnumItemStr == type(model.status), f'{EnumItemStr} == {type(model.status)}'
        assert EnumItemStr == type(modelList[0].status), f'{EnumItemStr} == {type(modelList[0].status)}'
        return self.service.status.globals.api.resource.converter.actuatorHealthTest.fromModelListToResponseDtoList(modelList), HttpStatus.OK

    @ControllerMethod(
        url=f'/{EnvironmentHelper.get("URL_VARIANT")}',
        logRequest = True,
        requestHeaderClass = [TestRequestDto.TestRequestHeaderDto],
        requestParamClass = [TestRequestDto.TestRequestParamDto],
        requestClass = ActuatorHealthDto.ActuatorHealthResponseDto,
        responseClass = [[ActuatorHealthDto.ActuatorHealthResponseDto]],
        logResponse = True
    )
    def put(self, dto, headers=None, params=None):
        # from flask import request
        # print(f'{self.__class__.__name__}.put -> request.headers: {request.headers}')
        # print(f'headers.firstHeader: {headers.firstHeader}')
        # print(f'headers.secondHeader: {headers.secondHeader}')
        # print(f'params.first: {params.first}')
        # print(f'params.second: {params.second}')
        return [dto], HttpStatus.OK

    @ControllerMethod(
        url = f'/{EnvironmentHelper.get("URL_VARIANT")}/<string:status>/<string:secondStatus>',
        requestHeaderClass = [TestRequestDto.TestRequestHeaderDto],
        requestParamClass = [TestRequestDto.TestRequestParamDto],
        responseClass = [TestRequestDto.TestResponseDto],
        logResponse = True
    )
    def get(self, status=None, secondStatus=None, headers=None, params=None):
        return self.globals.api.resource.client.some.getOnActuatorHealth(
            ActuatorHealthDto.ActuatorHealthResponseDto(status+secondStatus),
            headers=headers,
            params=params
        ), HttpStatus.OK
