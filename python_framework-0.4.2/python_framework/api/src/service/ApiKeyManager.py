import time
import jwt

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, ReflectionHelper, SettingHelper

from python_framework.api.src.util import UtcDateTimeUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


OPTION_VERIFY_SIGNATURE = 'verify_signature'
BLACK_LIST = set()


class JwtManager:

    def __init__(self, jwtSecret, algorithm, headerName, headerType):
        self.secret = jwtSecret
        self.algorithm = algorithm
        self.headerName = headerName
        self.headerType = headerType

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def encode(self, payload, headers=None):
        return jwt.encode(payload, self.secret, algorithm=self.algorithm, headers=StaticConverter.getValueOrDefault(headers, dict()))

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def decode(self, encodedPayload, options=None):
        return jwt.decode(encodedPayload, self.secret, algorithms=self.algorithm, options=options if ObjectHelper.isNotNone(options) else dict())

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateAccessApiKey(self, rawJwt=None, options=None, requestHeaders=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.validateGeneralApiKeyAndReturnItDecoded(rawJwt=decodedApiKeyToken, options=options, requestHeaders=requestHeaders)
            jwtType = getType(rawJwt=decodedApiKeyToken)
            assert jwtType == JwtConstant.ACCESS_VALUE_TYPE, f'Access api key should have type {JwtConstant.ACCESS_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addAccessTokenToBlackList(rawJwt=decodedApiKeyToken)
            log.log(self.validateAccessApiKey, f'Adding {rawJwt} (or current accces) to blackList', exception=exception, muteStackTrace=True)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateRefreshApiKey(self, rawJwt=None, options=None, requestHeaders=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.validateGeneralApiKeyAndReturnItDecoded(rawJwt=decodedApiKeyToken, options=options, requestHeaders=requestHeaders)
            jwtType = getType(rawJwt=decodedApiKeyToken)
            assert jwtType == JwtConstant.REFRESH_VALUE_TYPE, f'Refresh api key should have type {JwtConstant.REFRESH_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addAccessTokenToBlackList(rawJwt=decodedApiKeyToken)
            log.log(self.validateRefreshApiKey, f'Adding {rawJwt} (or current accces) to blackList', exception=exception, muteStackTrace=True)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateGeneralApiKeyAndReturnItDecoded(self, rawJwt=None, options=None, requestHeaders=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.getDecodedToken(rawJwt=decodedApiKeyToken, options=options, requestHeaders=requestHeaders)
            assert ObjectHelper.isDictionary(decodedApiKeyToken), f'Invalid api key payload type. It should be a dictionary, bu it is {type(decodedApiKeyToken)}'
            assert ObjectHelper.isNotEmpty(decodedApiKeyToken), 'ApiKey cannot be empty'
            jti = getJti(rawJwt=decodedApiKeyToken)
            assert ObjectHelper.isNotNone(jti), f'JWT jti cannot be None'
            assert jti not in BLACK_LIST, f'ApiKey {jti} already revoked'
            nbf = getNfb(rawJwt=decodedApiKeyToken)
            assert ObjectHelper.isNotNone(nbf), f'JWT nbf cannot be None'
            assert UtcDateTimeUtil.now() >= UtcDateTimeUtil.ofTimestamp(nbf), f'JWT api key token not valid before {UtcDateTimeUtil.ofTimestamp(nbf)}'
            expiration = getExpiration(rawJwt=decodedApiKeyToken)
            assert UtcDateTimeUtil.now() <= UtcDateTimeUtil.ofTimestamp(expiration), f'JWT api key token expired at {UtcDateTimeUtil.ofTimestamp(expiration)}'
        except Exception as exception:
            addAccessTokenToBlackList(rawJwt=decodedApiKeyToken)
            log.log(self.validateGeneralApiKeyAndReturnItDecoded, f'Adding {rawJwt} (or current accces) to blackList', exception=exception, muteStackTrace=True)
            raise exception
        return decodedApiKeyToken

    def getBody(self, rawJwt=None, options=None, requestHeaders=None):
        decodedApiKeyToken = self.getDecodedToken(rawJwt=rawJwt, options=options, requestHeaders=requestHeaders)
        return decodedApiKeyToken

    def getUnverifiedBody(self, rawJwt=None, requestHeaders=None):
        return self.getDecodedToken(rawJwt=rawJwt, options={OPTION_VERIFY_SIGNATURE: False}, requestHeaders=requestHeaders)

    def getUnverifiedHeaders(self, requestHeaders=None):
        return jwt.get_unverified_header(self.getEncodedTokenWithoutType(requestHeaders=requestHeaders))

    def getDecodedToken(self, rawJwt=None, options=None, requestHeaders=None):
        if ObjectHelper.isNotNone(rawJwt):
            return rawJwt
        return self.decode(self.getEncodedTokenWithoutType(requestHeaders=requestHeaders), options=options)

    def getEncodedTokenWithoutType(self, requestHeaders=None):
        encodedPayload = self.captureTokenFromRequestHeader(requestHeaders=requestHeaders)
        assert ObjectHelper.isNotNone(encodedPayload), f'JWT api key token cannot be None. Header: {self.headerName}'
        assert encodedPayload.startswith(f'{self.headerType} '), f'JWT api key token must starts with {self.headerType}'
        return encodedPayload[len(f'{self.headerType} '):].encode()

    def captureTokenFromRequestHeader(self, requestHeaders=None):
        if ObjectHelper.isNotEmpty(requestHeaders):
            return requestHeaders.get(self.headerName)
        return FlaskUtil.safellyGetHeaders().get(self.headerName)

def getRequestHeaders(kwargs):
    return kwargs.get('requestHeaders')

@Function
def jwtAccessRequired(function, *args, **kwargs):
    def innerFunction(*args, **kwargs):
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).resource.manager.apiKey.validateAccessApiKey(requestHeaders=getRequestHeaders(kwargs))
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@Function
def jwtRefreshRequired(function, *args, **kwargs):
    def innerFunction(*args, **kwargs):
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).resource.manager.apiKey.validateRefreshApiKey(requestHeaders=getRequestHeaders(kwargs))
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None, apiInstance=None, requestHeaders=None):
    if ObjectHelper.isNone(rawJwt):
        return retrieveApiInstance(apiInstance=apiInstance).resource.manager.apiKey.getBody(rawJwt=rawJwt, requestHeaders=requestHeaders)
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders(apiInstance=None, requestHeaders=None):
    headers = retrieveApiInstance(apiInstance=apiInstance).resource.manager.apiKey.getUnverifiedHeaders(requestHeaders=requestHeaders)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None, apiInstance=None, requestHeaders=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance, requestHeaders=requestHeaders)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT, [])

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(rawJwt=None, apiInstance=None):
    ###- unique identifier
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIat(rawJwt=None, apiInstance=None):
    ###- issued at
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IAT)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getNfb(rawJwt=None, apiInstance=None):
    ###- not valid before
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_NFB)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getExpiration(rawJwt=None, apiInstance=None):
    ###- expiration time
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_EXPIRATION)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IDENTITY)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getType(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_TYPE)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIsFresh(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_FRESH)

@Function
def addAccessTokenToBlackList(rawJwt=None, apiInstance=None):
    BLACK_LIST.add(getJti(rawJwt=rawJwt, apiInstance=apiInstance))

@Function
def getJwtMannager(appInstance, jwtSecret, algorithm=None, headerName=None, headerType=None):
    if not jwtSecret:
        log.warning(getJwtMannager, f'Not possible to instanciate manager.apiKey{c.DOT_SPACE_CAUSE}Missing jwt secret at {ConfigurationKeyConstant.API_API_KEY_SECRET}')
    else:
        jwtManager = JwtManager(
            jwtSecret,
            StaticConverter.getValueOrDefault(algorithm, JwtConstant.DEFAULT_JWT_API_KEY_ALGORITHM),
            StaticConverter.getValueOrDefault(headerName, JwtConstant.DEFAULT_JWT_API_KEY_HEADER_NAME),
            StaticConverter.getValueOrDefault(headerType, JwtConstant.DEFAULT_JWT_API_KEY_HEADER_TYPE)
        )
        if SettingHelper.activeEnvironmentIsLocal():
            info = {
                'secret': jwtManager.secret,
                'algorithm': jwtManager.algorithm,
                'headerName': jwtManager.headerName,
                'headerType': jwtManager.headerType
            }
            log.prettyJson(getJwtMannager, f'JWT api key', info, logLevel=log.SETTING)
        return jwtManager

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    return retrieveApiInstance(apiInstance=apiInstance).resource.manager.apiKey.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: safellyGetContext(contextList),
                JwtConstant.KW_DATA: safellyGetData(data)
            }
        },
        headers = StaticConverter.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    return retrieveApiInstance(apiInstance=apiInstance).resource.manager.apiKey.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.REFRESH_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: safellyGetContext(contextList),
                JwtConstant.KW_DATA: safellyGetData(data)
            }
        },
        headers = StaticConverter.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def patchAccessToken(newContextList=None, headers=None, data=None, rawJwt=None, apiInstance=None):
    headers = headers if ObjectHelper.isNone(rawJwt) else {**getJwtHeaders(), **StaticConverter.getValueOrDefault(headers, dict())}
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    userClaims = {
        JwtConstant.KW_CONTEXT: list(set([
            *safellyGetContext(getContext(rawJwt=rawJwt)),
            *safellyGetContext(newContextList)
        ])),
        JwtConstant.KW_DATA: {
            **safellyGetData(getData(rawJwt=rawJwt)),
            **safellyGetData(data)
        }
    }
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    addAccessTokenToBlackList(rawJwt=rawJwt, apiInstance=apiInstance)
    return apiInstance.resource.manager.apiKey.encode({
            JwtConstant.KW_IAT: getIat(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_NFB: UtcDateTimeUtil.now(),
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: getExpiration(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_IDENTITY: getIdentity(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: userClaims
        },
        headers = StaticConverter.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentApiKey(apiKeyClass=None, apiInstance=None):
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    rawJwt = getJwtBody(apiInstance=apiInstance)
    identity = getIdentity(rawJwt=rawJwt, apiInstance=apiInstance)
    context = getContext(rawJwt=rawJwt, apiInstance=apiInstance)
    data = getData(rawJwt=rawJwt, apiInstance=apiInstance)
    if ObjectHelper.isNone(apiKeyClass):
        return {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context,
            JwtConstant.KW_DATA: data
        }
    else:
        currentApiKey = apiKeyClass()
        currentApiKey._contextInfo = {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context
        }
        for attributeName in data:
            if ReflectionHelper.hasAttributeOrMethod(currentApiKey, attributeName):
                ReflectionHelper.setAttributeOrMethod(currentApiKey, attributeName, data.get(attributeName))
        return currentApiKey

def getContextData(dataClass=None, apiInstance=None):
    return getCurrentApiKey(apiKeyClass=dataClass, apiInstance=apiInstance)

def addResource(apiInstance, appInstance):
    apiInstance.resource.manager.apiKey = None
    try:
        apiInstance.resource.manager.apiKey = getJwtMannager(
            appInstance,
            apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_SECRET),
            algorithm = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_ALGORITHM),
            headerName = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_HEADER),
            headerType = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_TYPE)
        )
        apiInstance.resource.manager.apiKey.api = apiInstance
    except Exception as exception:
        log.warning(addResource, 'Not possible to add ApiKeyManager', exception=exception)
    if ObjectHelper.isNotNone(apiInstance.resource.manager.apiKey):
        log.status(initialize, 'ApiKeyManager created')
    return apiInstance.resource.manager.apiKey

