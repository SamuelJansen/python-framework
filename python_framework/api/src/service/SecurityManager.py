from flask_jwt_extended import (
    JWTManager,
    get_raw_jwt,
    jwt_required,
    get_current_user,
    get_jwt_identity,
    get_raw_jwt_header,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required
)

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, ReflectionHelper, SettingHelper, DateTimeHelper

from python_framework.api.src.util import UtcDateTimeUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import ConverterStatic
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None, apiInstance=None):
    if ObjectHelper.isNone(rawJwt):
        return get_raw_jwt()
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders():
    headers = get_raw_jwt_header()
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIat(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IAT)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getNfb(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_NFB)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getExpiration(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_EXPIRATION)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(rawJwt=None, apiInstance=None):
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IDENTITY)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def jwtAccessRequired(*arg,**kwargs):
    return jwt_required(*arg,**kwargs)

@Function
def addUserToBlackList(rawJwt=None, apiInstance=None):
    BLACK_LIST.add(getJti(rawJwt=rawJwt, apiInstance=apiInstance))

@Function
def getJwtMannager(appInstance, jwtSecret, algorithm=None, headerName=None, headerType=None):
    if ObjectHelper.isNone(jwtSecret):
        log.warning(getJwtMannager, f'Not possible to instanciate securityManager{c.DOT_SPACE_CAUSE}Missing jwt secret at {ConfigurationKeyConstant.API_SECURITY_SECRET}')
    else:
        jwtMannager = JWTManager(appInstance)
        appInstance.config[JwtConstant.KW_JWT_SECRET_KEY] = jwtSecret
        appInstance.config[JwtConstant.KW_JWT_BLACKLIST_ENABLED] = True
        appInstance.config[JwtConstant.KW_JWT_ALGORITHM] = ConverterStatic.getValueOrDefault(algorithm, JwtConstant.DEFAULT_JWT_SECURITY_ALGORITHM)
        appInstance.config[JwtConstant.KW_JWT_HEADER_NAME] = ConverterStatic.getValueOrDefault(headerName, JwtConstant.DEFAULT_JWT_SECURITY_HEADER_NAME)
        appInstance.config[JwtConstant.KW_JWT_HEADER_TYPE] = ConverterStatic.getValueOrDefault(headerType, JwtConstant.DEFAULT_JWT_SECURITY_HEADER_TYPE)
        if SettingHelper.activeEnvironmentIsLocal():
            info = {
                'secret': jwtSecret,
                'algorithm': appInstance.config[JwtConstant.KW_JWT_ALGORITHM],
                'headerName': appInstance.config[JwtConstant.KW_JWT_HEADER_NAME],
                'headerType': appInstance.config[JwtConstant.KW_JWT_HEADER_TYPE]
            }
            log.prettyJson(getJwtMannager, f'JWT security', info, logLevel=log.SETTING)
        return jwtMannager

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, roleList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_access_token
    data = Serializer.getObjectAsDictionary(data)
    return create_access_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: ConverterStatic.getValueOrDefault(roleList, list()),
            JwtConstant.KW_DATA: ConverterStatic.getValueOrDefault(data, dict())
        },
        fresh = False,
        expires_delta = DateTimeHelper.timeDelta(minutes=deltaMinutes),
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, roleList, deltaMinutes=0, headers=None, data=None, apiInstance=None):
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_refresh_token
    data = Serializer.getObjectAsDictionary(data)
    return create_refresh_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: roleList,
            JwtConstant.KW_DATA: data
        },
        expires_delta = DateTimeHelper.timeDelta(minutes=deltaMinutes),
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def patchAccessToken(newContextList=None, headers=None, data=None, rawJwt=None, apiInstance=None):
    headers = headers if ObjectHelper.isNone(rawJwt) else {**getJwtHeaders(), **ConverterStatic.getValueOrDefault(headers, dict())}
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    deltaMinutes = UtcDateTimeUtil.ofTimestamp(getExpiration(rawJwt=rawJwt)) - UtcDateTimeUtil.now()
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
    addUserToBlackList(rawJwt=rawJwt, apiInstance=apiInstance)
    return create_access_token(
        identity = getIdentity(rawJwt=rawJwt),
        user_claims = userClaims,
        fresh = False,
        expires_delta = deltaMinutes,
        headers = ConverterStatic.getValueOrDefault(headers, dict())
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentUser(userClass=None, apiInstance=None):
    currentUsert = get_current_user()
    if ObjectHelper.isNotNone(currentUsert):
        return currentUsert
    else:
        rawJwt = getJwtBody()
        identity = getIdentity(rawJwt=rawJwt)
        context = getContext(rawJwt=rawJwt)
        data = getData(rawJwt=rawJwt)
        if ObjectHelper.isNone(userClass):
            return {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context,
                JwtConstant.KW_DATA: data
            }
        else:
            currentUsert = userClass()
            currentUsert._contextInfo = {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context
            }
            for attributeName in data:
                if ReflectionHelper.hasAttributeOrMethod(currentUsert, attributeName):
                    ReflectionHelper.setAttributeOrMethod(currentUsert, attributeName, data.get(attributeName))
            return currentUsert

def getContextData(dataClass=None, apiInstance=None):
    return getCurrentUser(userClass=dataClass, apiInstance=apiInstance)

def addResource(apiInstance, appInstance):
    apiInstance.securityManager = None
    try:
        apiInstance.securityManager = getJwtMannager(
            appInstance,
            apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SECURITY_SECRET),
            algorithm = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SECURITY_ALGORITHM),
            headerName = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SECURITY_HEADER),
            headerType = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SECURITY_TYPE)
        )
        apiInstance.securityManager.api = apiInstance
    except Exception as exception:
        log.warning(addResource, 'Not possible to add SecurityManager', exception=exception)
    if ObjectHelper.isNotNone(apiInstance.securityManager):
        log.success(initialize, 'SecurityManager created')
    return apiInstance.securityManager

@Function
def initialize(apiInstance, appInstance):
    @apiInstance.securityManager.token_in_blacklist_loader
    def verifyAuthorizaionAccess(decriptedToken):
        return decriptedToken[JwtConstant.KW_JTI] in BLACK_LIST

    @apiInstance.securityManager.revoked_token_loader
    def invalidAccess():
        log.log(initialize, 'Access revoked', exception=None)
        return {'message': 'Unauthorized'}, HttpStatus.UNAUTHORIZED
    if ObjectHelper.isNotNone(apiInstance.securityManager):
        log.success(initialize, 'SecurityManager is running')

def onHttpRequestCompletion(apiInstance, appInstance):
    # @appInstance.teardown_appcontext
    # def methodNameMustBeUnique(error):
    #       do something here
    ...

def shutdown(apiInstance, appInstance):
    log.success(shutdown, 'SecurityManager successfully closed')

def onShutdown(apiInstance, appInstance):
    import atexit
    atexit.register(lambda: shutdown(apiInstance, appInstance))
