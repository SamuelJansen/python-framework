from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod

@Controller(url='/my', tag='MyUrl', description='My url controller')
class MyController:

    @ControllerMethod(
        url = '/url',
        requestClass = [[dict]],
        responseClass = [dict],
        logRequest = True,
        logResponse = True
    )
    def post(self, requestBodyList):
        return requestBodyList[0], HttpStatus.OK

    @ControllerMethod(
        url = '/other-url',
        logRequest = True,
        logResponse = True
    )
    def get(self):
        return None, HttpStatus.OK
