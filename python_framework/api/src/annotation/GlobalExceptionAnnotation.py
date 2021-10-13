import inspect, functools
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, StringHelper, log, Function
from python_framework.api.src.service.ExceptionHandler import GlobalException, DEFAULT_MESSAGE, DEFAULT_LOG_MESSAGE
from python_framework.api.src.enumeration.HttpStatus import HttpStatus


@Function
def EncapsulateItWithGlobalException(message=DEFAULT_MESSAGE, status=HttpStatus.INTERNAL_SERVER_ERROR) :
    def Function(function,*args,**kwargs) :
        def wrapedFunction(*args,**kwargs) :
            try :
                functionReturn = function(*args,**kwargs)
            except Exception as exception :
                if isinstance(exception, GlobalException):
                    raise exception
                logMessage = str(exception) if StringHelper.isNotBlank(str(exception)) else LOG_MESSAGE_NOT_PRESENT
                functionName = ReflectionHelper.getName(function, typeName=c.TYPE_FUNCTION)
                log.wraper(EncapsulateItWithGlobalException, f'''Failed to execute "{functionName}(args={args}, kwargs={kwargs})" {c.TYPE_FUNCTION} call''', exception)
                raise GlobalException(message=message, logMessage=logMessage, logResource=ReflectionHelper.getParentClass(function), logResourceMethod=function, status=HttpStatus.map(status))
            return functionReturn
        ReflectionHelper.overrideSignatures(wrapedFunction, function)
        return wrapedFunction
    return Function
