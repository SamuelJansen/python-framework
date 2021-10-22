from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.enumeration.SchedulerType import SchedulerType
from python_framework.api.src.service.flask import FlaskManager


@Function
def Scheduler(*schedulerArgs, disable=False, muteLogs=False, **schedulerKwargs) :
    def Wrapper(OuterClass, *args, **kwargs):
        log.debug(Scheduler,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = self.globals.getApiSetting('api.scheduler.enable')
                self.disabled = disable
                self.muteLogs = muteLogs
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SchedulerMethod(*methodArgs, requestClass=None, disable=False, muteLogs=False, **methodKwargs) :
    resourceMethodDisable = disable
    resourceMethodMuteLogs = muteLogs
    def innerMethodWrapper(resourceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.debug(SchedulerMethod,f'''wrapping {resourceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceMethod)
        methodName = ReflectionHelper.getName(resourceMethod)
        methodKwargs['id'] = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        instancesUpTo = methodKwargs.pop('instancesUpTo', 1)
        weekDays = methodKwargs.pop('weekDays', None)
        resourceMethod.disabled = disable
        resourceMethod.shedulerId = methodKwargs['id']
        resourceMethod.muteLogs = muteLogs
        if ObjectHelper.isNotEmpty(methodArgs) and SchedulerType.CRON == methodArgs[0] and ObjectHelper.isNotNone(weekDays) and StringHelper.isNotBlank(weekDays) :
            methodKwargs['day_of_week'] = weekDays
        if ObjectHelper.isNotNone(instancesUpTo) :
            methodKwargs['max_instances'] = instancesUpTo
        shedulerArgs = [*methodArgs]
        shedulerKwargs = {**methodKwargs}
        @apiInstance.scheduler.task(*shedulerArgs, **shedulerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstanceName = methodClassName[:-len(FlaskManager.KW_SCHEDULER_RESOURCE)]
            resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
            args = FlaskManager.getArgumentInFrontOfArgs(args, ReflectionHelper.getAttributeOrMethod(apiInstance.resource.scheduler, resourceInstanceName))
            resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceMethod.disabled:
                if not muteLogs:
                    log.debug(resourceMethod, f'{resourceMethod.shedulerId} scheduler started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceMethod, f'Not possible to run {resourceMethod.shedulerId} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseGlobalException(exception, resourceInstance, resourceMethod)
                if not muteLogs:
                    log.debug(resourceMethod, f'{resourceMethod.shedulerId} scheduler finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceMethod, f'{resourceMethod.shedulerId} scheduler didn{c.SINGLE_QUOTE}t started. {"Schedulers are disabled" if not resourceInstance.enabled else "This scheduler is disabled" if resourceInstance.disabled else "This scheduler method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceMethod)
        resourceMethod.shedulerId = methodKwargs.get('id')
        innerResourceInstanceMethod.disable = resourceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceMethodMuteLogs
        return innerResourceInstanceMethod
    return innerMethodWrapper
