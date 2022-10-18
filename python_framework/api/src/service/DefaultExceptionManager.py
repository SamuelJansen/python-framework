from python_helper import ReflectionHelper, log
from python_framework.api.src.model import ErrorLog

class ExceptionManager:
    def handleErrorLog(self, httpErrorLog, *args, **kwargs):
        try:
            self.api.repository.commit()
        except Exception as firstPreCommitException:
            log.warning(handleLogErrorException, f'Failed to pre commit before persist {ReflectionHelper.getName(httpErrorLog)}. Going for a second attempt', exception=firstPreCommitException, muteStackTrace=True)
            try:
                self.api.repository.flush()
                self.api.repository.commit()
            except Exception as secondPreCommitException:
                log.warning(handleLogErrorException, f'Failed to pre commit before persist {ReflectionHelper.getName(httpErrorLog)}. Going for a third attempt', exception=secondPreCommitException, muteStackTrace=True)
                try:
                    self.api.repository.rollback()
                    self.api.repository.flush()
                    self.api.repository.commit()
                except Exception as thirdPreCommitException:
                    log.warning(handleLogErrorException, f'Failed to pre commit before persist {ReflectionHelper.getName(httpErrorLog)}', exception=thirdPreCommitException)
        httpErrorLog.reload()
        self.api.repository.saveAndCommit(httpErrorLog)

def addResource(apiInstance, appInstance) :
    apiInstance.resource.manager.exception = ExceptionManager()
    apiInstance.resource.manager.exception.api = apiInstance
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
