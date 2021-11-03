from python_helper import log, Test, SettingHelper, RandomHelper, ObjectHelper, TestHelper, ReflectionHelper, Constant
from python_framework import EncapsulateItWithGlobalException, GlobalException, ExceptionHandler, HttpStatus

LOG_HELPER_SETTINGS = {
    log.LOG : False,
    log.INFO : True,
    log.SUCCESS : True,
    log.SETTING : True,
    log.DEBUG : True,
    log.WARNING : True,
    log.WRAPPER : True,
    log.FAILURE : True,
    log.ERROR : True,
    log.TEST : False
}

FULL_LOG_HELPER_SETTINGS = {
    log.LOG : True,
    log.INFO : True,
    log.SUCCESS : True,
    log.SETTING : True,
    log.DEBUG : True,
    log.WARNING : True,
    log.WRAPPER : True,
    log.FAILURE : True,
    log.ERROR : True,
    log.TEST : False
}

SUCCESS = '__SUCCESS__'
FAILURE = '__FAILURE__'

RAISED_EXCEPTION = Exception(FAILURE)

@EncapsulateItWithGlobalException()
def externalFuncionDoesNotThrowsException():
    return SUCCESS

@EncapsulateItWithGlobalException()
def externalFuncionDoesThrowsException():
    raise RAISED_EXCEPTION

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def encapsulateItWithGlobalException_noParameters_unknownException() :
    #arrange
    @EncapsulateItWithGlobalException()
    def internalFuncionDoesNotThrowsException():
        return SUCCESS
    @EncapsulateItWithGlobalException()
    def internalFuncionDoesThrowsException():
        raise RAISED_EXCEPTION

    # #act
    externalSuccess = externalFuncionDoesNotThrowsException()
    internalSuccess = internalFuncionDoesNotThrowsException()
    externalFailure = TestHelper.getRaisedException(externalFuncionDoesThrowsException)
    internalFailure = TestHelper.getRaisedException(internalFuncionDoesThrowsException)
    # print(externalFailure.logResource)
    # print(externalFailure.logResourceMethod)
    # print(internalFailure.logResource)
    # print(internalFailure.logResourceMethod)

    #assert
    assert SUCCESS == externalSuccess
    assert SUCCESS == internalSuccess
    assert not RAISED_EXCEPTION == externalFailure, f'not {RAISED_EXCEPTION} == {externalFailure}: {not RAISED_EXCEPTION == externalFailure}'
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert not RAISED_EXCEPTION == externalFailure, f'not {RAISED_EXCEPTION} == {externalFailure}: {not RAISED_EXCEPTION == externalFailure}'
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert GlobalException == ReflectionHelper.getClass(externalFailure)
    assert GlobalException == ReflectionHelper.getClass(internalFailure)
    assert ExceptionHandler.DEFAULT_MESSAGE == externalFailure.message, f'{ExceptionHandler.DEFAULT_LOG_MESSAGE} == {externalFailure.message}: {ExceptionHandler.DEFAULT_LOG_MESSAGE == externalFailure.message}'
    assert ExceptionHandler.DEFAULT_MESSAGE == internalFailure.message
    assert HttpStatus.INTERNAL_SERVER_ERROR == externalFailure.status
    assert HttpStatus.INTERNAL_SERVER_ERROR == internalFailure.status
    assert FAILURE == externalFailure.logMessage
    assert FAILURE == internalFailure.logMessage
    assert ExceptionHandler.DEFAULT_LOG_RESOURCE == externalFailure.logResource, f'{ExceptionHandler.DEFAULT_LOG_RESOURCE} == {externalFailure.logResource}: {ExceptionHandler.DEFAULT_LOG_RESOURCE == externalFailure.logResource}'
    assert externalFuncionDoesThrowsException.__name__ == externalFailure.logResourceMethod.__name__, f'{externalFuncionDoesThrowsException} == {externalFailure.logResourceMethod}: {externalFuncionDoesThrowsException == externalFailure.logResourceMethod}'
    assert ExceptionHandler.DEFAULT_LOG_RESOURCE == internalFailure.logResource, f'{ExceptionHandler.DEFAULT_LOG_RESOURCE} == {internalFailure.logResource}: {ExceptionHandler.DEFAULT_LOG_RESOURCE == internalFailure.logResource}'
    assert type(internalFuncionDoesThrowsException) == type(internalFailure.logResourceMethod)


