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
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getRawJwt(*arg,**kwargs) :
    return get_raw_jwt(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def jwtRequired(*arg,**kwargs) :
    return jwt_required(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(*arg,**kwargs) :
    return getRawJwt(*arg,**kwargs).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.FORBIDDEN_MESSAGE, status=HttpStatus.FORBIDDEN)
def getRole(*arg,**kwargs) :
    return getRawJwt(*arg,**kwargs).get(JwtConstant.KW_CLAIMS)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(*arg,**kwargs) :
    return getRawJwt(*arg,**kwargs).get(JwtConstant.KW_IDENTITY)

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
        log.warning(JWTManager, f'Not possible to instanciate jwtManager{c.DOT_SPACE_CAUSE}Missing jwt secret')
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
def createAccessToken(user, deltaMinutes=None, headers=None) :
    ###- datetime.datetime.utcnow()
    if deltaMinutes :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    id, roleList = getIdAndRoleListFromUser(user)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_access_token
    return create_access_token(
        identity = id,
        user_claims = {
            JwtConstant.KW_CONTEXT: roleList,
            JwtConstant.KW_DATA: None
        },
        fresh = False,
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(user, deltaMinutes=None, headers=None) :
    ###- datetime.datetime.utcnow()
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    id, roleList = getIdAndRoleListFromUser(user)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_refresh_token
    return create_refresh_token(
        identity = id,
        user_claims = {
            JwtConstant.KW_CONTEXT: roleList,
            JwtConstant.KW_DATA: None
        },
        fresh = False,
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
        id, roleList = getIdAndRoleListFromRawJwt(rawJwt)
        if ObjectHelper.isNone(userClass):
            return {
                'id': id,
                'roles': roleList,
                'data': rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)
            }
        else:
            currentUsert = userClass()
            currentUsert._authorizationInfo = {
                'id': id,
                'roles': roleList
            }
            for attributeName in rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA):
                if ReflectionHelper.hasAttributeOrMethod(currentUsert, attributeName):
                    ReflectionHelper.setAttributeOrMethod(currentUsert, attributeName, rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(attributeName))
            return currentUsert

def getIdAndRoleListFromUser(user):
    id = role = None
    if ObjectHelper.isDictionary(user):
        id = user.get('id')
        role = user.get('role')
    else:
        id = user.id
        role = user.role
    return id, [role]

def getIdAndRoleListFromRawJwt(rawJwt):
    id = rawJwt.get(JwtConstant.KW_IDENTITY)
    roleList = rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)
    return id, roleList
