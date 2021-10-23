from python_helper import EnvironmentHelper
from python_framework import Controller, ControllerMethod, HttpStatus

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
