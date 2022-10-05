from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod
import TestCallDto

@Controller(url = '/call', tag='Call', description='Call controller')
class TestCallController:

    @ControllerMethod(
        requestClass = TestCallDto.TestCallRequestDto,
        responseClass = TestCallDto.TestCallRequestDto
    )
    def post(self, dto):
        return dto, HttpStatus.OK

@Controller(url = '/call/batch', tag='Call', description='Call controller')
class TestCallBatchController:

    @ControllerMethod(
        requestClass = [[TestCallDto.TestCallRequestDto]],
        responseClass = [[TestCallDto.TestCallRequestDto]]
    )
    def post(self, dtoList):
        return dtoList, HttpStatus.OK
