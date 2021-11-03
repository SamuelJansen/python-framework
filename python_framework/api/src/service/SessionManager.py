import time
import jwt

from python_helper import Constant as c
from python_helper import log, Function, ObjectHelper, ReflectionHelper, DateTimeHelper
import datetime

from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.annotation.GlobalExceptionAnnotation import EncapsulateItWithGlobalException


BLACK_LIST = set()


class JwtManager:

    def __init__(self, jwtSecret, algorithm, headerName, headerType):
        self.secret = jwtSecret
        self.algorithm = algorithm
        self.headerName = headerName
        self.headerType = headerType

    @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def encode(self, payload, headers=None) :
        return jwt.encode(payload, self.secret, algorithm=self.algorithm, headers=headers if ObjectHelper.isNotNone else dict())

    @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def decode(self, encoded_payload, options=None) :
        if ObjectHelper.isNone(encoded_payload):
            self.raiseInvalidAccess('JWT session token cannot be None')
        if not encoded_payload.startswith(f'{self.headerType} '):
            self.raiseInvalidAccess(f'JWT session token must starts with {self.headerType}')
        return jwt.decode(encoded_payload, self.secret, algorithms=self.algorithm, options=options if ObjectHelper.isNotNone(options) else dict())

    @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def verifyAuthorizaionAccess(self, decriptedToken) :
        return decriptedToken[JwtConstant.KW_JTI] in BLACK_LIST

    @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def raiseInvalidAccess(self, logMessage) :
        raise Exception(logMessage)

    @EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
    def validateSession(self):
        decodedSessionToken = self.getDecodedToken()

    def getBody(self, rawJwt=None):
        decodedSessionToken = self.getDecodedToken(rawJwt=rawJwt)
        print(decodedSessionToken)
        return decodedSessionToken

    def getUnverifiedBody(self, rawJwt=None):
        return self.getDecodedToken(rawJwt=rawJwt, options={"verify_signature": False})

    def getUnverifiedHeaders(self):
        return jwt.get_unverified_header(captureEncodedToken(self))

    def getDecodedToken(self, rawJwt=None, options=None):
        if ObjectHelper.isNotNone(rawJwt):
            return rawJwt
        return self.decode(self.captureEncodedToken(), options=options)

    def captureEncodedToken(self):
        return FlaskUtil.safellyGetHeaders().get(self.headerName)


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtBody(rawJwt=None, apiInstance=None) :
    if ObjectHelper.isNone(rawJwt):
        return retrieveApiInstance(apiInstance=apiInstance).session.getBody(rawJwt=rawJwt)
    return rawJwt

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJwtHeaders(apiInstance=None):
    headers = retrieveApiInstance(apiInstance=apiInstance).session.getUnverifiedHeaders()
    return headers if ObjectHelper.isNotNone(headers) else dict()

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getContext(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return list() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_CONTEXT)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getData(rawJwt=None, apiInstance=None):
    rawJwt = getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance)
    return dict() if ObjectHelper.isNone(rawJwt) else rawJwt.get(JwtConstant.KW_CLAIMS, {}).get(JwtConstant.KW_DATA)

@Function
def jwtRequired(function, *args, **kwargs) :
    def innerFunction(*args, **kwargs) :
        retrieveApiInstance(arguments=args).session.validateSession()
        functionReturn = function(*args, **kwargs)
        return functionReturn
    ReflectionHelper.overrideSignatures(innerFunction, function)
    return innerFunction


@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getJti(rawJwt=None, apiInstance=None) :
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_JTI)

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getIdentity(rawJwt=None, apiInstance=None) :
    return getJwtBody(rawJwt=rawJwt, apiInstance=apiInstance).get(JwtConstant.KW_IDENTITY)

@Function
def addUserToBlackList() :
    BLACK_LIST.add(getJti())

@Function
def getJwtMannager(
    appInstance,
    jwtSecret,
    algorithm = JwtConstant.DEFAULT_JWT_SESSION_ALGORITHM,
    headerName = JwtConstant.DEFAULT_JWT_SESSION_HEADER_NAME,
    headerType = JwtConstant.DEFAULT_JWT_SESSION_HEADER_TYPE
) :
    if not jwtSecret :
        log.warning(getJwtMannager, f'Not possible to instanciate jwtManager{c.DOT_SPACE_CAUSE}Missing jwt secret')
    else :
        jwtMannager = JwtManager(jwtSecret, algorithm, headerName, headerType)
        return jwtMannager