@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def encapsulateItWithGlobalException_noParameters_GlobalException() :
    #arrange

    class MyClass:
        def myMethod(self):
            ...
    resource = MyClass()
    ERROR_MESSAGE = 'ERROR_MESSAGE'
    LOG_ERROR_MESSAGE = 'LOG_ERROR_MESSAGE'
    EXCEPTION_STATUS = HttpStatus.BAD_REQUEST
    simpleException = GlobalException(
        status = EXCEPTION_STATUS,
        message = ERROR_MESSAGE,
        logMessage = LOG_ERROR_MESSAGE,
        logResource = resource,
        logResourceMethod = resource.myMethod
    )
    @EncapsulateItWithGlobalException()
    def internalFuncionDoesThrowsException():
        raise simpleException

    # #act
    internalFailure = TestHelper.getRaisedException(internalFuncionDoesThrowsException)
    # print(internalFailure)
    # print(internalFailure.logResource)
    # print(internalFailure.logResourceMethod)

    #assert
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert GlobalException == ReflectionHelper.getClass(internalFailure)
    assert ERROR_MESSAGE == internalFailure.message, f'"{ERROR_MESSAGE}" and "{internalFailure.message}" should be equals'
    assert EXCEPTION_STATUS == internalFailure.status
    assert LOG_ERROR_MESSAGE == internalFailure.logMessage, f'"{LOG_ERROR_MESSAGE} == {internalFailure.logMessage}": {LOG_ERROR_MESSAGE == internalFailure.logMessage}'
    assert resource == internalFailure.logResource, f'"{resource} == {internalFailure.logResource}": {resource == internalFailure.logResource}'
    assert resource.myMethod == internalFailure.logResourceMethod, f'"{resource.myMethod} == {internalFailure.logResourceMethod}": {resource.myMethod == internalFailure.logResourceMethod}'


@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def encapsulateItWithGlobalException_withParameters_GlobalException() :
    #arrange

    class MyClass:
        def myMethod(self):
            ...
    resource = MyClass()
    ERROR_MESSAGE = 'ERROR_MESSAGE'
    LOG_ERROR_MESSAGE = 'LOG_ERROR_MESSAGE'
    EXCEPTION_STATUS = HttpStatus.BAD_REQUEST
    simpleException = Exception(ERROR_MESSAGE)
    PERSONALIZED_MESSAGE = 'PERSONALIZED_MESSAGE'
    PERSONALIZED_STATUS = HttpStatus.UNAUTHORIZED
    @EncapsulateItWithGlobalException(message=PERSONALIZED_MESSAGE, status=PERSONALIZED_STATUS)
    def internalFuncionDoesThrowsException():
        raise simpleException

    #act
    internalFailure = TestHelper.getRaisedException(internalFuncionDoesThrowsException)
    # print(internalFailure)
    # print(internalFailure.logResource)
    # print(internalFailure.logResourceMethod)

    #assert
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert not RAISED_EXCEPTION == internalFailure, f'not {RAISED_EXCEPTION} == {internalFailure}: {not RAISED_EXCEPTION == internalFailure}'
    assert GlobalException == ReflectionHelper.getClass(internalFailure)
    assert PERSONALIZED_MESSAGE == internalFailure.message, f'{PERSONALIZED_MESSAGE} == {internalFailure.message}: {PERSONALIZED_MESSAGE == internalFailure.message}'
    assert PERSONALIZED_STATUS == internalFailure.status
    assert ERROR_MESSAGE == internalFailure.logMessage, f'{ERROR_MESSAGE} == {internalFailure.logMessage}: {ERROR_MESSAGE == internalFailure.logMessage}'
    assert ExceptionHandler.DEFAULT_LOG_RESOURCE == internalFailure.logResource
    assert type(internalFuncionDoesThrowsException) == type(internalFailure.logResourceMethod)
