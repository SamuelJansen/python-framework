import time
import jwt

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, ReflectionHelper, SettingHelper

from python_framework.api.src.util import UtcDateTimeUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import ConverterStatic
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
        return jwt.encode(payload, self.secret, algorithm=self.algorithm, headers=ConverterStatic.getValueOrDefault(headers, dict())).decode()

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def decode(self, encodedPayload, options=None):
        return jwt.decode(encodedPayload, self.secret, algorithms=self.algorithm, options=options if ObjectHelper.isNotNone(options) else dict())

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateAccessApiKey(self, rawJwt=None, options=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.validateGeneralApiKeyAndReturnItDecoded(rawJwt=decodedApiKeyToken, options=options)
            jwtType = getType(rawJwt=decodedApiKeyToken)
            assert jwtType == JwtConstant.ACCESS_VALUE_TYPE, f'Access apiKey should have type {JwtConstant.ACCESS_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedApiKeyToken)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateRefreshApiKey(self, rawJwt=None, options=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.validateGeneralApiKeyAndReturnItDecoded(rawJwt=decodedApiKeyToken, options=options)
            jwtType = getType(rawJwt=decodedApiKeyToken)
            assert jwtType == JwtConstant.REFRESH_VALUE_TYPE, f'Refresh apiKey should have type {JwtConstant.REFRESH_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedApiKeyToken)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateGeneralApiKeyAndReturnItDecoded(self, rawJwt=None, options=None):
        decodedApiKeyToken = rawJwt
        try:
            decodedApiKeyToken = self.getDecodedToken(rawJwt=decodedApiKeyToken, options=options)
            assert ObjectHelper.isDictionary(decodedApiKeyToken), f'Invalid apiKey payload type. It should be a dictionary, bu it is {type(decodedApiKeyToken)}'
            assert ObjectHelper.isNotEmpty(decodedApiKeyToken), 'ApiKey cannot be empty'
            jti = getJti(rawJwt=decodedApiKeyToken)
            assert not jti in BLACK_LIST, f'ApiKey {jti} already revoked'
            nbf = getNfb(rawJwt=decodedApiKeyToken)
            assert UtcDateTimeUtil.now() >= UtcDateTimeUtil.ofTimestamp(nbf), f'JWT apiKey token not valid before {UtcDateTimeUtil.ofTimestamp(nbf)}'
            expiration = getExpiration(rawJwt=decodedApiKeyToken)
            assert UtcDateTimeUtil.now() <= UtcDateTimeUtil.ofTimestamp(expiration), f'JWT apiKey token expired at {UtcDateTimeUtil.ofTimestamp(expiration)}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedApiKeyToken)
            raise exception
        return decodedApiKeyToken

    def getBody(self, rawJwt=None, options=None):
        decodedApiKeyToken = self.getDecodedToken(rawJwt=rawJwt, options=options)
        return decodedApiKeyToken

    def getUnverifiedBody(self, rawJwt=None):
        return self.getDecodedToken(rawJwt=rawJwt, options={OPTION_VERIFY_SIGNATURE: False})

    def getUnverifiedHeaders(self):
        return jwt.get_unverified_header(self.getEncodedTokenWithoutType())

    def getDecodedToken(self, rawJwt=None, options=None):
        if ObjectHelper.isNotNone(rawJwt):
            return rawJwt
        return self.decode(self.getEncodedTokenWithoutType(), options=options)

    def getEncodedTokenWithoutType(self):
        encodedPayload = self.captureTokenFromRequestHeader()
        assert ObjectHelper.isNotNone(encodedPayload), 'JWT apiKey token cannot be None'
        assert encodedPayload.startswith(f'{self.headerType} '), f'JWT apiKey token must starts with {self.headerType}'
        return encodedPayload[len(f'{self.headerType} '):].encode()

    def captureTokenFromRequestHeader(self):
        return FlaskUtil.safellyGetHeaders().get(self.headerName)

@Function
def jwtAccessRequired(function, *args, **kwargs):
    def innerFunction(*args, **kwargs):
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).apiKeyManager.validateAccessApiKey()
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@Function
def jwtRefreshRequired(function, *args, **kwargs):
    def innerFunction(*args, **kwargs):
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).apiKeyManager.validateRefreshApiKey()
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None, apiInstance=None):
    if ObjectHelper.isNone(rawJwt):
        return retrieveApiInstance(apiInstance=apiInstance).apiKeyManager.getBody(rawJwt=rawJwt)
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders(apiInstance=None):
    headers = retrieveApiInstance(apiInstance=apiInstance).apiKeyManager.getUnverifiedHeaders()
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

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
def addUserToBlackList(rawJwt=None, apiInstance=None):
    BLACK_LIST.add(getJti(rawJwt=rawJwt, apiInstance=apiInstance))

