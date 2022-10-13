from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.domain import HttpDomain


DEFAUTL_MUTE_LOGS = False
DEFAUTL_ENABLED = True


@Function
def Emitter(*emitterArgs, manager=None, managerClient=None, enabled=DEFAUTL_ENABLED, muteLogs=DEFAUTL_MUTE_LOGS, **emitterKwargs) :
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
                self.enabled = enabled and self.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_ENABLE)
                self.muteLogs = muteLogs or StaticConverter.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def EmitterMethod(
    *methodArgs,
    requestClass = None,
    interceptor = FlaskManager.defaultResourceInterceptor,
    enabled = DEFAUTL_ENABLED,
    muteLogs = DEFAUTL_MUTE_LOGS,
    **methodKwargs
):
    resourceInstanceMethodRequestClass = requestClass
    resourceInstanceMethodEnabled = enabled
    resourceInstanceMethodMuteLogs = muteLogs
    resourceInterceptor = interceptor
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(EmitterMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceInstanceMethod)
        methodName = ReflectionHelper.getName(resourceInstanceMethod)
        resourceTypeIsEnabled = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_ENABLE)
        resourceInstanceMethod.enabled = resourceInstanceMethodEnabled and resourceTypeIsEnabled
        resourceInstanceMethod.id = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        resourceInstanceMethod.muteLogs = resourceInstanceMethodMuteLogs or StaticConverter.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceInstanceMethodMuteLogs)
        emitterArgs = [*methodArgs]
        emitterKwargs = {**methodKwargs}
        resourceInstanceName = methodClassName[:-len(FlaskManager.KW_EMITTER_RESOURCE)]
        resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        interceptor = resourceInterceptor if not isinstance(resourceInterceptor, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, resourceInterceptor)
        @interceptor(*emitterArgs, **emitterKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstance = FlaskManager.getResourceSelf(apiInstance, FlaskManager.KW_EMITTER_RESOURCE, resourceInstanceName)
            args = FlaskManager.getArgumentInFrontOfArgs(args, resourceInstance) ###- resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceInstanceMethod.muteLogs
            if resourceInstance.enabled and resourceInstanceMethod.enabled:
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.EMITTER_CONTEXT.lower()} method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceInstanceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceInstanceMethod, f'Not possible to run {resourceInstanceMethod.id} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=HttpDomain.EMITTER_CONTEXT)
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.EMITTER_CONTEXT.lower()} method finished')
                return methodReturn
            else:
                if not muteLogs:
                    log.warning(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.EMITTER_CONTEXT.lower()} method didn{c.SINGLE_QUOTE}t started. {"Handlers are disabled" if resourceTypeIsEnabled else f"This {HttpDomain.EMITTER_CONTEXT.lower()} class is disabled" if not resourceInstance.enabled else f"This {HttpDomain.EMITTER_CONTEXT.lower()} method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.id = resourceInstanceMethod.id
        innerResourceInstanceMethod.requestClass = resourceInstanceMethodRequestClass
        innerResourceInstanceMethod.enabled = resourceInstanceMethodEnabled
        innerResourceInstanceMethod.muteLogs = resourceInstanceMethodMuteLogs
        innerResourceInstanceMethod.interceptor = resourceInterceptor
        return innerResourceInstanceMethod
    return innerMethodWrapper
