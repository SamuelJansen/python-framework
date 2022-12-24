from python_helper import log, ObjectHelper

from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.constant import AuditoryConstant
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager


def overrideSessionData(model):
    StaticConverter.overrideData(
        model,
        StaticConverter.getValueOrDefault(
            getSessionIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentSession(apiInstance=None, service=None, sessionClass=None):
    currentSession = None
    try:
        currentSession = SessionManager.getCurrentSession(sessionClass=sessionClass, apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentSession, f'Not possible to get current session. Returning "{currentSession}" by default', exception=exception, muteStackTrace=True)
    return StaticConverter.getValueOrDefault(currentSession, {} if ObjectHelper.isNone(sessionClass) else sessionClass())


def getSessionIdentity(apiInstance=None, service=None):
    return safellyGetCurrentSession(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)


def overrideApiKeyData(model):
    StaticConverter.overrideData(
        model,
        StaticConverter.getValueOrDefault(
            getApiKeyIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentApiKey(apiInstance=None, service=None, apiKeyClass=None):
    currentApiKey = None
    try:
        currentApiKey = ApiKeyManager.getCurrentApiKey(apiKeyClass=apiKeyClass, apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentApiKey, f'Not possible to get current api key. Returning "{currentApiKey}" by default', exception=exception, muteStackTrace=True)
    return StaticConverter.getValueOrDefault(currentApiKey, {} if ObjectHelper.isNone(apiKeyClass) else apiKeyClass())


def getApiKeyIdentity(apiInstance=None, service=None):
    return safellyGetCurrentApiKey(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)


def overrideAthenticationData(model):
    StaticConverter.overrideData(
        model,
        StaticConverter.getValueOrDefault(
            getAthenticationIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentAthentication(apiInstance=None, service=None, securityClass=None):
    currentAthentication = None
    try:
        currentAthentication = SecurityManager.getCurrentUser(securityClass=securityClass, apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentAthentication, f'Not possible to get current user. Returning "{currentAthentication}" by default', exception=exception, muteStackTrace=True)
    return StaticConverter.getValueOrDefault(currentAthentication, {} if ObjectHelper.isNone(securityClass) else securityClass())


def getAthenticationIdentity(apiInstance=None, service=None):
    return safellyGetCurrentAthentication(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)
