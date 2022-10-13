from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function
from python_framework.api.src.service.flask import FlaskManager

@Function
def Service() :
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Service,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args,**kwargs)
                self.service = apiInstance.resource.service
                self.client = apiInstance.resource.client
                self.emitter = apiInstance.resource.emitter
                self.repository = apiInstance.resource.repository
                self.validator = apiInstance.resource.validator
                self.mapper = apiInstance.resource.mapper
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
                self.globals = apiInstance.globals
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def ServiceMethod(requestClass=None):
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        log.wrapper(ServiceMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                FlaskManager.raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper
