from python_framework.api.src.annotation.ServiceAnnotation import Service, ServiceMethod

@Service()
class DocumentationService:

    @ServiceMethod()
    def getSwaggerDocumentation(self):
        return self.repository.documentation.getSwaggerDocumentation()

    @ServiceMethod()
    def getActiveEnvironment(self):
        return {
            'active': self.repository.documentation.getActiveEnvironment()
        }
