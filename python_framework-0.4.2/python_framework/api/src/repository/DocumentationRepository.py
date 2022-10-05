from python_helper import SettingHelper
from python_framework.api.src.service.openapi import OpenApiDocumentationFile
from python_framework.api.src.annotation.RepositoryAnnotation import Repository

@Repository()
class DocumentationRepository:

    def getSwaggerDocumentation(self):
        return OpenApiDocumentationFile.loadDocumentation(self.globals.api)

    def getActiveEnvironment(self):
        return SettingHelper.getActiveEnvironment()
