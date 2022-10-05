from python_helper import Constant as c
from python_helper import EnvironmentHelper, log, ObjectHelper
from flask_apscheduler import APScheduler
from python_framework.api.src.constant import ConfigurationKeyConstant, SchedulerConstant
from python_framework.api.src.converter.static import StaticConverter


def addResource(apiInstance, appInstance) :
    scheduler = APScheduler()
    globals = apiInstance.globals
    scheduler.api_enabled = globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_ENABLE) is True
    scheduler.timezone = StaticConverter.getValueOrDefault(
        globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_TIMEZONE),
        SchedulerConstant.DEFAULT_TIMEZONE
    ) ###- guess
    scheduler.zone = scheduler.timezone ###- guess
    appInstance.config[SchedulerConstant.KW_SCHEDULER_API_ENABLED] = scheduler.api_enabled
    appInstance.config[SchedulerConstant.KW_SCHEDULER_TIMEZONE] = scheduler.timezone

    apiInstance.resource.manager.scheduler = scheduler
    if ObjectHelper.isNotNone(apiInstance.resource.manager.scheduler):
        log.status(addResource, f'APScheduler schedulers created{"" if apiInstance.resource.manager.scheduler.api_enabled else ". But are disabled"}')
    return scheduler

def initialize(apiInstance, appInstance) :
    apiInstance.resource.manager.scheduler.init_app(appInstance)
    apiInstance.resource.manager.scheduler.start()
    if apiInstance.resource.manager.scheduler.api_enabled:
        log.success(initialize, f'APScheduler scheduler is running')
    else:
        log.status(initialize, f'APScheduler scheduler successfull initialized, but is disabled to run')

def onHttpRequestCompletion(apiInstance, appInstance) :
    ...

def onRun(apiInstance, appInstance):
    ...

def shutdown(apiInstance, appInstance):
    try:
        apiInstance.resource.manager.scheduler.shutdown(wait=False)
    except Exception as exception:
        log.failure(shutdown, 'Not possible to close APScheduler schedulers properly', exception)
        return
    log.success(shutdown, 'APScheduler schedulers successfully closed')

def onShutdown(apiInstance, appInstance) :
    import atexit
    atexit.register(lambda: shutdown(apiInstance, appInstance))
