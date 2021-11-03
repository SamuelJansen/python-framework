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
from python_helper import log, Function, ObjectHelper, ReflectionHelper
import datetime

from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None) :
    if ObjectHelper.isNone(rawJwt):
        return get_raw_jwt()
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders():
    headers = get_raw_jwt_header()
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None):
    rawJwt = getJwtBody(rawJwt=rawJwt)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt=None):
    rawJwt = getJwtBody(rawJwt=rawJwt)
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def jwtRequired(*arg,**kwargs) :
    return jwt_required(*arg,**kwargs)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(rawJwt=None) :
    return getJwtBody(rawJwt=rawJwt).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(rawJwt=None) :
    return getJwtBody(rawJwt=rawJwt).get(JwtConstant.KW_IDENTITY)

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
def createAccessToken(identity, contextList, deltaMinutes=None, headers=None, data=None) :
    ###- datetime.datetime.utcnow()
    if deltaMinutes :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_access_token
    return create_access_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: contextList,
            JwtConstant.KW_DATA: data
        },
        fresh = False,
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, contextList, deltaMinutes=None, headers=None, data=None) :
    ###- datetime.datetime.utcnow()
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    ###- https://flask-jwt-extended.readthedocs.io/en/stable/_modules/flask_jwt_extended/utils/#create_refresh_token
    return create_refresh_token(
        identity = identity,
        user_claims = {
            JwtConstant.KW_CONTEXT: contextList,
            JwtConstant.KW_DATA: data
        },
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def patchAccessToken(newContextList=None, headers=None, data=None) :
    rawJwt = getJwtBody()
    # expiresDelta=rawJwt.get(JwtConstant.KW_EXPIRATION)
    import time
    print(time.time())
    deltaMinutes = datetime.timedelta(minutes=1)
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
    return create_access_token(
        identity = getIdentity(rawJwt=rawJwt),
        user_claims = userClaims,
        fresh = False,
        expires_delta = deltaMinutes,
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentSession(sessionClass=None):
    currentUsert = get_current_user()
    if ObjectHelper.isNotNone(currentUsert):
        return currentUsert
    else:
        rawJwt = getJwtBody()
        identity = getIdentity(rawJwt=rawJwt)
        context = getContext(rawJwt=rawJwt)
        if ObjectHelper.isNone(sessionClass):
            return {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context,
                JwtConstant.KW_DATA: getData(rawJwt=rawJwt)
            }
        else:
            currentUsert = sessionClass()
            currentUsert._authorizationInfo = {
                JwtConstant.KW_IDENTITY: identity,
                JwtConstant.KW_CONTEXT: context
            }
            data = getData(rawJwt=rawJwt)
            for attributeName in data:
                if ReflectionHelper.hasAttributeOrMethod(currentUsert, attributeName):
                    ReflectionHelper.setAttributeOrMethod(currentUsert, attributeName, data.get(attributeName))
            return currentUsert

# @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
# def createAccessToken(session, deltaMinutes=None, headers=None) :
#     ###- datetime.datetime.utcnow()
#     if ObjectHelper.isNotNone(deltaMinutes) :
#         deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
#     return create_access_token(
#         identity = session.id,
#         fresh = False,
#         expires_delta = deltaMinutes,
#         user_claims = session.role,
#         headers = headers
#     )
#
# @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
# def refreshAccessToken(session, deltaMinutes=None, headers=None) :
#     ###- datetime.datetime.utcnow()
#     if ObjectHelper.isNotNone(deltaMinutes) :
#         deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
#     return create_refresh_token(
#         identity = session.id,
#         fresh = False,
#         expires_delta = deltaMinutes,
#         user_claims = session.role,
#         headers = headers
#     )
