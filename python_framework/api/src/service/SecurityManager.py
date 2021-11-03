import flask_jwt_extended
from flask_jwt_extended import (
    JWTManager,
    get_raw_jwt,
    jwt_required,
    get_current_user,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required
)

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, ReflectionHelper
import datetime

from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getRawJwt(*arg,**kwargs) :
    return get_raw_jwt(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt):
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt):
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def jwtRequired(*arg,**kwargs) :
    return jwt_required(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(*arg, rawJwt=None, **kwargs) :
    if ObjectHelper.isNone(rawJwt):
        return getRawJwt(*arg,**kwargs).get(JwtConstant.KW_JTI)
    else:
        return rawJwt.get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders(*arg,**kwargs):
    headers = get_jwt_header(*arg,**kwargs)
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(*arg, rawJwt=None, **kwargs) :
    if ObjectHelper.isNone(rawJwt):
        return getRawJwt(*arg,**kwargs).get(JwtConstant.KW_IDENTITY)
    else:
        return rawJwt.get(JwtConstant.KW_IDENTITY)

@Function
def addUserToBlackList() :
    BLACK_LIST.add(getJti())

@Function
def getJwtMannager(
    appInstance,
    jwtSecret,
    headerName=JwtConstant.DEFAULT_JWT_AUTHORIZATION_HEADER_NAME,
    headerType=JwtConstant.DEFAULT_JWT_AUTHORIZATION_HEADER_TYPE
) :
    if not jwtSecret :
        log.warning(getJwtMannager, f'Not possible to instanciate jwtManager{c.DOT_SPACE_CAUSE}Missing jwt secret')
    else :
        jwtMannager = JWTManager(appInstance)
        appInstance.config[JwtConstant.KW_JWT_SECRET_KEY] = jwtSecret
        appInstance.config[JwtConstant.KW_JWT_BLACKLIST_ENABLED] = True
        appInstance.config[JwtConstant.JWT_HEADER_NAME] = headerName
        appInstance.config[JwtConstant.JWT_HEADER_TYPE] = headerType
        return jwtMannager

@Function
def addJwt(jwtInstance) :
    @jwtInstance.token_in_blacklist_loader
    def verifyAuthorizaionAccess(decriptedToken) :
        return decriptedToken[JwtConstant.KW_JTI] in BLACK_LIST

    @jwtInstance.revoked_token_loader
    def invalidAccess() :
        return {'message': 'Access denied'}, HttpStatus.UNAUTHORIZED

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, roleList, deltaMinutes=None, headers=None, data=None) :
    ###- datetime.datetime.utcnow()
    if deltaMinutes :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_access_token
    return create_access_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: roleList,
            JwtConstant.KW_DATA: data
        },
        fresh = False,
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, roleList, deltaMinutes=None, headers=None, data=None) :
    ###- datetime.datetime.utcnow()
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_refresh_token
    return create_refresh_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: roleList,
            JwtConstant.KW_DATA: data
        },
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentUser(*args, userClass=None, **kwargs):
    currentUsert = get_current_user()
    if ObjectHelper.isNotNone(currentUsert):
        return currentUsert
    else:
        rawJwt = getRawJwt(*args, **kwargs)
        identity, context = getIdentityAndContextFromRawJwt(rawJwt)
        if ObjectHelper.isNone(userClass):
            return {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context,
                JwtConstant.KW_DATA: getData(rawJwt)
            }
        else:
            currentUsert = userClass()
            currentUsert._authorizationInfo = {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context
            }
            data = getData(rawJwt)
            for attributeName in data:
                if ReflectionHelper.hasAttributeOrMethod(currentUsert, attributeName):
                    ReflectionHelper.setAttributeOrMethod(currentUsert, attributeName, data.get(attributeName))
            return currentUsert

def getIdentityAndContextFromRawJwt(rawJwt):
    identity = rawJwt.get(JwtConstant.KW_IDENTITY)
    context = getContext(rawJwt)
    return identity, context

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
@jwtRequired
def validateSecuredControllerMethod(
    args,
    kwargs,
    contentType,
    resourceInstance,
    resourceInstanceMethod,
    roleRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    logRequest
) :
    roleList = getContext(getRawJwt())
    if not any(role in set(roleList) for role in roleRequired) :
        raise GlobalException(
            message = 'Role not allowed',
            logMessage = f'''Roles {roleList} trying to access denied resourse. Allowed roles {roleRequired}''',
            status = HttpStatus.FORBIDDEN
        )
