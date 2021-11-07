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
KEY_API_INSTANCE = 'apiInstance'
API_INSTANCE_HOLDER = {
    KEY_API_INSTANCE: None
}
BLACK_LIST = set()


class JwtManager:

    def __init__(self, jwtSecret, algorithm, headerName, headerType):
        self.secret = jwtSecret
        self.algorithm = algorithm
        self.headerName = headerName
        self.headerType = headerType

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def encode(self, payload, headers=None) :
        return jwt.encode(payload, self.secret, algorithm=self.algorithm, headers=ConverterStatic.getValueOrDefault(headers, dict())).decode()

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def decode(self, encodedPayload, options=None) :
        return jwt.decode(encodedPayload, self.secret, algorithms=self.algorithm, options=options if ObjectHelper.isNotNone(options) else dict())

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateAccessSession(self, rawJwt=None, options=None):
        decodedSessionToken = rawJwt
        try:
            decodedSessionToken = self.validateGeneralSessionAndReturnItDecoded(rawJwt=decodedSessionToken, options=options)
            jwtType = getType(rawJwt=decodedSessionToken)
            assert jwtType == JwtConstant.ACCESS_VALUE_TYPE, f'Access session should have type {JwtConstant.ACCESS_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedSessionToken)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateRefreshSession(self, rawJwt=None, options=None):
        decodedSessionToken = rawJwt
        try:
            decodedSessionToken = self.validateGeneralSessionAndReturnItDecoded(rawJwt=decodedSessionToken, options=options)
            jwtType = getType(rawJwt=decodedSessionToken)
            assert jwtType == JwtConstant.REFRESH_VALUE_TYPE, f'Refresh session should have type {JwtConstant.REFRESH_VALUE_TYPE}, but it is {jwtType}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedSessionToken)
            raise exception

    @EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateGeneralSessionAndReturnItDecoded(self, rawJwt=None, options=None):
        decodedSessionToken = rawJwt
        try:
            decodedSessionToken = self.getDecodedToken(rawJwt=decodedSessionToken, options=options)
            assert ObjectHelper.isDictionary(decodedSessionToken), f'Invalid session payload type. It should be a dictionary, bu it is {type(decodedSessionToken)}'
            assert ObjectHelper.isNotEmpty(decodedSessionToken), 'Session cannot be empty'
            jti = getJti(rawJwt=decodedSessionToken)
            assert not jti in BLACK_LIST, f'Session {jti} already revoked'
            nbf = getNfb(rawJwt=decodedSessionToken)
            assert UtcDateTimeUtil.now() >= UtcDateTimeUtil.ofTimestamp(nbf), f'JWT session token not valid before {UtcDateTimeUtil.ofTimestamp(nbf)}'
            expiration = getExpiration(rawJwt=decodedSessionToken)
            assert UtcDateTimeUtil.now() <= UtcDateTimeUtil.ofTimestamp(expiration), f'JWT session token expired at {UtcDateTimeUtil.ofTimestamp(expiration)}'
        except Exception as exception:
            addUserToBlackList(rawJwt=decodedSessionToken)
            raise exception
        return decodedSessionToken

    def getBody(self, rawJwt=None, options=None):
        decodedSessionToken = self.getDecodedToken(rawJwt=rawJwt, options=options)
        return decodedSessionToken

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
        assert ObjectHelper.isNotNone(encodedPayload), 'JWT session token cannot be None'
        assert encodedPayload.startswith(f'{self.headerType} '), f'JWT session token must starts with {self.headerType}'
        return encodedPayload[len(f'{self.headerType} '):].encode()

    def captureTokenFromRequestHeader(self):
        return FlaskUtil.safellyGetHeaders().get(self.headerName)

@Function
def jwtAccessRequired(function, *args, **kwargs) :
    def innerFunction(*args, **kwargs) :
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).sessionManager.validateAccessSession()
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@Function
def jwtRefreshRequired(function, *args, **kwargs) :
    def innerFunction(*args, **kwargs) :
        ###- arguments=args[0] --> python weardnes in it's full glory
        retrieveApiInstance(arguments=args[0]).sessionManager.validateRefreshSession()
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None, apiInstance=None) :
    if ObjectHelper.isNone(rawJwt):
        return retrieveApiInstance(apiInstance=apiInstance).sessionManager.getBody(rawJwt=rawJwt)
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders(apiInstance=None):
    headers = retrieveApiInstance(apiInstance=apiInstance).sessionManager.getUnverifiedHeaders()
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(rawJwt=None, apiInstance=None) :
    ###- unique identifier
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIat(rawJwt=None, apiInstance=None) :
    ###- issued at
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IAT)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getNfb(rawJwt=None, apiInstance=None) :
    ###- not valid before
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_NFB)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getExpiration(rawJwt=None, apiInstance=None) :
    ###- expiration time
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_EXPIRATION)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(rawJwt=None, apiInstance=None) :
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IDENTITY)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getType(rawJwt=None, apiInstance=None) :
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_TYPE)

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIsFresh(rawJwt=None, apiInstance=None) :
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_FRESH)

