from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.enumeration.SchedulerType import SchedulerType
from python_framework.api.src.service.flask import FlaskManager


@Function
def Scheduler(*schedulerArgs, disable=False, **schedulerKwargs) :
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
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SchedulerMethod(*methodArgs, requestClass=None, disable=False, **methodKwargs) :
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        resourceInstanceMethod.disabled = disable
        log.debug(SchedulerMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceInstanceMethod)
        methodName = ReflectionHelper.getName(resourceInstanceMethod)
        methodKwargs['id'] = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        instancesUpTo = methodKwargs.pop('instancesUpTo', 1)
        weekDays = methodKwargs.pop('weekDays', None)
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
            if resourceInstance.enabled or not resourceInstance.disabled or not resourceInstanceMethod.disabled:
                log.debug(resourceInstanceMethod, f'{shedulerId} scheduler started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceInstanceMethod(*args,**kwargs)
                except Exception as exception :
                    log.warning(innerResourceInstanceMethod, f'Not possible to run {shedulerId} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
                log.debug(resourceInstanceMethod, f'{shedulerId} scheduler finished')
                return methodReturn
            log.warning(resourceInstanceMethod, f'{shedulerId} scheduler didn{c.SINGLE_QUOTE}t started. {"Schedulers are disabled" if not resourceInstance.enabled else "This scheduler is disabled" if resourceInstance.disabled else "This scheduler method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper
