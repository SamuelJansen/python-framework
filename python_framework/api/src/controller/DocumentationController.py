from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod

@Controller(url='/doc', tag='Documentation', description='OpenApi documentation')
class DocumentationController:

    @ControllerMethod(responseClass=dict)
    def get(self):
        return self.service.documentation.getSwaggerDocumentation(), HttpStatus.OK

@Controller(url='/environment', tag='Documentation', description='Api Tree')
class DocumentationBatchController:

    @ControllerMethod(url='/environment', responseClass=dict)
    def get(self):
        return self.service.documentation.getActiveEnvironment(), HttpStatus.OK
