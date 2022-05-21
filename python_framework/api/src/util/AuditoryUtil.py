from python_helper import log, ObjectHelper

from python_framework.api.src.constant import JwtConstant
from python_framework.api.src.constant import AuditoryConstant
from python_framework.api.src.converter.static import ConverterStatic
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager


def overrideSessionData(model):
    ConverterStatic.overrideData(
        model,
        ConverterStatic.getValueOrDefault(
            getSessionIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentSession(apiInstance=None, service=None):
    currentSession = None
    try:
        currentSession = SessionManager.getCurrentSession(apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentSession, f'Not possible to get current session. Returning "{currentSession}" by default', exception=exception, muteStackTrace=True)
    return ConverterStatic.getValueOrDefault(currentSession, {})


def getSessionIdentity(apiInstance=None, service=None):
    return safellyGetCurrentSession(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)


def overrideApiKeyData(model):
    ConverterStatic.overrideData(
        model,
        ConverterStatic.getValueOrDefault(
            getApiKeyIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentApiKey(apiInstance=None, service=None):
    currentApiKey = None
    try:
        currentApiKey = ApiKeyManager.getCurrentApiKey(apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentApiKey, f'Not possible to get current api key. Returning "{currentApiKey}" by default', exception=exception, muteStackTrace=True)
    return ConverterStatic.getValueOrDefault(currentApiKey, {})


def getApiKeyIdentity(apiInstance=None, service=None):
    return safellyGetCurrentApiKey(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)


def overrideAthenticationData(model):
    ConverterStatic.overrideData(
        model,
        ConverterStatic.getValueOrDefault(
            getAthenticationIdentity(apiInstance=None),
            AuditoryConstant.DEFAULT_USER
        )
    )


def safellyGetCurrentAthentication(apiInstance=None, service=None):
    currentAthentication = None
    try:
        currentAthentication = SecurityManager.getCurrentUser(apiInstance=apiInstance if ObjectHelper.isNone(service) else service.globals.api)
    except Exception as exception:
        log.debug(safellyGetCurrentAthentication, f'Not possible to get current user. Returning "{currentAthentication}" by default', exception=exception, muteStackTrace=True)
    return ConverterStatic.getValueOrDefault(currentAthentication, {})


def getAthenticationIdentity(apiInstance=None, service=None):
    return safellyGetCurrentAthentication(apiInstance=apiInstance, service=service).get(JwtConstant.KW_IDENTITY)