@Function
def addUserToBlackList(rawJwt=None, apiInstance=None) :
    BLACK_LIST.add(getJti(rawJwt=rawJwt, apiInstance=apiInstance))

@Function
def getJwtMannager(appInstance, jwtSecret, algorithm=None, headerName=None, headerType=None):
    if SettingHelper.activeEnvironmentIsLocal():
        log.setting(getJwtMannager, f'JWT session secret: {jwtSecret}')
    if not jwtSecret:
        log.warning(getJwtMannager, f'Not possible to instanciate sessionManager{c.DOT_SPACE_CAUSE}Missing jwt secret at {ConfigurationKeyConstant.API_SESSION_SECRET}')
    else:
        return JwtManager(
            jwtSecret,
            ConverterStatic.getValueOrDefault(algorithm, JwtConstant.DEFAULT_JWT_SESSION_ALGORITHM),
            ConverterStatic.getValueOrDefault(headerName, JwtConstant.DEFAULT_JWT_SESSION_HEADER_NAME),
            ConverterStatic.getValueOrDefault(headerType, JwtConstant.DEFAULT_JWT_SESSION_HEADER_TYPE)
        )

@Function
def addJwt(jwtInstance) :
    ...

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    data = Serializer.getObjectAsDictionary(data)
    return retrieveApiInstance(apiInstance=apiInstance).sessionManager.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList if ObjectHelper.isList(contextList) else [] if ObjectHelper.isNone(contextList) else raiseSessionContextCannotBeNone(),
                JwtConstant.KW_DATA: data if ObjectHelper.isNotNone(data) else {}
            }
        },
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, contextList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    timeNow = UtcDateTimeUtil.now()
    data = Serializer.getObjectAsDictionary(data)
    return retrieveApiInstance(apiInstance=apiInstance).sessionManager.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: getNewJti(),
            JwtConstant.KW_EXPIRATION: UtcDateTimeUtil.plusMinutes(timeNow, minutes=deltaMinutes),
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.REFRESH_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList if ObjectHelper.isList(contextList) else [] if ObjectHelper.isNone(contextList) else raiseSessionContextCannotBeNone(),
                JwtConstant.KW_DATA: data if ObjectHelper.isNotNone(data) else {}
            }
        },
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
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
    return apiInstance.sessionManager.encode({
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

@EncapsulateItWithGlobalException(message=JwtConstant.INVALID_SESSION_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentSession(sessionClass=None, apiInstance=None):
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    rawJwt = getJwtBody(apiInstance=apiInstance)
    identity = getIdentity(rawJwt=rawJwt, apiInstance=apiInstance)
    context = getContext(rawJwt=rawJwt, apiInstance=apiInstance)
    data = getData(rawJwt=rawJwt, apiInstance=apiInstance)
    if ObjectHelper.isNone(sessionClass):
        return {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context,
            JwtConstant.KW_DATA: data
        }
    else:
        currentSession = sessionClass()
        currentSession._contextInfo = {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context
        }
        for attributeName in data:
            if ReflectionHelper.hasAttributeOrMethod(currentSession, attributeName):
                ReflectionHelper.setAttributeOrMethod(currentSession, attributeName, data.get(attributeName))
        return currentSession

def addSessionManager(apiInstance, appInstance):
    apiInstance.sessionManager = None
    try:
        apiInstance.sessionManager = getJwtMannager(
            appInstance,
            apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SESSION_SECRET),
            algorithm = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SESSION_ALGORITHM),
            headerName = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SESSION_HEADER),
            headerType = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SESSION_TYPE)
        )
        apiInstance.sessionManager.api = apiInstance
    except Exception as exception:
        log.warning(addSessionManager, 'Not possible to add SessionManager', exception=exception)

def retrieveApiInstance(apiInstance=None, arguments=None):
    apiInstance = FlaskUtil.retrieveApiInstance(apiInstance=apiInstance, arguments=arguments)
    if ObjectHelper.isNone(apiInstance.sessionManager):
        raise Exception('There is no session manager')
    return apiInstance

def raiseSessionContextCannotBeNone():
    raise Exception('Context cannot be None')

def getNewJti():
    return Serializer.newUuid()
