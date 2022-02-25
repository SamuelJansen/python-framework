from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.converter.static import ConverterStatic


DEFAUTL_MUTE_LOGS = False
DEFAUTL_DISABLE = False


@Function
def Producer(*producerArgs, manager=None, managerClient=None, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **producerKwargs) :
    producerManager = manager
    producerManagerClient = managerClient
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Producer,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.manager = producerManager if not isinstance(producerManager, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, producerManager)
                self.managerClient = producerManagerClient if not isinstance(producerManagerClient, str) else ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, producerManagerClient)
                self.globals = apiInstance.globals
                self.service = apiInstance.resource.service
                self.enabled = self.globals.getApiSetting(ConfigurationKeyConstant.API_PRODUCER_ENABLE)
                self.disabled = disable
                self.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(self.globals.getApiSetting(ConfigurationKeyConstant.API_PRODUCER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and muteLogs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ProducerMethod(*methodArgs, requestClass=None, interceptor=None, disable=DEFAUTL_DISABLE, muteLogs=DEFAUTL_MUTE_LOGS, **methodKwargs) :
    resourceMethodDisable = disable
    resourceMethodMuteLogs = muteLogs
    resourceInterceptor = interceptor
    def innerMethodWrapper(resourceMethod, *innerMethodArgs, **innerMethodKwargs) :
        log.wrapper(ProducerMethod,f'''wrapping {resourceMethod.__name__}''')
        apiInstance = FlaskManager.getApi()
        methodClassName = ReflectionHelper.getMethodClassName(resourceMethod)
        methodName = ReflectionHelper.getName(resourceMethod)
        resourceMethod.disabled = disable
        resourceMethod.id = methodKwargs.get('id', f'{methodClassName}{c.DOT}{methodName}')
        resourceMethod.muteLogs = resourceMethodMuteLogs or ConverterStatic.getValueOrDefault(apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_PRODUCER_MUTE_LOGS), DEFAUTL_MUTE_LOGS and resourceMethodMuteLogs)
        producerArgs = [*methodArgs]
        producerKwargs = {**methodKwargs}
        resourceInstanceName = methodClassName[:-len(FlaskManager.KW_PRODUCER_RESOURCE)]
        resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        interceptor = resourceInterceptor if not isinstance(resourceInterceptor, str) else  ReflectionHelper.getAttributeOrMethodByNamePath(apiInstance, resourceInterceptor)
        @interceptor(*producerArgs, **producerKwargs)
        def innerResourceInstanceMethod(*args, **kwargs) :
            resourceInstance = FlaskManager.getResourceSelf(apiInstance, FlaskManager.KW_PRODUCER_RESOURCE, resourceInstanceName)
            args = FlaskManager.getArgumentInFrontOfArgs(args, resourceInstance) ###- resourceInstance = args[0]
            muteLogs = resourceInstance.muteLogs or resourceMethod.muteLogs
            if resourceInstance.enabled and not resourceInstance.disabled and not resourceMethod.disabled:
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} producer method started with args={methodArgs} and kwargs={methodKwargs}')
                methodReturn = None
                try :
                    FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                    methodReturn = resourceMethod(*args,**kwargs)
                except Exception as exception :
                    if not muteLogs:
                        log.warning(resourceMethod, f'Not possible to run {resourceMethod.id} properly', exception=exception, muteStackTrace=True)
                    FlaskManager.raiseAndPersistGlobalException(exception, resourceInstance, resourceMethod)
                if not muteLogs:
                    log.info(resourceMethod, f'{resourceMethod.id} producer method finished')
                return methodReturn
            if not muteLogs:
                log.warning(resourceMethod, f'{resourceMethod.id} producer method didn{c.SINGLE_QUOTE}t started. {"Handlers are disabled" if not resourceInstance.enabled else "This producer class is disabled" if resourceInstance.disabled else "This producer method is disabled"}')
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceMethod)
        innerResourceInstanceMethod.disable = resourceMethodDisable
        innerResourceInstanceMethod.muteLogs = resourceMethodMuteLogs
        innerResourceInstanceMethod.interceptor = resourceInterceptor
        return innerResourceInstanceMethod
    return innerMethodWrapper