@Function
def getJwtMannager(appInstance, jwtSecret, algorithm=None, headerName=None, headerType=None):
    if not jwtSecret:
        log.warning(getJwtMannager, f'Not possible to instanciate apiKeyManager{c.DOT_SPACE_CAUSE}Missing jwt secret at {ConfigurationKeyConstant.API_API_KEY_SECRET}')
    else:
        jwtManager = JwtManager(
            jwtSecret,
            ConverterStatic.getValueOrDefault(algorithm, JwtConstant.DEFAULT_JWT_API_KEY_ALGORITHM),
            ConverterStatic.getValueOrDefault(headerName, JwtConstant.DEFAULT_JWT_API_KEY_HEADER_NAME),
            ConverterStatic.getValueOrDefault(headerType, JwtConstant.DEFAULT_JWT_API_KEY_HEADER_TYPE)
        )
        if SettingHelper.activeEnvironmentIsLocal():
            info = {
                'secret': jwtManager.secret,
                'algorithm': jwtManager.algorithm,
                'headerName': jwtManager.headerName,
                'headerType': jwtManager.headerType
            }
            log.prettyJson(getJwtMannager, f'JWT apiKey', info, logLevel=log.SETTING)
        return jwtManager

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    return retrieveApiInstance(apiInstance=apiInstance).apiKeyManager.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList if ObjectHelper.isList(contextList) else [] if ObjectHelper.isNone(contextList) else raiseApiKeyContextCannotBeNone(),
                JwtConstant.KW_DATA: data if ObjectHelper.isNotNone(data) else {}
            }
        },
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    data = Serializer.getObjectAsDictionary(data)
    return retrieveApiInstance(apiInstance=apiInstance).apiKeyManager.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.REFRESH_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList if ObjectHelper.isList(contextList) else [] if ObjectHelper.isNone(contextList) else raiseApiKeyContextCannotBeNone(),
                JwtConstant.KW_DATA: data if ObjectHelper.isNotNone(data) else {}
            }
        },
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_API_KEY_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def patchAccessToken(newContextList=None, headers=None, data=None, rawJwt=None, apiInstance=None):
    headers = headers if ObjectHelper.isNone(rawJwt) else {**getJwtHeaders(), **ConverterStatic.getValueOrDefault(headers, dict())}
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    data = Serializer.getObjectAsDictionary(data)
    userClaims = {
        JwtConstant.KW_CONTEXT: list(set([
            *getContext(rawJwt=rawJwt),
            *[
                element for element in list([] if ObjectHelper.isNone(newContextList) else newContextList)
            ]
        ])),
        JwtConstant.KW_DATA: {
            **getData(rawJwt=rawJwt),
            **{
                k: v for k, v in (data if ObjectHelper.isNotNone(data) else dict()).items()
            }
        }
    }
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    addUserToBlackList(rawJwt=rawJwt, apiInstance=apiInstance)
    return apiInstance.apiKeyManager.encode({
            JwtConstant.KW_IAT: getIat(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_NFB: UtcDateTimeUtil.now(),
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: getExpiration(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_IDENTITY: getIdentity(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: userClaims
        },
        headers = ConverterStatic.getValueOrDefault(headers, dict())
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

def addResource(apiInstance, appInstance):
    apiInstance.apiKeyManager = None
    try:
        apiInstance.apiKeyManager = getJwtMannager(
            appInstance,
            apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_SECRET),
            algorithm = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_ALGORITHM),
            headerName = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_HEADER),
            headerType = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_API_KEY_TYPE)
        )
        apiInstance.apiKeyManager.api = apiInstance
    except Exception as exception:
        log.warning(addResource, 'Not possible to add ApiKeyManager', exception=exception)
    if ObjectHelper.isNotNone(apiInstance.apiKeyManager):
        log.success(initialize, 'ApiKeyManager created')
    return apiInstance.apiKeyManager

def initialize(apiInstance, appInstance):
    if ObjectHelper.isNotNone(apiInstance.apiKeyManager):
        log.success(initialize, 'ApiKeyManager is running')

def onHttpRequestCompletion(apiInstance, appInstance):
    # @appInstance.teardown_appcontext
    # def methodNameMustBeUnique(error):
    #       do something here
    ...

def shutdown(apiInstance, apiInstance):
    log.success(shutdown, 'ApiKeyManager successfully closed')

def onShutdown(apiInstance, apiInstance):
    import atexit
    atexit.register(lambda: shutdown(apiInstance, apiInstance))

def retrieveApiInstance(apiInstance=None, arguments=None):
    apiInstance = FlaskUtil.retrieveApiInstance(apiInstance=apiInstance, arguments=arguments)
    if ObjectHelper.isNone(apiInstance.apiKeyManager):
        raise Exception('There is no api key manager')
    return apiInstance

def raiseApiKeyContextCannotBeNone():
    raise Exception('Context cannot be None')

def getNewJti():
    return Serializer.newUuidAsString()