def initialize(apiInstance, appInstance):
    if ObjectHelper.isNotNone(apiInstance.resource.manager.apiKey):
        log.success(initialize, 'ApiKeyManager is running')

def onHttpRequestCompletion(apiInstance, appInstance):
    # @appInstance.teardown_appcontext
    # def methodNameMustBeUnique(error):
    #       do something here
    ...

def shutdown(apiInstance, appInstance):
    if ObjectHelper.isNotNone(apiInstance.resource.manager.apiKey):
        log.success(shutdown, 'ApiKeyManager successfully closed')

def onRun(apiInstance, appInstance):
    ...

def onShutdown(apiInstance, appInstance):
    import atexit
    atexit.register(lambda: shutdown(apiInstance, appInstance))

def retrieveApiInstance(apiInstance=None, arguments=None):
    apiInstance = FlaskUtil.retrieveApiInstance(apiInstance=apiInstance, arguments=arguments)
    if not ReflectionHelper.hasAttributeOrMethod(apiInstance.resource.manager, 'apiKey') or ObjectHelper.isNone(apiInstance.resource.manager.apiKey):
        raise Exception('There is no api key manager')
    return apiInstance

def raiseSessionContextCannotBeNone():
    raise Exception('Api key context cannot be None')

def safellyGetContext(contextList):
    return [] if ObjectHelper.isNone(contextList) else Serializer.getObjectAsDictionary(contextList) if ObjectHelper.isList(contextList) else raiseSessionContextCannotBeNone()

def safellyGetData(data):
    return dict() if ObjectHelper.isNone(data) else Serializer.getObjectAsDictionary(data)

def getNewJti():
    return Serializer.newUuidAsString()
