class ExceptionManager:
    def handleErrorLog(self, *args, **kwargs):
        ...

def addResource(apiInstance, appInstance) :
    apiInstance.resource.manager.exception = ExceptionManager()
    return apiInstance.resource.manager.exception

def initialize(apiInstance, appInstance) :
    ...

def onHttpRequestCompletion(apiInstance, appInstance) :
    ...

def onRun(apiInstance, appInstance):
    ...

def shutdown(apiInstance, appInstance):
    ...

def onShutdown(apiInstance, appInstance) :
    ...
