from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import ConverterStatic


DEFAUTL_MUTE_LOGS = True
DEFAUTL_DISABLE = False


@Function
def Listener(*listenerArgs, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **listenerKwargs) :
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Listener,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = self.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_ENABLE)
                self.disabled = disable
                self.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS), DEFAUTL_MUTE_LOGS)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ListenerMethod(*methodArgs, requestClass=None, managerMethodPath='manager.method', disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **methodKwargs) :
    resourceMethodDisable = disable
    resourceMethodMuteLogs = muteLogs
    def innerMethodWrapper(resourceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(ListenerMethod,f'''wrapping {resourceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceMethod)
        methodName = ReflectionHelper.getName(resourceMethod)
        resourceMethod.disabled = disable
        resourceMethod.listenerId = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        resourceMethod.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS), DEFAUTL_MUTE_LOGS)
        listenerArgs = [*methodArgs]
        listenerKwargs = {**methodKwargs}
        resourceInstanceName = methodClassName[:-len(FlaskManager.KW_LISTENER_RESOURCE)]
        resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        annotationMethod = ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, managerMethodPath)
        @annotationMethod(*listenerArgs, **listenerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            args = FlaskManager.getArgumentInFrontOfArgs(args, FlaskManager.getResourceSelf(apiInstance, FlaskManager.KW_LISTENER_RESOURCE, resourceInstanceName))
            resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceMethod.disabled:
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.listenerId} listener method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceMethod, f'Not possible to run {resourceMethod.listenerId} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseAndPersistGlobalException(exception, resourceInstance, resourceMethod)
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.listenerId} listener method finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceMethod, f'{resourceMethod.listenerId} listener method didn{c.SINGLE_QUOTE}t started. {"Handlers are disabled" if not resourceInstance.enabled else "This listener class is disabled" if resourceInstance.disabled else "This listener method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceMethod)
        innerResourceInstanceMethod.disable = resourceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceMethodMuteLogs
        return innerResourceInstanceMethod
    return innerMethodWrapper
