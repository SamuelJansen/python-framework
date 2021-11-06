from python_helper import EnvironmentHelper
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service.flask.FlaskManager import Controller, ControllerMethod


VALID_TOKEN_MINUTES_DURATION = 30


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/api-key-manager', tag='ApiKeyManagerTest', description='ApiKey Manager controller test')
class ApiKeyManagerTestController:

    @ControllerMethod(
        url = f'/consume',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        apiKeyRequired=['TEST_API_KEY']
    )
    def get(self):
        return {
            'secured': 'information',
            'currentUser': ApiKeyManager.getCurrentApiKey()
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
            'accessToken': ApiKeyManager.createAccessToken(dto['id'], ['TEST_API_KEY'], deltaMinutes=VALID_TOKEN_MINUTES_DURATION, headers=headers, data=data)
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/refresh',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        apiKeyRequired=['TEST_API_KEY']
    )
    def patch(self, dto):
        assert 'headers' == ApiKeyManager.getJwtHeaders().get('some'), f"headers == {ApiKeyManager.getJwtHeaders().get('some')} should be equals. Headers: {ApiKeyManager.getJwtHeaders()}"
        headers={'some': 'other headers'}
        data = {'some': 'other data'}
        return {
            # 'accessToken': ApiKeyManager.patchAccessToken(dto['id'], ['TEST_API_KEY', 'TEST_API_KEY_REFRESH'], deltaMinutes=VALID_TOKEN_MINUTES_DURATION, headers=headers, data=data)
            'accessToken': ApiKeyManager.patchAccessToken(newContextList=['TEST_API_KEY', 'TEST_API_KEY_REFRESH'], headers=headers, data=data)
        }, HttpStatus.OK

    @ControllerMethod(
        url = f'/logout',
        requestClass = dict,
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        apiKeyRequired=['TEST_API_KEY', 'TEST_API_KEY_REFRESH']
    )
    def put(self, dto):
        ApiKeyManager.addUserToBlackList()
        return {'message': 'ApiKey closed'}, HttpStatus.ACCEPTED


@Controller(url=f'/test/{EnvironmentHelper.get("URL_VARIANT")}/api-key-manager', tag='ApiKeyManagerTest', description='ApiKey Manager controller test')
class ApiKeyManagerTestBatchController:

    @ControllerMethod(
        url = f'/consume/only-after-refresh',
        responseClass = dict,
        logRequest = True,
        logResponse = True,
        apiKeyRequired=['TEST_API_KEY_REFRESH']
    )
    def get(self):
        # print(ApiKeyManager.getCurrentApiKey())
        assert 'other headers' == ApiKeyManager.getJwtHeaders().get('some'), f"other headers == {ApiKeyManager.getJwtHeaders().get('some')} should be equals. Headers: {ApiKeyManager.getJwtHeaders()}"
        return {
            'secured': 'information',
            'after': 'refresh',
            'currentUser': ApiKeyManager.getCurrentApiKey()
        }, HttpStatus.OK
