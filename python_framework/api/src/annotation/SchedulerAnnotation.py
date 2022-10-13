from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.enumeration.SchedulerType import SchedulerType
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.domain import HttpDomain


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
                self.muteLogs = muteLogs or StaticConverter.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SchedulerMethod(
    *methodArgs,
    requestClass = None,
    disable = DEFAUTL_DISABLE,
    muteLogs = DEFAUTL_MUTE_LOGS,
    muteStacktraceOnBusinessRuleException = True,
    **methodKwargs
):
    resourceInstanceMethodRequestClass = requestClass
    resourceInstanceMethodDisable = disable
    resourceInstanceMethodMuteLogs = muteLogs
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException = muteStacktraceOnBusinessRuleException
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(SchedulerMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceInstanceMethod)
        methodName = ReflectionHelper.getName(resourceInstanceMethod)
        methodKwargs['id'] = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        instancesUpTo = methodKwargs.pop('instancesUpTo', 1)
        weekDays = methodKwargs.pop('weekDays', None)
        toleranceTime = methodKwargs.pop('toleranceTime', None)
        resourceInstanceMethod.disabled = disable
        resourceInstanceMethod.id = methodKwargs['id']
        resourceInstanceMethod.muteLogs = muteLogs or StaticConverter.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SCHEDULER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceInstanceMethodMuteLogs)
        if ObjectHelper.isNotEmpty(methodArgs) and SchedulerType.CRON == methodArgs[0] and ObjectHelper.isNotNone(weekDays) and StringHelper.isNotBlank(weekDays) :
            methodKwargs['day_of_week'] = weekDays
        if ObjectHelper.isNotNone(instancesUpTo) :
            methodKwargs['max_instances'] = instancesUpTo
        if ObjectHelper.isNotNone(toleranceTime):
            methodKwargs['misfire_grace_time'] = toleranceTime
        schedulerArgs = [*methodArgs]
        schedulerKwargs = {**methodKwargs}
        @apiInstance.resource.manager.scheduler.task(*schedulerArgs, **schedulerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstanceName = methodClassName[:-len(FlaskManager.KW_SCHEDULER_RESOURCE)]
            resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
            args = FlaskManager.getArgumentInFrontOfArgs(args, ReflectionHelper.getAttributeOrMethod(apiInstance.resource.scheduler, resourceInstanceName))
            resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceInstanceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceInstanceMethod.disabled:
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.SCHEDULER_CONTEXT.lower()} method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try:
                    try :
                        FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                        methodReturn = resourceInstanceMethod(*args,**kwargs)
                    except Exception as exception:
                        FlaskManager.raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=HttpDomain.SCHEDULER_CONTEXT)
                except Exception as exception:
                    logErrorMessage = f'Error processing {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__name__} {HttpDomain.SCHEDULER_CONTEXT.lower()}'
                    if HttpStatus.INTERNAL_SERVER_ERROR <= HttpStatus.map(exception.status):
                        log.error(resourceInstance.__class__, logErrorMessage, exception)
                    else :
                        log.failure(resourceInstance.__class__, logErrorMessage, exception=exception, muteStackTrace=resourceInstanceMethodMuteStacktraceOnBusinessRuleException)
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.SCHEDULER_CONTEXT.lower()} method finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceInstanceMethod, f'''{resourceInstanceMethod.id} {HttpDomain.SCHEDULER_CONTEXT.lower()} didn{c.SINGLE_QUOTE}t started. {"Schedulers are disabled" if not resourceInstance.enabled else f"This {HttpDomain.SCHEDULER_CONTEXT.lower()} is disabled" if resourceInstance.disabled else f"This {HttpDomain.SCHEDULER_CONTEXT.lower()} method is disabled"}''')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.id = methodKwargs.get('id')
        innerResourceInstanceMethod.requestClass = resourceInstanceMethodRequestClass
        innerResourceInstanceMethod.disable = resourceInstanceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceInstanceMethodMuteLogs
        innerResourceInstanceMethod.muteStacktraceOnBusinessRuleException = resourceInstanceMethodMuteStacktraceOnBusinessRuleException
        return innerResourceInstanceMethod
    return innerMethodWrapper
