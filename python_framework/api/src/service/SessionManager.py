from flask_jwt_extended import get_current_user
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)
from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper
import datetime

from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(*arg,**kwargs) :
    return get_raw_jwt(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def jwtRequired(*arg,**kwargs) :
    return jwt_required(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(*arg,**kwargs) :
    return getJwtBody(*arg,**kwargs)[JwtConstant.KW_JTI]

@EncapsulateItWithGlobalException(message=JwtConstant.FORBIDDEN_MESSAGE, status=HttpStatus.FORBIDDEN)
def getGroup(*arg,**kwargs) :
    return getJwtBody(*arg,**kwargs)[JwtConstant.KW_CLAIMS]

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(*arg,**kwargs) :
    return getJwtBody(*arg,**kwargs)[JwtConstant.KW_IDENTITY]

@Function
def addUserToBlackList() :
    BLACK_LIST.add(getJti())

@Function
def getJwtMannager(
    appInstance,
    jwtSecret,
    headerName=JwtConstant.DEFAULT_JWT_SESSION_HEADER_NAME,
    headerType=JwtConstant.DEFAULT_JWT_SESSION_HEADER_TYPE
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
def createAccessToken(session, deltaMinutes=None, headers=None) :
    ###- datetime.datetime.utcnow()
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    return create_access_token(
        identity = session.id,
        fresh = False,
        expires_delta = deltaMinutes,
        user_claims = session.role,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(session, deltaMinutes=None, headers=None) :
    ###- datetime.datetime.utcnow()
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    return create_refresh_token(
        identity = session.id,
        fresh = False,
        expires_delta = deltaMinutes,
        user_claims = session.role,
        headers = headers
    )
