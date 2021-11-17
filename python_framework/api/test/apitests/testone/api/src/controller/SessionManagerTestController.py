from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod


VALID_TOKEN_MINUTES_DURATION = 30


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/session-manager', tag='SessionManagerTest', description='Session Manager controller test')
class SessionManagerTestController:

    @ControllerMethod(
        url = f'/consume',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        contextRequired=['TEST_SESSION']
    )
    def get(self):
        return {
            'secured': 'information',
            'currentUser': SessionManager.getCurrentSession()
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
            'accessToken': SessionManager.createAccessToken(dto['id'], ['TEST_SESSION'], deltaMinutes=VALID_TOKEN_MINUTES_DURATION, headers=headers, data=data)
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/refresh',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        contextRequired=['TEST_SESSION']
    )
    def patch(self, dto):
        assert 'headers' == SessionManager.getJwtHeaders().get('some'), f"headers == {SessionManager.getJwtHeaders().get('some')} should be equals. Headers: {SessionManager.getJwtHeaders()}"
        headers={'some': 'other headers'}
        data = {'some': 'other data'}
        return {
            'accessToken': SessionManager.patchAccessToken(newContextList=['TEST_SESSION', 'TEST_SESSION_REFRESH'], headers=headers, data=data)
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/logout',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        contextRequired=['TEST_SESSION', 'TEST_SESSION_REFRESH']
    )
    def put(self, dto):
        SessionManager.addAccessTokenToBlackList()
        return {'message': 'Session closed'}, HttpStatus.ACCEPTED


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/session-manager', tag='SessionManagerTest', description='Session Manager controller test')
class SessionManagerTestBatchController:

    @ControllerMethod(
        url = f'/consume/only-after-refresh',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        contextRequired=['TEST_SESSION_REFRESH']
    )
    def get(self):
        # print(SessionManager.getCurrentSession())
        assert 'other headers' == SessionManager.getJwtHeaders().get('some'), f"other headers == {SessionManager.getJwtHeaders().get('some')} should be equals. Headers: {SessionManager.getJwtHeaders()}"
        return {
            'secured': 'information',
            'after': 'refresh',
            'currentUser': SessionManager.getCurrentSession()
        }, HttpStatus.OK
