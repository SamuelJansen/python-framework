from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function
from python_framework.api.src.service.flask import FlaskManager

@Function
def Scheduler() :
    def Wrapper(OuterClass, *args, **kwargs):
        log.debug(Scheduler,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.debug(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def SchedulerMethod(*methodArgs, requestClass=None, **methodKwargs) :
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.debug(SchedulerMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        methodClassName = ReflectionHelper.getMethodClassName(resourceInstanceMethod)
        methodName = ReflectionHelper.getName(resourceInstanceMethod)
        methodKwargs['id'] = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        instancesUpTo = methodKwargs.pop('instancesUpTo', 1)
        weekDays = methodKwargs.pop('weekDays', None)
        methodKwargs['max_instances'] = instancesUpTo
        methodKwargs['day_of_week'] = weekDays
        shedulerArgs = [*methodArgs]
        shedulerArgs = {**methodKwargs}
        apiInstance = resourceInstanceMethod.__self__.globals.api
        @apiInstance.scheduler.task(*shedulerArgs, **shedulerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            args = FlaskManager.getArgumentInFrontOfArgs(args, ReflectionHelper.getAttributeOrMethod(apiInstance.resource.scheduler, methodClassName[:-len('Scheduler')].lower()))
            resourceInstance = args[0]
            methodReturn = None
            try :
                FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                FlaskManager.raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
                log.log(innerResourceInstanceMethod, f'Not possible to run {shedulerId} properly', exception=exception)
            return methodReturn
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper
