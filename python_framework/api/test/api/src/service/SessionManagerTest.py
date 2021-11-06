import time
from python_helper import Test, RandomHelper, log, DateTimeHelper, ObjectHelper, TestHelper
from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service.ExceptionHandler import GlobalException

@Test(environmentVariables = {
    log.ENABLE_LOGS_WITH_COLORS: True
})
def patchSession_worksProperly() :
    # arrange
    SECRET = 'abcd'
    SESSION_DURATION = 10
    ALGORITHM = 'HS256'
    HEADER_NAME = 'Context'
    HEADER_TYPE = 'Session '
    IDENTITY = RandomHelper.string(minimum=100, maximum=150)
    CONTEXT = 'ABCD'
    CONTEXT_LIST = [CONTEXT]
    DATA = {
        'personal': 'data'
    }
    deltaMinutes = DateTimeHelper.timeDelta(minutes=1)
    sessionManager = SessionManager.JwtManager(
        SECRET,
        ALGORITHM,
        HEADER_NAME,
        HEADER_TYPE
    )
    timeNow = DateTimeHelper.dateTimeNow()
    payload = {
        JwtConstant.KW_IAT: timeNow,
        JwtConstant.KW_NFB: timeNow,
        JwtConstant.KW_JTI: f"{int(f'{time.time()}'.replace('.', ''))+int(f'{time.time()}'.replace('.', ''))}",
        JwtConstant.KW_EXPIRATION: timeNow + deltaMinutes,
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
    lines = 4
    initTime = time.time()
    for i in range(totalRuns):
        encodedPayload = sessionManager.encode(payload)
        decodedPayload = sessionManager.decode(encodedPayload)
        accessException = TestHelper.getRaisedException(sessionManager.validateAccessSession, rawJwt=decodedPayload)
        refreshException = TestHelper.getRaisedException(sessionManager.validateRefreshSession, rawJwt=decodedPayload)
    endTime = time.time() - initTime

    # assert
    assert lines * .0001 > endTime/totalRuns, (lines * .0001, endTime/totalRuns)
    assert ObjectHelper.equals(payload, decodedPayload)
    assert ObjectHelper.isNone(accessException)
    assert ObjectHelper.isNotNone(refreshException)
    assert ObjectHelper.equals(GlobalException.__name__, type(refreshException).__name__), (GlobalException.__name__, type(refreshException).__name__, refreshException)
    assert ObjectHelper.equals(401, refreshException.status)
    assert ObjectHelper.equals('Unauthorized', refreshException.message)
    assert ObjectHelper.equals('Refresh session should have type refresh, but it is access', refreshException.logMessage)
