import time
from python_helper import Test, RandomHelper, log, DateTimeHelper, ObjectHelper, TestHelper
from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service.ExceptionHandler import GlobalException

LOG_HELPER_SETTINGS = {
    log.LOG : True,
    log.SUCCESS : True,
    log.SETTING : True,
    log.STATUS : True,
    log.INFO : True,
    log.DEBUG : True,
    log.WARNING : True,
    log.WRAPPER : True,
    log.FAILURE : True,
    log.ERROR : True,
    log.TEST : False
}

@Test(environmentVariables = {
    **{
        log.ENABLE_LOGS_WITH_COLORS: True
    },
    **LOG_HELPER_SETTINGS
})
def securityManager_worksProperly() :
    # arrange
    SECRET = 'abcd'
    SESSION_DURATION = 10 + 360
    ALGORITHM = 'HS256'
    HEADER_NAME = 'Context'
    HEADER_TYPE = 'Authorizaton '
    IDENTITY = RandomHelper.string(minimum=100, maximum=150)
    CONTEXT = 'ABCD'
    CONTEXT_LIST = [CONTEXT]
    DATA = {
        'personal': 'data'
    }
    deltaMinutes = DateTimeHelper.timeDelta(minutes=SESSION_DURATION)
    securityManager = SecurityManager.JwtManager(
        SECRET,
        ALGORITHM,
        HEADER_NAME,
        HEADER_TYPE
    )
    timeNow = DateTimeHelper.dateTimeNow()
    payload = {
        JwtConstant.KW_IAT: DateTimeHelper.timestampOf(dateTime=timeNow),
        JwtConstant.KW_NFB: DateTimeHelper.timestampOf(dateTime=timeNow),
        JwtConstant.KW_JTI: f"{int(f'{time.time()}'.replace('.', ''))+int(f'{time.time()}'.replace('.', ''))}",
        JwtConstant.KW_EXPIRATION: DateTimeHelper.timestampOf(dateTime=timeNow + deltaMinutes),
        JwtConstant.KW_IDENTITY: IDENTITY,
        JwtConstant.KW_FRESH: False,
        JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
        JwtConstant.KW_CLAIMS: {
            JwtConstant.KW_CONTEXT: CONTEXT_LIST,
            JwtConstant.KW_DATA: DATA
        }
    }

    # act
    totalRuns = 10000
    lines = 3
    initTime = time.time()
    for i in range(totalRuns):
        encodedPayload = securityManager.encode(payload)
        decodedPayload = securityManager.decode(encodedPayload)
        accessException = TestHelper.getRaisedException(securityManager.validateAccessAuthorization, rawJwt=decodedPayload)
    refreshException = TestHelper.getRaisedException(securityManager.validateRefreshAuthorization, rawJwt=decodedPayload)
    endTime = time.time() - initTime

    # assert
    assert lines * .0001 > endTime/totalRuns, (lines * .0001, endTime/totalRuns)
    assert ObjectHelper.equals(payload, decodedPayload), (payload, decodedPayload)
    assert ObjectHelper.isNone(accessException), accessException
    assert ObjectHelper.isNotNone(refreshException), refreshException
    assert ObjectHelper.equals(GlobalException.__name__, type(refreshException).__name__), (GlobalException.__name__, type(refreshException).__name__, refreshException)
    assert ObjectHelper.equals(401, refreshException.status)
    assert ObjectHelper.equals('Unauthorized', refreshException.message), f'Invalid authorization == {refreshException.message}'
    assert ObjectHelper.equals('Refresh authorization should have type refresh, but it is access', refreshException.logMessage), f'Refresh authorization should have type refresh, but it is access == {refreshException.logMessage}'
