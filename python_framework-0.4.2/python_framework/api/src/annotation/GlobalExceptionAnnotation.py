import inspect, functools
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, StringHelper, log, Function
from python_framework.api.src.service.ExceptionHandler import GlobalException, DEFAULT_MESSAGE, DEFAULT_LOG_MESSAGE
from python_framework.api.src.enumeration.HttpStatus import HttpStatus


@Function
def EncapsulateItWithGlobalException(message=DEFAULT_MESSAGE, logMessage=DEFAULT_LOG_MESSAGE, status=HttpStatus.INTERNAL_SERVER_ERROR) :
    encapsulateItWithGlobalExceptionMessage = message
    encapsulateItWithGlobalExceptionLogMessage = logMessage
    encapsulateItWithGlobalExceptionStatus = status
    def wrapper(givenFunction,*args,**kwargs) :
        log.wrapper(wrapper, f'Wrapping {givenFunction} function with (*{args} args and **{kwargs} kwargs)')
        def wrapedFunction(*args,**kwargs) :
            try :
                givenFunctionReturn = givenFunction(*args,**kwargs)
            except Exception as exception :
                if isinstance(exception, GlobalException):
                    raise exception
                message = encapsulateItWithGlobalExceptionMessage
                logMessage = str(exception) if StringHelper.isNotBlank(str(exception)) else encapsulateItWithGlobalExceptionLogMessage
                givenFunctionName = ReflectionHelper.getName(givenFunction, typeName=c.TYPE_FUNCTION)
                log.wrapper(EncapsulateItWithGlobalException, f'''Failed to execute "{givenFunctionName}(args={args}, kwargs={kwargs})" {c.TYPE_FUNCTION} call''', exception)
                raise GlobalException(
                    message=message,
                    logMessage=logMessage,
                    logResource=ReflectionHelper.getParentClass(givenFunction),
                    logResourceMethod=givenFunction,
                    status=HttpStatus.map(encapsulateItWithGlobalExceptionStatus).enumValue
                )
            return givenFunctionReturn
        ReflectionHelper.overrideSignatures(wrapedFunction, givenFunction)
        return wrapedFunction
    return wrapper
