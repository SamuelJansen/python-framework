from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.enumeration.SchedulerType import SchedulerType
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import ConverterStatic


DEFAUTL_MUTE_LOGS = False
DEFAUTL_DISABLE = False


@Function
def Scheduler(*schedulerArgs, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **schedulerKwargs) :
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Scheduler,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = self.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_ENABLE)
                self.disabled = disable
                self.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SchedulerMethod(*methodArgs, requestClass=None, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **methodKwargs) :
    resourceMethodDisable = disable
    resourceMethodMuteLogs = muteLogs
    def innerMethodWrapper(resourceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(SchedulerMethod,f'''wrapping {resourceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceMethod)
        methodName = ReflectionHelper.getName(resourceMethod)
        methodKwargs['id'] = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        instancesUpTo = methodKwargs.pop('instancesUpTo', 1)
        weekDays = methodKwargs.pop('weekDays', None)
        resourceMethod.disabled = disable
        resourceMethod.id = methodKwargs['id']
        resourceMethod.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceMethodMuteLogs)
        if ObjectHelper.isNotEmpty(methodArgs) and SchedulerType.CRON == methodArgs[0] and ObjectHelper.isNotNone(weekDays) and StringHelper.isNotBlank(weekDays) :
            methodKwargs['day_of_week'] = weekDays
        if ObjectHelper.isNotNone(instancesUpTo) :
            methodKwargs['max_instances'] = instancesUpTo
        shedulerArgs = [*methodArgs]
        shedulerKwargs = {**methodKwargs}
        @apiInstance.schedulerManager.task(*shedulerArgs, **shedulerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstanceName = methodClassName[:-len(FlaskManager.KW_SCHEDULER_RESOURCE)]
            resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
            args = FlaskManager.getArgumentInFrontOfArgs(args, ReflectionHelper.getAttributeOrMethod(apiInstance.resource.scheduler, resourceInstanceName))
            resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceMethod.disabled:
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} scheduler method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceMethod, f'Not possible to run {resourceMethod.id} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseAndPersistGlobalException(exception, resourceInstance, resourceMethod)
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} scheduler method finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceMethod, f'{resourceMethod.id} scheduler didn{c.SINGLE_QUOTE}t started. {"Schedulers are disabled" if not resourceInstance.enabled else "This scheduler is disabled" if resourceInstance.disabled else "This scheduler method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceMethod)
        resourceMethod.id = methodKwargs.get('id')
        innerResourceInstanceMethod.disable = resourceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceMethodMuteLogs
        return innerResourceInstanceMethod
    return innerMethodWrapper
