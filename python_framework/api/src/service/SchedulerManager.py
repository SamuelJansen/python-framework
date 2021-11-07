from python_helper import Constant as c
from python_helper import EnvironmentHelper, log
from flask_apscheduler import APScheduler
from python_framework.api.src.constant import ConfigurationKeyConstant, SchedulerConstant
from python_framework.api.src.converter.static import ConverterStatic


def addResource(apiInstance, appInstance) :
    scheduler = APScheduler()
    globals = apiInstance.globals
    scheduler.api_enabled = globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_ENABLE) is True
    scheduler.timezone = ConverterStatic.getValueOrDefault(
        globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_TIMEZONE),
        SchedulerConstant.DEFAULT_TIMEZONE
    ) ###- guess
    scheduler.zone = scheduler.timezone ###- guess
    appInstance.config[SchedulerConstant.KW_SCHEDULER_API_ENABLED] = scheduler.api_enabled
    appInstance.config[SchedulerConstant.KW_SCHEDULER_TIMEZONE] = scheduler.timezone

    apiInstance.schedulerManager = scheduler
    log.success(addResource, f'APScheduler schedulers created{"" if apiInstance.schedulerManager.api_enabled else ". But are disabled"}')
    return scheduler

def initialize(apiInstance, appInstance) :
    apiInstance.schedulerManager.init_app(appInstance)
    apiInstance.schedulerManager.start()
    log.success(initialize, f'APScheduler schedulers initialized{"" if apiInstance.schedulerManager.api_enabled else ". But are disabled"}')

def onShutdown(apiInstance, appInstance) :
    @appInstance.teardown_appcontext
    def closeAPSchedulerSchedulers(error):
        apiInstance.schedulerManager.shutdown(wait=False)
        log.success(closeAPSchedulerSchedulers, 'APScheduler schedulers successfully closed')
    import atexit
    atexit.register(lambda: apiInstance.schedulerManager.shutdown(wait=False))
