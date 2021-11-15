import time, requests
from pathlib import Path
from python_helper import Constant as c
from python_helper import Test, ObjectHelper, SettingHelper, EnvironmentHelper, log

### - most likelly to be moved to python_framework library
import subprocess, psutil

CURRENT_PATH = str(Path(__file__).parent.absolute())
ESTIMATED_BUILD_TIME_IN_SECONDS = 6

def killProcesses(givenProcess) :
    try :
        process = psutil.Process(givenProcess.pid)
        for child in process.children(recursive=True):
            child.kill()
        process.kill()
    except Exception as exception :
        log.log(killProcesses, 'Error while killing process', exception=exception)

def getProcess(command, path, timeout=20, muteLogs=False) :
    return subprocess.Popen(
        command, #if not muteLogs else f'''{command} {'2>/dev/null' if EnvironmentHelper.isLinux() else '> NUL'}''',
        cwd = path,
        # stdout = subprocess.PIPE,
        # stderr = None if not muteLogs else subprocess.DEVNULL,
        shell = True
    )


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
    log.TEST : False,
    log.ENABLE_LOGS_WITH_COLORS: True
}

### - Other possible solutions
# https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true

# import subprocess
# import psutil
# def killProcesses(pid):
#     process = psutil.Process(pid)
#     for child in process.children(recursive=True):
#         child.kill()
#     process.kill()
# process = subprocess.Popen(["infinite_app", "param"], shell=True)
# try:
#     process.wait(timeout=3)
# except subprocess.TimeoutExpired:
#     killProcesses(process.pid)
# process = subprocess.Popen(["infinite_app", "param"], shell=True)
# try:
#     process.wait(timeout=3)
# except subprocess.TimeoutExpired:
#     killProcesses(process.pid)


# import os
# import signal
# import subprocess
# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
# pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
# os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups


# processPath = f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone'
# command = 'flask run --host=localhost --port=5001'
# commandList = [
#     command + ('2>/dev/null' if EnvironmentHelper.isLinux() else ' > NUL')
# ]
# process = subprocess.Popen(commandList, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=processPath)
# process = subprocess.Popen(
#     commandList,
#     cwd = processPath,
#     stdout = subprocess.PIPE,
#     stderr = subprocess.DEVNULL,
#     shell = True,
#     preexec_fn = EnvironmentHelper.OS.setsid
# )
# time.sleep(3)

GET_ACTUATOR_HEALTH_CONTROLLER = f'/health'
TEST_CONTROLLER = '/test-controller'
TEST_BATCH_CONTROLLER = f'{TEST_CONTROLLER}/batch'

GET_ACTUATOR_HEALTH_CONTROLLER_TEST = '/test/actuator/health'

GET_NONE_ONE = f'{TEST_CONTROLLER}/all-fine-if-its-none'
POST_PAYLOAD_ONE = f'{TEST_CONTROLLER}/payload-validation-test'
GET_NONE_ONE_BATCH = f'{TEST_BATCH_CONTROLLER}/all-fine-if-its-none'
POST_PAYLOAD_ONE_BATCH = f'{TEST_BATCH_CONTROLLER}/payload-validation-test'

def debugRequests() :
    import requests
    import logging
    import http.client
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

