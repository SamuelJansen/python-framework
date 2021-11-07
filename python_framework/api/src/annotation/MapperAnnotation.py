from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function
from python_framework.api.src.service.flask import FlaskManager

@Function
def Mapper() :
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Mapper,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            def __init__(self,*args,**kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self,*args,**kwargs)
                apiInstance = FlaskManager.getApi()
                self.service = apiInstance.resource.service
                self.validator = apiInstance.resource.validator
                self.mapper = apiInstance.resource.mapper
                self.helper = apiInstance.resource.helper
                self.converter = apiInstance.resource.converter
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper

@Function
def MapperMethod(requestClass=None, responseClass=None) :
    def innerMethodWrapper(resourceInstanceMethod,*args,**kwargs) :
        log.wrapper(MapperMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args,**kwargs) :
            resourceInstance = args[0]
            try :
                FlaskManager.validateArgs(args,requestClass,innerResourceInstanceMethod)
                args = FlaskManager.getArgsWithResponseClassInstanceAppended(args, responseClass)
                methodReturn = resourceInstanceMethod(*args,**kwargs)
            except Exception as exception :
                FlaskManager.raiseGlobalException(exception, resourceInstance, resourceInstanceMethod)
            return methodReturn
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper
