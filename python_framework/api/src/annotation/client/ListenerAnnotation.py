from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.domain import HttpDomain


DEFAUTL_MUTE_LOGS = False
DEFAUTL_ENABLED = True


@Function
def Listener(*listenerArgs, manager=None, managerClient=None, enabled=DEFAUTL_ENABLED, muteLogs=DEFAUTL_MUTE_LOGS, **listenerKwargs) :
    listenerManager = manager
    listenerManagerClient = managerClient
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Listener,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.manager = listenerManager if not isinstance(listenerManager, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, listenerManager)
                self.managerClient = listenerManagerClient if not isinstance(listenerManagerClient, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, listenerManagerClient)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = enabled and self.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_ENABLE)
                self.muteLogs = muteLogs or StaticConverter.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ListenerMethod(
    *methodArgs,
    requestClass = None,
    interceptor = FlaskManager.defaultResourceInterceptor,
    enabled = DEFAUTL_ENABLED,
    muteLogs = DEFAUTL_MUTE_LOGS,
    muteStacktraceOnBusinessRuleException = True,
    **methodKwargs
):
    resourceInstanceMethodRequestClass = requestClass
    resourceInstanceMethodEnabled = enabled
    resourceInstanceMethodMuteLogs = muteLogs
    resourceInterceptor = interceptor
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException = muteStacktraceOnBusinessRuleException
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(ListenerMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceInstanceMethod)
        methodName = ReflectionHelper.getName(resourceInstanceMethod)
        resourceTypeIsEnabled = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_ENABLE)
        resourceInstanceMethod.enabled = resourceInstanceMethodEnabled and resourceTypeIsEnabled
        resourceInstanceMethod.id = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        resourceInstanceMethod.muteLogs = resourceInstanceMethodMuteLogs or StaticConverter.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceInstanceMethodMuteLogs)
        listenerArgs = [*methodArgs]
        listenerKwargs = {**methodKwargs}
        resourceInstanceName = methodClassName[:-len(FlaskManager.KW_LISTENER_RESOURCE)]
        resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        interceptor = resourceInterceptor if not isinstance(resourceInterceptor, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, resourceInterceptor)
        @interceptor(*listenerArgs, **listenerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstance = FlaskManager.getResourceSelf(apiInstance, FlaskManager.KW_LISTENER_RESOURCE, resourceInstanceName)
            args = FlaskManager.getArgumentInFrontOfArgs(args, resourceInstance) ###- resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceInstanceMethod.muteLogs
            if resourceInstance.enabled and resourceInstanceMethod.enabled:
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.LISTENER_CONTEXT.lower()} method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try:
                    try :
                        FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                        methodReturn = resourceInstanceMethod(*args,**kwargs)
                    except Exception as exception :
                        # if not muteLogs:
                        #     log.warning(resourceInstanceMethod, f'Not possible to run {resourceInstanceMethod.id} properly', exception=exception, muteStackTrace=True)
                        FlaskManager.raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod)
                except Exception as exception:
                    logErrorMessage = f'Error processing {resourceInstance.__class__.__name__}.{resourceInstanceMethod.__name__} {HttpDomain.LISTENER_CONTEXT.lower()}'
                    if HttpStatus.INTERNAL_SERVER_ERROR <= HttpStatus.map(exception.status):
                        log.error(resourceInstance.__class__, logErrorMessage, exception)
                    else :
                        log.failure(resourceInstance.__class__, logErrorMessage, exception=exception, muteStackTrace=resourceInstanceMethodMuteStacktraceOnBusinessRuleException)
                    raise exception
                if not muteLogs:
                    log.info(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.LISTENER_CONTEXT.lower()} method finished')
                return methodReturn
            else:
                if not muteLogs:
                    log.warning(resourceInstanceMethod, f'{resourceInstanceMethod.id} {HttpDomain.LISTENER_CONTEXT.lower()} method didn{c.SINGLE_QUOTE}t started. {"Listeners are disabled" if resourceTypeIsEnabled else f"This {HttpDomain.LISTENER_CONTEXT.lower()} class is disabled" if not resourceInstance.enabled else f"This {HttpDomain.LISTENER_CONTEXT.lower()} method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.id = resourceInstanceMethod.id
        innerResourceInstanceMethod.requestClass = resourceInstanceMethodRequestClass
        innerResourceInstanceMethod.enabled = resourceInstanceMethodEnabled
        innerResourceInstanceMethod.muteLogs = resourceInstanceMethodMuteLogs
        innerResourceInstanceMethod.interceptor = resourceInterceptor
        innerResourceInstanceMethod.muteStacktraceOnBusinessRuleException = resourceInstanceMethodMuteStacktraceOnBusinessRuleException
        return innerResourceInstanceMethod
    return innerMethodWrapper
