import time, requests
from pathlib import Path
from python_helper import Constant as c
from python_helper import Test, ObjectHelper, SettingHelper, EnvironmentHelper, log

### - most likelly to be moved to python_framework library
import subprocess, psutil

CURRENT_PATH = str(Path(__file__).parent.absolute())
ESTIMATED_BUILD_TIME_IN_SECONDS = 4

def killProcesses(givenProcess) :
    try :
        process = psutil.Process(givenProcess.pid)
        for child in process.children(recursive=True):
            child.kill()
        process.kill()
    except Exception as exception :
        log.log(killProcesses, 'Error while killing process', exception=exception)

def getProcess(command, path, muteLogs=False) :
    return subprocess.Popen(
        command, #if not muteLogs else f'''{command} {'2>/dev/null' if EnvironmentHelper.isLinux() else '> NUL'}''',
        cwd = path,
        # stdout = subprocess.PIPE,
        # stderr = None if not muteLogs else subprocess.DEVNULL,
        shell = True
    )


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

GET_ACTUATOR_HEALTH_CONTROLLER = f'/actuator/health'
TEST_CONTROLLER = '/test-controller'
TEST_BATCH_CONTROLLER = f'{TEST_CONTROLLER}/batch'

GET_ACTUATOR_HEALTH_CONTROLLER_TEST = '/test/actuator/health'

GET_NONE_ONE = f'{TEST_CONTROLLER}/all-fine-if-its-none'
POST_PAYLOAD_ONE = f'{TEST_CONTROLLER}/payload-validation-test'
GET_NONE_ONE_BATCH = f'{TEST_BATCH_CONTROLLER}/all-fine-if-its-none'
POST_PAYLOAD_ONE_BATCH = f'{TEST_BATCH_CONTROLLER}/payload-validation-test'

@Test()
def appRun_whenEnvironmentIsLocalFromLocalConfig_withSuccess_0() :
    # arrange
    muteLogs = False
    serverPort = 5001
    process = getProcess(
        f'flask run --host=localhost --port={serverPort}',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    BASE_URL = f'http://localhost:{serverPort}/local-test-api'
    payload = {'me':'and you'}
    payloadList = [payload]
    time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

    # act
    responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER)

    responseGetNone = requests.get(BASE_URL + GET_NONE_ONE)
    responseGetNoneBatch = requests.post(BASE_URL + GET_NONE_ONE_BATCH, json=payload)

    responsePostSendPayload = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payload)
    responsePostSendPayloadList = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payloadList)
    responsePostSendPayloadBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payload)
    responsePostSendPayloadListBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payloadList)

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

@Test()
def appRun_whenEnvironmentIsLocalFromLocalConfig_withSuccess_1() :
    # arrange
    muteLogs = False
    serverPort = 5002
    process = getProcess(
        f'flask run --host=localhost --port={serverPort}',
        f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
        muteLogs = muteLogs
    )
    BASE_URL = f'http://localhost:{serverPort}/local-test-api'
    time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)

    # act
    responseGetHealth = requests.post(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER_TEST, json={'status': 'UP'})

    # assert
    assert ObjectHelper.equals(
        [{'status':'UP'}],
        responseGetHealth.json()
    )
    assert 200 == responseGetHealth.status_code

    killProcesses(process)


# @Test()
# def appRun_whenEnvironmentIsLocalFromLocalConfig_withSuccess_2() :
#     # arrange
#     muteLogs = False
#     serverPort = 5003
#     process = getProcess(
#         f'flask run --host=localhost --port={serverPort}',
#         f'{CURRENT_PATH}{EnvironmentHelper.OS_SEPARATOR}apitests{EnvironmentHelper.OS_SEPARATOR}testone',
#         muteLogs = muteLogs
#     )
#     BASE_URL = f'http://localhost:{serverPort}/local-test-api'
#     payload = {'me':'and you'}
#     payloadList = [payload]
#     time.sleep(ESTIMATED_BUILD_TIME_IN_SECONDS)
#
#     # act
#     responseGetHealth = requests.get(BASE_URL + GET_ACTUATOR_HEALTH_CONTROLLER)
#
#     responseGetNone = requests.get(BASE_URL + GET_NONE_ONE)
#     responseGetNoneBatch = requests.post(BASE_URL + GET_NONE_ONE_BATCH, json=payload)
#
#     responsePostSendPayload = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payload)
#     responsePostSendPayloadList = requests.post(BASE_URL + POST_PAYLOAD_ONE, json=payloadList)
#     responsePostSendPayloadBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payload)
#     responsePostSendPayloadListBatch = requests.post(BASE_URL + POST_PAYLOAD_ONE_BATCH, json=payloadList)
#
#     # assert
#     assert ObjectHelper.equals(
#         {'status':'UP'},
#         responseGetHealth.json()
#     )
#     assert 200 == responseGetHealth.status_code
#
#     {'message': 'OK'}
#     {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.299735'}
#     {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'}
#     {'me': 'and you'}
#     {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.636759'}
#     {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.767735'}
#     assert ObjectHelper.equals(
#         {'message': 'OK'},
#         responseGetNone.json()
#     )
#     assert 200 == responseGetNone.status_code
#     assert ObjectHelper.equals(
#         {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.299735'},
#         responseGetNoneBatch.json(),
#         ignoreKeyList=['timestamp']
#     )
#     assert 500 == responseGetNoneBatch.status_code
#     assert ObjectHelper.equals(
#         {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.405736'},
#         responsePostSendPayload.json(),
#         ignoreKeyList=['timestamp']
#     )
#     assert 400 == responsePostSendPayload.status_code
#     assert ObjectHelper.equals(
#         {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-19 08:36:20.925177'},
#         responsePostSendPayloadList.json(),
#         ignoreKeyList=['timestamp']
#     )
#     assert 500 == responsePostSendPayloadList.status_code
#     assert ObjectHelper.equals(
#         {'message': 'Something bad happened. Please, try again later', 'timestamp': '2021-03-18 21:43:47.636759'},
#         responsePostSendPayloadBatch.json(),
#         ignoreKeyList=['timestamp']
#     )
#     assert 500 == responsePostSendPayloadBatch.status_code
#     assert ObjectHelper.equals(
#         {'message': 'Bad request', 'timestamp': '2021-03-18 21:43:47.767735'},
#         responsePostSendPayloadListBatch.json(),
#         ignoreKeyList=['timestamp']
#     )
#     assert 400 == responsePostSendPayloadListBatch.status_code
#
#     killProcesses(process)