@Function
def addJwt(jwtInstance) :
    ...

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def createAccessToken(identity, contextList, deltaMinutes=None, headers=None, data=None, apiInstance=None):
    if deltaMinutes :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    timeNow = DateTimeHelper.dateTimeNow()
    return retrieveApiInstance(apiInstance=apiInstance).session.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: f"{int(f'{time.time()}'.replace('.', ''))+int(f'{time.time()}'.replace('.', ''))}",
            JwtConstant.KW_EXPIRATION: timeNow + deltaMinutes,
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.ACCESS_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList,
                JwtConstant.KW_DATA: data
            }
        },
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def refreshAccessToken(identity, contextList, deltaMinutes=None, headers=None, data=None, apiInstance=None):
    if ObjectHelper.isNotNone(deltaMinutes) :
        deltaMinutes = datetime.timedelta(minutes=deltaMinutes)
    timeNow = DateTimeHelper.dateTimeNow()
    return retrieveApiInstance(apiInstance=apiInstance).session.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: f"{int(f'{time.time()}'.replace('.', ''))+int(f'{time.time()}'.replace('.', ''))}",
            JwtConstant.KW_EXPIRATION: timeNow + deltaMinutes,
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.REFRESH_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: {
                JwtConstant.KW_CONTEXT: contextList,
                JwtConstant.KW_DATA: data
            }
        },
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def patchAccessToken(newContextList=None, headers=None, data=None, apiInstance=None):
    rawJwt = getJwtBody()
    # expiresDelta=rawJwt.get(JwtConstant.KW_EXPIRATION)
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
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    return apiInstance.session.encode({
            JwtConstant.KW_IAT: timeNow,
            JwtConstant.KW_NFB: timeNow,
            JwtConstant.KW_JTI: f"{int(f'{time.time()}'.replace('.', ''))+int(f'{time.time()}'.replace('.', ''))}",
            JwtConstant.KW_EXPIRATION: timeNow + deltaMinutes,
            JwtConstant.KW_IDENTITY: getIdentity(rawJwt=rawJwt, apiInstance=apiInstance),
            JwtConstant.KW_FRESH: False,
            JwtConstant.KW_TYPE: JwtConstant.REFRESH_VALUE_TYPE,
            JwtConstant.KW_CLAIMS: userClaims
        },
        headers = headers
    )

@EncapsulateItWithGlobalException(message=JwtConstant.UNAUTHORIZED_MESSAGE, status=HttpStatus.UNAUTHORIZED)
def getCurrentSession(sessionClass=None, apiInstance=None):
    apiInstance = retrieveApiInstance(apiInstance=apiInstance)
    rawJwt = getJwtBody(apiInstance=apiInstance)
    identity = getIdentity(rawJwt=rawJwt, apiInstance=apiInstance)
    context = getContext(rawJwt=rawJwt, apiInstance=apiInstance)
    if ObjectHelper.isNone(sessionClass):
        return {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context,
            JwtConstant.KW_DATA: getData(rawJwt=rawJwt, apiInstance=apiInstance)
        }
    else:
        currentUsert = sessionClass()
        currentUsert._authorizationInfo = {
            JwtConstant.KW_IDENTITY: identity,
            JwtConstant.KW_CONTEXT: context
        }
        data = getData(rawJwt=rawJwt, apiInstance=apiInstance)
        for attributeName in data:
            if ReflectionHelper.hasAttributeOrMethod(currentUsert, attributeName):
                ReflectionHelper.setAttributeOrMethod(currentUsert, attributeName, data.get(attributeName))
        return currentUsert

def retrieveApiInstance(apiInstance=None, arguments=None):
    if ObjectHelper.isNone(apiInstance) and ObjectHelper.isNotNone(arguments):
        apiInstance = None
        try:
            apiInstance = arguments[0]
        except Exception as exception:
            log.warning(jwtRequired, f'''Not possible to retrieve api instance by arguments. Going for another approach''')
    if ObjectHelper.isNone(apiInstance) or not FlaskUtil.isApiInstance(apiInstance):
        log.warning(jwtRequired, f'''Not possible to retrieve api instance. Going for a slower approach''')
        apiInstance = FlaskUtil.getApi()
    return apiInstance if ObjectHelper.isNotNone(apiInstance) else raiseUnretrievedApiInstance()

def raiseUnretrievedApiInstance():
    raise Exception('Not possible to retrieve api instance')
