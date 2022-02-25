from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import ConverterStatic


DEFAUTL_MUTE_LOGS = False
DEFAUTL_DISABLE = False


@Function
def Emitter(*emitterArgs, manager=None, managerClient=None, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **emitterKwargs) :
    emitterManager = manager
    emitterManagerClient = managerClient
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Emitter,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.manager = emitterManager if not isinstance(emitterManager, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, emitterManager)
                self.managerClient = emitterManagerClient if not isinstance(emitterManagerClient, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, emitterManagerClient)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = self.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_ENABLE)
                self.disabled = disable
                self.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def EmitterMethod(
    *methodArgs,
    requestClass = None,
    interceptor = FlaskManager.defaultResourceInterceptor,
    disable = DEFAUTL_DISABLE,
    muteLogs = DEFAUTL_MUTE_LOGS,
    **methodKwargs
):
    resourceMethodDisable = disable
    resourceMethodMuteLogs = muteLogs
    resourceInterceptor = interceptor
    def innerMethodWrapper(resourceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(EmitterMethod,f'''wrapping {resourceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceMethod)
        methodName = ReflectionHelper.getName(resourceMethod)
        resourceMethod.disabled = disable
        resourceMethod.id = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        resourceMethod.muteLogs = resourceMethodMuteLogs or ConverterStatic.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceMethodMuteLogs)
        emitterArgs = [*methodArgs]
        emitterKwargs = {**methodKwargs}
        resourceInstanceName = methodClassName[:-len(FlaskManager.KW_EMITTER_RESOURCE)]
        resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        interceptor = resourceInterceptor if not isinstance(resourceInterceptor, str) else  ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, resourceInterceptor)
        @interceptor(*emitterArgs, **emitterKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstance = FlaskManager.getResourceSelf(apiInstance, FlaskManager.KW_EMITTER_RESOURCE, resourceInstanceName)
            args = FlaskManager.getArgumentInFrontOfArgs(args, resourceInstance) ###- resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceMethod.disabled:
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} emitter method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceMethod, f'Not possible to run {resourceMethod.id} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseAndPersistGlobalException(exception, resourceInstance, resourceMethod)
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} emitter method finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceMethod, f'{resourceMethod.id} emitter method didn{c.SINGLE_QUOTE}t started. {"Handlers are disabled" if not resourceInstance.enabled else "This emitter class is disabled" if resourceInstance.disabled else "This emitter method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceMethod)
        innerResourceInstanceMethod.disable = resourceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceMethodMuteLogs
        innerResourceInstanceMethod.interceptor = resourceInterceptor
        return innerResourceInstanceMethod
    return innerMethodWrapper
