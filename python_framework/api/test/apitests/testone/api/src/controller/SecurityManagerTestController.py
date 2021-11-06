from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod
from python_framework.api.src.util import UtcDateTimeUtil


VALID_TOKEN_MINUTES_DURATION = 30


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/security-manager', tag='SecurityManagerTest', description='Security Manager controller test')
class SecurityManagerTestController:

    @ControllerMethod(
        url = f'/consume',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        roleRequired=['TEST_ROLE']
    )
    def get(self):
        return {
            'secured': 'information',
            'currentUser': SecurityManager.getCurrentUser()
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/login',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True
    )
    def post(self, dto):
        headers={'some': 'headers'}
        data = {'some': 'data'}
        return {
            'accessToken': SecurityManager.createAccessToken(dto['id'], ['TEST_ROLE'], deltaMinutes=VALID_TOKEN_MINUTES_DURATION, headers=headers, data=data)
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/refresh',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        roleRequired=['TEST_ROLE']
    )
    def patch(self, dto):
        assert 'headers' == SecurityManager.getJwtHeaders().get('some'), f"headers == {SecurityManager.getJwtHeaders().get('some')} should be equals. Headers: {SecurityManager.getJwtHeaders()}"
        headers={'some': 'other headers'}
        data = {'some': 'other data'}
        accessToken = SecurityManager.patchAccessToken(newContextList=['TEST_ROLE', 'TEST_ROLE_REFRESH'], headers=headers, data=data)
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getExpiration()))
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getIat()))
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getNfb()))
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getExpiration()))
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getIat()))
        print(UtcDateTimeUtil.ofTimestamp(SecurityManager.getNfb()))
        return {
            # 'accessToken': SecurityManager.patchAccessToken(dto['id'], ['TEST_ROLE', 'TEST_ROLE_REFRESH'], deltaMinutes=VALID_TOKEN_MINUTES_DURATION, headers=headers, data=data)
            'accessToken': accessToken
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/logout',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        roleRequired=['TEST_ROLE', 'TEST_ROLE_REFRESH']
    )
    def put(self, dto):
        SecurityManager.addUserToBlackList()
        return {'message': 'Logged out'}, HttpStatus.ACCEPTED


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/security-manager', tag='SecurityManagerTest', description='Security Manager controller test')
class SecurityManagerTestBatchController:

    @ControllerMethod(
        url = f'/consume/only-after-refresh',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        roleRequired=['TEST_ROLE_REFRESH']
    )
    def get(self):
        assert 'other headers' == SecurityManager.getJwtHeaders().get('some'), f"other headers == {SecurityManager.getJwtHeaders().get('some')} should be equals. Headers: {SecurityManager.getJwtHeaders()}"
        return {
            'secured': 'information',
            'after': 'refresh',
            'currentUser': SecurityManager.getCurrentUser()
        }, HttpStatus.OK
