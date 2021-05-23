from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod

@Controller(url='/test-controller', tag='MyUrl', description='My url controller')
class MyController:

    @ControllerMethod(
        url = '/payload-validation-test',
        requestClass = [[dict]],
        responseClass = [dict],
        logRequest = True,
        logResponse = True,
        muteStacktraceOnBusinessRuleException = False
    )
    def post(self, requestBodyList):
        return requestBodyList, HttpStatus.OK

    @ControllerMethod(
        url = '/payload-validation-test',
        requestClass = [[dict]],
        responseClass = [dict],
        logRequest = True,
        logResponse = True
    )
    def patch(self, requestBodyList):
        return requestBodyList, HttpStatus.OK

    @ControllerMethod(
        url = '/all-fine-if-its-none',
        logRequest = True,
        logResponse = True
    )
    def get(self):
        return None, HttpStatus.OK

@Controller(url='/test-controller/batch', tag='MyUrl', description='My url controller')
class MyBatchController:

    @ControllerMethod(
        url = '/payload-validation-test',
        requestClass = [dict],
        responseClass = [[dict]],
        logRequest = True,
        logResponse = True
    )
    def post(self, requestBodyList):
        return requestBodyList  , HttpStatus.OK

    @ControllerMethod(
        url = '/payload-validation-test',
        requestClass = [dict],
        responseClass = [[dict]],
        logRequest = True,
        logResponse = True
    )
    def patch(self, requestBodyList):
        return requestBodyList, HttpStatus.OK

    @ControllerMethod(
        url = '/all-fine-if-its-none',
        logRequest = True,
        logResponse = True
    )
    def get(self):
        return [None], HttpStatus.OK
