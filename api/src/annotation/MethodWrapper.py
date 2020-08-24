from python_helper import log
from python_helper import Constant as c

KW_CLASS = 'class'
KW_METHOD = 'method'
KW_FUNCTION = 'function'
NAME_NOT_PRESENT = 'name not present'

def Function(function,*args,**kwargs) :
    def wrapedFunction(*args,**kwargs) :
        try :
            functionReturn = function(*args,**kwargs)
        except Exception as exception :
            try :
                functionName = f'{function.__name__}'
            except :
                functionName = f'({KW_FUNCTION} {NAME_NOT_PRESENT})'
            log.wraper(Function,f'''failed to execute "{functionName}" function. Received args: {args}. Received kwargs: {kwargs}''',exception)
            raise Exception(f'{functionName} function error{c.DOT_SPACE_CAUSE}{str(exception)}')
        return functionReturn
    overrideSignatures(wrapedFunction, function)
    return wrapedFunction

def Method(method,*args,**kwargs) :
    def wrapedMethod(*args,**kwargs) :
        try :
            methodReturn = method(*args,**kwargs)
        except Exception as exception :
            try :
                className = f'{args[0].__class__.__name__}'
            except :
                className = f'({KW_CLASS} {NAME_NOT_PRESENT})'
            try :
                methodName = method.__name__
            except :
                methodName = f'({KW_METHOD} {NAME_NOT_PRESENT})'
            log.wraper(Method,f'''failed to execute {className}{c.DOT}{methodName} method. Received args: {args}. Received kwargs: {kwargs}''',exception)
            raise Exception(f'{className}{methodName} method error{c.DOT_SPACE_CAUSE}{str(exception)}')
        return methodReturn
    overrideSignatures(wrapedMethod, method)
    return wrapedMethod

def overrideSignatures(toOverride, original) :
    try :
        toOverride.__name__ = original.__name__
        toOverride.__module__ = original.__module__
        toOverride.__qualname__ = original.__qualname__
    except Exception as exception :
        log.wraper(overrideSignatures,f'''failed to override signatures of {toOverride} by signatures of {original} method''',exception)