@Test(environmentVariables={
    SettingHelper.ACTIVE_ENVIRONMENT : 'local'
})
def appRun_whenEnvironmentIsLocalFromLocalConfig_withSuccess() :
    # arrange
    muteLogs = False
    serverPort = 5001
    process = getProcess(
        f'flask run --host=localhost --port={serverPort}',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{serverPort}/local-test-api'
        payload = {'me':'and you'}
        payloadList = [payload]
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }

        # act
        # assert
        responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER, headers=headers)
        assert ObjectHelper.equals(
            {'status':'UP'},
            responseGetHealth.json()
        )
        assert 200 == responseGetHealth.status_code

        responseDocumentation = requests.get(BASE_URL + '/documentation', headers=headers)
        assert ObjectHelper.equals(
            'Local Test Api',
            responseDocumentation.json().get('info', {}).get('title')
        ), responseDocumentation.json().get('info', {})
        assert ObjectHelper.equals(
            'This is a Local Test Api service',
            responseDocumentation.json().get('info', {}).get('description')
        ), responseDocumentation.json().get('info', {})
        assert ObjectHelper.equals(
            '0.0.1',
            responseDocumentation.json().get('info', {}).get('version')
        ), responseDocumentation.json().get('info', {})
        assert 200 == responseGetHealth.status_code

        responseGetNone = requests.get(BASE_URL + GET_NONE_ONE)
        assert ObjectHelper.equals(
            {'message': 'OK'},
            responseGetNone.json()
        )
        assert 200 == responseGetNone.status_code

        responseGetNoneBatch = requests.post(BASE_URL + GET_NONE_ONE_BATCH, json=payload, headers=headers)
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.299735'},
            responseGetNoneBatch.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responseGetNoneBatch.status_code

        responsePostSendPayload = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payload, headers=headers)
        expectedResponsePostSendPayload = {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'}
        assert ObjectHelper.equals(
            {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'},
            responsePostSendPayload.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponsePostSendPayload} should be equals to {responsePostSendPayload.json()}'
        assert 400 == responsePostSendPayload.status_code

        responsePostSendPayloadList = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payloadList, headers=headers)
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-19 08:36:20.925177'},
            responsePostSendPayloadList.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responsePostSendPayloadList.status_code

        responsePostSendPayloadBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payload, headers=headers)
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.636759'},
            responsePostSendPayloadBatch.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responsePostSendPayloadBatch.status_code

        responsePostSendPayloadListBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payloadList, headers=headers)
        expectedResponsePostSendPayloadListBatch = {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.767735'}
        assert ObjectHelper.equals(
            expectedResponsePostSendPayloadListBatch,
            responsePostSendPayloadListBatch.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponsePostSendPayloadListBatch} should be equals to {responsePostSendPayloadListBatch.json()}'
        assert 400 == responsePostSendPayloadListBatch.status_code

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception

@Test(environmentVariables={
    SettingHelper.ACTIVE_ENVIRONMENT : 'dev'
})
def appRun_whenEnvironmentIsLocalFromDevConfig_withSuccess() :
    # arrange
    muteLogs = False
    serverPort = 5002
    process = getProcess(
        f'flask run --host=localhost --port={serverPort}',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{serverPort}/dev-test-api'
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }

        # act
        responseGetHealth = requests.post(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER_TEST, json={'status': 'UP'})

        # assert
        assert ObjectHelper.equals(
            [{'status':'UP'}],
            responseGetHealth.json()
        ), f"{[{'status':'UP'}]} == {responseGetHealth.json()}"
        assert 200 == responseGetHealth.status_code

        expectedResponseHeaders = {
            'added': 'header',
            'booleanFalse': False,
            'booleanTrue': True,
            'int': 1,
            'otherInt': -34,
            'float': 1.0,
            'otherFloat': 2.3334
        }
        for k, v in expectedResponseHeaders.items():
            assert k in dict(responseGetHealth.headers), k
            assert ObjectHelper.equals(
                str(v),
                dict(responseGetHealth.headers)[k]
            ), (k, str(v), dict(responseGetHealth.headers)[k])

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception

@Test()
def testing_headersAndParams() :
    #arrange
    muteLogs = False
    serverPort = 5010
    process = getProcess(
        f'flask run --host=localhost --port={serverPort}',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')
        BASE_URL = f'http://localhost:{serverPort}/local-test-api'
        params = {'first': 'first_p', 'second': 'second_p', 'ytu': 'uty', 'ytv': 'vty'}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache',
            "Pragma" : 'no-cache',
            'Expires' : '0',
            'Cache-Control' : 'public, max-age=0'
        }
        headers = {'firstHeader': 'firstHeader_h', 'secondHeader': 'secondHeader_h', 'ytu': 'uty', 'ytv': 'vty', **headers}
        log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

        #act
        responseComplete = requests.get(BASE_URL + f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}/abcdef/oi', params=params, headers=headers)
        responseWithoutParams = requests.get(BASE_URL + f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}/abcdef/oi', headers=headers)
        responseWithoutHeaders = requests.get(BASE_URL + f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}/abcdef/oi', params=params)
        responseWithoutHeadersAndWithoutParams = requests.get(BASE_URL + f'/test/actuator/health/{EnvironmentHelper.get("URL_VARIANT")}/abcdef/oi')
        log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')

        #assert
        assert ObjectHelper.equals(
            {
                "first": "first_p",
                "firstHeader": "firstHeader_h",
                "second": "second_p",
                "secondHeader": "secondHeader_h",
                "status": "abcdefoi"
            },
            responseComplete.json()
        )
        assert 200 == responseComplete.status_code
        assert ObjectHelper.equals(
            {
                "first": None,
                "firstHeader": "firstHeader_h",
                "second": None,
                "secondHeader": "secondHeader_h",
                "status": "abcdefoi"
            },
            responseWithoutParams.json()
        )
        assert 200 == responseWithoutParams.status_code
        assert ObjectHelper.equals(
            {
                "first": "first_p",
                "firstHeader": None,
                "second": "second_p",
                "secondHeader": None,
                "status": "abcdefoi"
            },
            responseWithoutHeaders.json()
        )
        assert 200 == responseWithoutHeaders.status_code
        assert ObjectHelper.equals(
            {
                "first": None,
                "firstHeader": None,
                "second": None,
                "secondHeader": None,
                "status": "abcdefoi"
            },
            responseWithoutHeadersAndWithoutParams.json()
        )
        assert 200 == responseWithoutHeadersAndWithoutParams.status_code
        log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception

@Test(environmentVariables={
    SettingHelper.ACTIVE_ENVIRONMENT : 'client'
    , log.ENABLE_LOGS_WITH_COLORS: True
    # , **LOG_HELPER_SETTINGS
})
def testing_Client() :
    #arrange
    muteLogs = False
    ### - port on python-build config
    process = getProcess(
        f'python app.py',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)
    log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')
    try:
        URL_PARAM = 'abcd'
        OTHER_URL_PARAM = 'efgh'
        BASE_SIMPLE_URL = 'http://localhost:5022/client-test-api'
        BASE_URL = f'{BASE_SIMPLE_URL}/test/{EnvironmentHelper.get("URL_VARIANT")}/{URL_PARAM}/{OTHER_URL_PARAM}'
        BASE_EXCEPTON_URL = f'{BASE_SIMPLE_URL}/exception/test/{EnvironmentHelper.get("URL_VARIANT")}/{URL_PARAM}/{OTHER_URL_PARAM}'
        PARAMS = {
            'someParam': 'given-someParam'
        }
        HEADERS = {
            'someHeader': 'given-someHeader'
        }

        ##################
        ###- getTest
        ##################
        getResponse = requests.get(f'{BASE_URL}/get', params=PARAMS, headers=HEADERS, timeout=10)
        assert ObjectHelper.isNotNone(getResponse)
        assert ObjectHelper.equals(200, getResponse.status_code)
        assert ObjectHelper.equals('headers-get', dict(getResponse.headers).get('get'))
        expectedGetResponse = {
            "someBody": URL_PARAM + OTHER_URL_PARAM,
            "someOtherBody": {
                "someHeader": "given-someHeader",
                "someParam": "given-someParam"
            }
        }
        assert ObjectHelper.equals(expectedGetResponse, getResponse.json())

        getExceptionResponse = requests.get(f'{BASE_EXCEPTON_URL}/get', params=PARAMS, headers=HEADERS, timeout=10)
        assert ObjectHelper.isNotNone(getExceptionResponse)
        assert ObjectHelper.equals(200, getExceptionResponse.status_code)
        assert ObjectHelper.equals('headers-get', dict(getExceptionResponse.headers).get('get'))
        expectedGetExceptionResponse = {
            'message': 'Something bad happened. Please, try again later',
            'timestamp': '2021-03-18 21:43:47.299735'
        }
        assert ObjectHelper.equals(
            expectedGetExceptionResponse,
            getResponse.json(),
            ignoreKeyList=['timestamp']
        )

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception

@Test(environmentVariables={
    SettingHelper.ACTIVE_ENVIRONMENT : 'local'
})
def pythonRun_worksProperly() :
    # arrange
    muteLogs = False
    devServerPort = 5001 ### - on local config
    process = getProcess(
        f'python app.py',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{devServerPort}/local-test-api'
        payload = {'me':'and you'}
        payloadList = [payload]
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

        # act
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }

        session = requests.Session()

        responseGetHealth = session.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER, headers=headers)

        responseGetNone = session.get(BASE_URL + GET_NONE_ONE)
        responseGetNoneBatch = session.post(BASE_URL + GET_NONE_ONE_BATCH, json=payload, headers=headers)

        responsePostSendPayload = session.post(BASE_URL + POST_PAYLOAD_ONE, json=payload, headers=headers)
        responsePostSendPayloadList = session.post(BASE_URL + POST_PAYLOAD_ONE, json=payloadList, headers=headers)
        responsePostSendPayloadBatch = session.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payload, headers=headers)
        responsePostSendPayloadListBatch = session.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payloadList, headers=headers)

        # print(requests.get('https://www.google.com/search?q=something&rlz=1C1GCEU_pt-BRBR884BR884&oq=something&aqs=chrome..69i57.5839j0j7&sourceid=chrome&ie=UTF-8'))
        # print(requests.get('https://www.google.com/search?q=something+else&rlz=1C1GCEU_pt-BRBR884BR884&sxsrf=ALeKk03rn_R9yREVJSkMqIUeAJfmFMVSfA%3A1619326195697&ei=8_SEYNWPKsGn5OUPobip-AQ&oq=something+else&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEJECMgUIABDLATIFCC4QywEyBQgAEMsBMgUILhDLATIFCC4QywEyBQgAEMsBMgUILhDLATICCAAyBQgAEMsBOgcIABBHELADOgcIABCwAxBDOg0ILhCwAxDIAxBDEJMCOgoILhCwAxDIAxBDOgIILjoHCAAQChDLAUoFCDgSATFQr_wLWPyCDGDdigxoAXACeACAAZYBiAGiBpIBAzAuNpgBAKABAaoBB2d3cy13aXrIAQ_AAQE&sclient=gws-wiz&ved=0ahUKEwiV1a2VzJjwAhXBE7kGHSFcCk8Q4dUDCA4&uact=5'))

        # print(f'responseGetNone: {responseGetNone.json()}')
        # print(f'responseGetNoneBatch: {responseGetNoneBatch.json()}')
        #
        # print(f'responsePostSendPayload: {responsePostSendPayload.json()}')
        # print(f'responsePostSendPayloadList: {responsePostSendPayloadList.json()}')
        # print(f'responsePostSendPayloadBatch: {responsePostSendPayloadBatch.json()}')
        # print(f'responsePostSendPayloadListBatch: {responsePostSendPayloadListBatch.json()}')

        # assert
        assert ObjectHelper.equals(
            {'status':'UP'},
            responseGetHealth.json()
        )
        assert 200 == responseGetHealth.status_code

        {'message': 'OK'}
        {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.299735'}
        {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'}
        {'me': 'and you'}
        {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.636759'}
        {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.767735'}
        # print(f'responseGetNone: {responseGetNone.json()}')
        assert ObjectHelper.equals(
            {'message': 'OK'},
            responseGetNone.json()
        )
        assert 200 == responseGetNone.status_code
        # print(f'responseGetNoneBatch: {responseGetNoneBatch.json()}')
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.299735'},
            responseGetNoneBatch.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responseGetNoneBatch.status_code
        # print(f'responsePostSendPayload: {responsePostSendPayload.json()}')
        assert ObjectHelper.equals(
            {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'},
            responsePostSendPayload.json(),
            ignoreKeyList=['timestamp']
        )
        assert 400 == responsePostSendPayload.status_code
        # print(f'responsePostSendPayloadList: {responsePostSendPayloadList.json()}')
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-19 08:36:20.925177'},
            responsePostSendPayloadList.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responsePostSendPayloadList.status_code
        assert ObjectHelper.equals(
            {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.636759'},
            responsePostSendPayloadBatch.json(),
            ignoreKeyList=['timestamp']
        )
        assert 500 == responsePostSendPayloadBatch.status_code
        assert ObjectHelper.equals(
            {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.767735'},
            responsePostSendPayloadListBatch.json(),
            ignoreKeyList=['timestamp']
        )
        assert 400 == responsePostSendPayloadListBatch.status_code

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception


@Test(environmentVariables={
    log.ENABLE_LOGS_WITH_COLORS: True,
    SettingHelper.ACTIVE_ENVIRONMENT : 'security-manager'
})
def pythonRun_securityManager() :
    # arrange
    muteLogs = False
    securityServerPort = 5011 ### - on security-manager config
    process = getProcess(
        f'python app.py',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{securityServerPort}/security-manager-api'
        BASE_URI = f'{BASE_URL}/test/{EnvironmentHelper.get("URL_VARIANT")}/security-manager'
        POST_LOGIN_URI = '/login'
        GET_CONSUME_URI = '/consume'
        GET_CONSUME_AFTER_REFRESH_URI = '/consume/only-after-refresh'
        PATCH_REFRESH_URI = '/refresh'
        PUT_LOGOUT_URI = '/logout'
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

        # act
        # assert
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }
        id = time.time()
        payload = {
            'id': id
        }

        responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER, headers=headers)
        assert ObjectHelper.equals(
            {'status':'UP'},
            responseGetHealth.json()
        )
        assert 200 == responseGetHealth.status_code

        responseGetConsumeBeforeLogin = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeLogin = {
            "message": "Unauthorized",
            "timestamp": "2021-11-02 21:47:32.444629"
        }
        assert ObjectHelper.isNotNone(responseGetConsumeBeforeLogin)
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeLogin,
            responseGetConsumeBeforeLogin.json(),
            ignoreKeyList=['timestamp']
        )

        responseLogin = requests.post(BASE_URI + POST_LOGIN_URI, json=payload, headers=headers)
        firstAuthorization = responseLogin.json().get('accessToken')
        firstAuthorizationHeaders = responseLogin.headers
        assert ObjectHelper.isNotNone(firstAuthorization)
        headers['Authorization'] = 'Bearer ' + firstAuthorization
        assert ObjectHelper.isNotNone(firstAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(firstAuthorizationHeaders.get('some'))

        responseGetConsumeBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_ROLE"
                ],
                "data": {
                    "some": "data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeRefresh,
            responseGetConsumeBeforeRefresh.json()
        ), f'{expectedResponseGetConsumeBeforeRefresh} should be equals to {responseGetConsumeBeforeRefresh.json()}'

        responseGetConsumeAfterRefreshBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_AFTER_REFRESH_URI, headers=headers)
        assert ObjectHelper.equals({
                "message": "Role not allowed",
                "timestamp": "2021-11-02 21:47:32.444629"
            },
            responseGetConsumeAfterRefreshBeforeRefresh.json(),
            ignoreKeyList=['timestamp']
        )
        assert 403 == responseGetConsumeAfterRefreshBeforeRefresh.status_code

        responsePatchRefresh = requests.patch(BASE_URI + PATCH_REFRESH_URI, json=payload, headers=headers)
        patchedAuthorizationHeaders = responseLogin.headers
        patchedAuthorization = responsePatchRefresh.json().get('accessToken')
        assert ObjectHelper.isNotNone(patchedAuthorization)
        headers['Authorization'] = 'Bearer ' + patchedAuthorization
        assert ObjectHelper.isNotNone(responsePatchRefresh)
        assert not ObjectHelper.equals(firstAuthorization, patchedAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(patchedAuthorizationHeaders.get('some'))

        responseGetConsumeAfterRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeAfterRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_ROLE",
                    "TEST_ROLE_REFRESH"
                ],
                "data": {
                    "some": "other data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterRefresh,
            responseGetConsumeAfterRefresh.json()
        ), f'{expectedResponseGetConsumeAfterRefresh} should be equals to {responseGetConsumeAfterRefresh.json()}'

        responseLogout = requests.put(BASE_URI + PUT_LOGOUT_URI, json=payload, headers=headers)
        assert ObjectHelper.isNotNone(responseLogout.json())
        expectedResponseLogout = {'message': 'Logged out'}
        assert ObjectHelper.equals(
            expectedResponseLogout,
            responseLogout.json()
        ), f'{expectedResponseLogout} should be equals to {responseLogout.json()}'
        assert 202 == responseLogout.status_code

        responseGetConsumeAfterLogout = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        assert ObjectHelper.isNotNone(responseGetConsumeAfterLogout.json())
        expectedResponseGetConsumeAfterLogout = {'message': 'Unauthorized', 'timestamp': '2021-11-03 01:10:10.876113'}
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterLogout,
            responseGetConsumeAfterLogout.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeAfterLogout} should be equals to {responseGetConsumeAfterLogout.json()}'
        assert 401 == responseGetConsumeAfterLogout.status_code

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception


@Test(environmentVariables={
    log.ENABLE_LOGS_WITH_COLORS: True,
    SettingHelper.ACTIVE_ENVIRONMENT : 'session-manager'
})
def pythonRun_sessionManager() :
    # arrange
    muteLogs = False
    sessionServerPort = 5012 ### - on session-manager config
    process = getProcess(
        f'python app.py',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{sessionServerPort}/session-manager-api'
        BASE_URI = f'{BASE_URL}/test/{EnvironmentHelper.get("URL_VARIANT")}/session-manager'
        POST_LOGIN_URI = '/login'
        GET_CONSUME_URI = '/consume'
        GET_CONSUME_AFTER_REFRESH_URI = '/consume/only-after-refresh'
        PATCH_REFRESH_URI = '/refresh'
        PUT_LOGOUT_URI = '/logout'
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }
        id = time.time()
        payload = {
            'id': id
        }

        # act
        # assert
        responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER, headers=headers)
        assert ObjectHelper.equals(
            {'status':'UP'},
            responseGetHealth.json()
        )
        assert 200 == responseGetHealth.status_code

        responseGetConsumeBeforeLogin = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeLogin = {
            "message": "Invalid session",
            "timestamp": "2021-11-02 21:47:32.444629"
        }
        assert ObjectHelper.isNotNone(responseGetConsumeBeforeLogin)
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeLogin,
            responseGetConsumeBeforeLogin.json(),
            ignoreKeyList=['timestamp']
        )

        responseLogin = requests.post(BASE_URI + POST_LOGIN_URI, json=payload, headers=headers)
        firstAuthorization = responseLogin.json().get('accessToken')
        firstAuthorizationHeaders = responseLogin.headers
        assert ObjectHelper.isNotNone(firstAuthorization)
        headers['Context'] = 'Bearer ' + firstAuthorization
        assert ObjectHelper.isNotNone(firstAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(firstAuthorizationHeaders.get('some'))

        responseGetConsumeBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_SESSION"
                ],
                "data": {
                    "some": "data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeRefresh,
            responseGetConsumeBeforeRefresh.json()
        ), f'{expectedResponseGetConsumeBeforeRefresh} should be equals to {responseGetConsumeBeforeRefresh.json()}'

        responseGetConsumeAfterRefreshBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_AFTER_REFRESH_URI, headers=headers)
        expectedResponseGetConsumeAfterRefreshBeforeRefresh = {
            "message": "Session not allowed",
            "timestamp": "2021-11-02 21:47:32.444629"
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterRefreshBeforeRefresh,
            responseGetConsumeAfterRefreshBeforeRefresh.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeAfterRefreshBeforeRefresh} should be equals to {responseGetConsumeAfterRefreshBeforeRefresh.json()}'
        assert 403 == responseGetConsumeAfterRefreshBeforeRefresh.status_code

        responsePatchRefresh = requests.patch(BASE_URI + PATCH_REFRESH_URI, json=payload, headers=headers)
        patchedAuthorizationHeaders = responseLogin.headers
        patchedAuthorization = responsePatchRefresh.json().get('accessToken')
        assert ObjectHelper.isNotNone(patchedAuthorization)
        headers['Context'] = 'Bearer ' + patchedAuthorization
        assert ObjectHelper.isNotNone(responsePatchRefresh)
        assert not ObjectHelper.equals(firstAuthorization, patchedAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(patchedAuthorizationHeaders.get('some'))

        responseGetConsumeAfterRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeAfterRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_SESSION",
                    "TEST_SESSION_REFRESH"
                ],
                "data": {
                    "some": "other data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterRefresh,
            responseGetConsumeAfterRefresh.json()
        ), f'{expectedResponseGetConsumeAfterRefresh} should be equals to {responseGetConsumeAfterRefresh.json()}'

        responseLogout = requests.put(BASE_URI + PUT_LOGOUT_URI, json=payload, headers=headers)
        assert ObjectHelper.isNotNone(responseLogout.json())
        expectedResponseLogout = {'message': 'Session closed'}
        assert ObjectHelper.equals(
            expectedResponseLogout,
            responseLogout.json()
        ), f'{expectedResponseLogout} should be equals to {responseLogout.json()}'
        assert 202 == responseLogout.status_code

        responseGetConsumeAfterLogout = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        assert ObjectHelper.isNotNone(responseGetConsumeAfterLogout.json())
        expectedResponseGetConsumeAfterLogout = {'message': 'Invalid session', 'timestamp': '2021-11-03 01:10:10.876113'}
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterLogout,
            responseGetConsumeAfterLogout.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeAfterLogout} should be equals to {responseGetConsumeAfterLogout.json()}'
        assert 401 == responseGetConsumeAfterLogout.status_code

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception


@Test(environmentVariables={
    log.ENABLE_LOGS_WITH_COLORS: True,
    SettingHelper.ACTIVE_ENVIRONMENT : 'api-key-manager'
})
def pythonRun_apiKeyManager() :
    # arrange
    muteLogs = False
    apiKeyServerPort = 5013 ### - on apiKey-manager config
    process = getProcess(
        f'python app.py',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    try:
        BASE_URL = f'http://localhost:{apiKeyServerPort}/api-key-manager-api'
        BASE_URI = f'{BASE_URL}/test/{EnvironmentHelper.get("URL_VARIANT")}/api-key-manager'
        POST_LOGIN_URI = '/login'
        GET_CONSUME_URI = '/consume'
        GET_CONSUME_AFTER_REFRESH_URI = '/consume/only-after-refresh'
        PATCH_REFRESH_URI = '/refresh'
        PUT_LOGOUT_URI = '/logout'
        time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            'Cache-Control': 'no-cache'
        }
        id = time.time()
        payload = {
            'id': id
        }

        # act
        # assert
        responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER, headers=headers)
        assert ObjectHelper.equals(
            {'status':'UP'},
            responseGetHealth.json()
        )
        assert 200 == responseGetHealth.status_code

        responseGetConsumeBeforeLogin = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeLogin = {
            "message": "Invalid apiKey",
            "timestamp": "2021-11-02 21:47:32.444629"
        }
        assert ObjectHelper.isNotNone(responseGetConsumeBeforeLogin)
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeLogin,
            responseGetConsumeBeforeLogin.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeBeforeLogin} should be equals to {responseGetConsumeBeforeLogin.json()}'

        responseLogin = requests.post(BASE_URI + POST_LOGIN_URI, json=payload, headers=headers)
        firstAuthorization = responseLogin.json().get('accessToken')
        firstAuthorizationHeaders = responseLogin.headers
        assert ObjectHelper.isNotNone(firstAuthorization)
        headers['Api-key'] = 'Bearer ' + firstAuthorization
        assert ObjectHelper.isNotNone(firstAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(firstAuthorizationHeaders.get('some'))

        responseGetConsumeBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeBeforeRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_API_KEY"
                ],
                "data": {
                    "some": "data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeBeforeRefresh,
            responseGetConsumeBeforeRefresh.json()
        ), f'{expectedResponseGetConsumeBeforeRefresh} should be equals to {responseGetConsumeBeforeRefresh.json()}'

        responseGetConsumeAfterRefreshBeforeRefresh = requests.get(BASE_URI + GET_CONSUME_AFTER_REFRESH_URI, headers=headers)
        expectedResponseGetConsumeAfterRefreshBeforeRefresh = {
            "message": "ApiKey not allowed",
            "timestamp": "2021-11-02 21:47:32.444629"
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterRefreshBeforeRefresh,
            responseGetConsumeAfterRefreshBeforeRefresh.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeAfterRefreshBeforeRefresh} should be equals to {responseGetConsumeAfterRefreshBeforeRefresh.json()}'
        assert 403 == responseGetConsumeAfterRefreshBeforeRefresh.status_code

        responsePatchRefresh = requests.patch(BASE_URI + PATCH_REFRESH_URI, json=payload, headers=headers)
        patchedAuthorizationHeaders = responseLogin.headers
        patchedAuthorization = responsePatchRefresh.json().get('accessToken')
        assert ObjectHelper.isNotNone(patchedAuthorization)
        headers['Api-key'] = 'Bearer ' + patchedAuthorization
        assert ObjectHelper.isNotNone(responsePatchRefresh)
        assert not ObjectHelper.equals(firstAuthorization, patchedAuthorization)
        assert ObjectHelper.isNotNone(id)
        assert ObjectHelper.isNone(patchedAuthorizationHeaders.get('some'))

        responseGetConsumeAfterRefresh = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        expectedResponseGetConsumeAfterRefresh = {
            "secured": "information",
            "currentUser": {
                "identity": id,
                "context": [
                    "TEST_API_KEY",
                    "TEST_API_KEY_REFRESH"
                ],
                "data": {
                    "some": "other data"
                }
            }
        }
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterRefresh,
            responseGetConsumeAfterRefresh.json()
        ), f'{expectedResponseGetConsumeAfterRefresh} should be equals to {responseGetConsumeAfterRefresh.json()}'

        responseLogout = requests.put(BASE_URI + PUT_LOGOUT_URI, json=payload, headers=headers)
        assert ObjectHelper.isNotNone(responseLogout.json())
        expectedResponseLogout = {'message': 'ApiKey closed'}
        assert ObjectHelper.equals(
            expectedResponseLogout,
            responseLogout.json()
        ), f'{expectedResponseLogout} should be equals to {responseLogout.json()}'
        assert 202 == responseLogout.status_code

        responseGetConsumeAfterLogout = requests.get(BASE_URI + GET_CONSUME_URI, headers=headers)
        assert ObjectHelper.isNotNone(responseGetConsumeAfterLogout.json())
        expectedResponseGetConsumeAfterLogout = {'message': 'Invalid apiKey', 'timestamp': '2021-11-03 01:10:10.876113'}
        assert ObjectHelper.equals(
            expectedResponseGetConsumeAfterLogout,
            responseGetConsumeAfterLogout.json(),
            ignoreKeyList=['timestamp']
        ), f'{expectedResponseGetConsumeAfterLogout} should be equals to {responseGetConsumeAfterLogout.json()}'
        assert 401 == responseGetConsumeAfterLogout.status_code

        killProcesses(process)
    except Exception as exception:
        killProcesses(process)
        raise exception
