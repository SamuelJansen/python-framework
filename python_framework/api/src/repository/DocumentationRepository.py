from python_framework import Repository, OpenApiDocumentationFile

@Repository()
class DocumentationRepository:

    def getSwaggerDocumentation(self):
        return OpenApiDocumentationFile.loadDocumentation(self.globals.api)

    def getActiveEnvironment(self):
        return EnvironmentHelper.getAcvtiveEnvironment()
