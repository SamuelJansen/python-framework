import requests
from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function, StringHelper

from python_framework.api.src.constant import HttpClientConstant
from python_framework.api.src.domain import HttpDomain
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service import ExceptionHandler
from python_framework.api.src.service.ExceptionHandler import GlobalException


class HttpClientEvent:
    def __init__(self, verb, *args, eventContext=HttpDomain.CLIENT_CONTEXT, **kwargs):
        if ObjectHelper.isNone(verb):
            raise Exception(f'Http {eventContext.lower()} event verb cannot be none')
        self.verb = verb
        self.args = args
        self.kwargs = kwargs


class ManualHttpClientEvent:
    def __init__(self, completeResponse, *args, eventContext=HttpDomain.CLIENT_CONTEXT, **kwargs):
        self.completeResponse = completeResponse


def getHttpClientEvent(resourceInstanceMethod, *args, **kwargs):
    try:
        evenOrCompleteResponse = resourceInstanceMethod(*args, **kwargs)
        if isinstance(evenOrCompleteResponse, HttpClientEvent):
            return evenOrCompleteResponse
        else:
            return ManualHttpClientEvent(evenOrCompleteResponse, *args, **kwargs)
    except Exception as exception:
        log.log(getHttpClientEvent, 'Not possible o get client event', exception=exception)
        raise exception


def raiseHttpClientEventNotFoundException(*args, **kwargs):
    raise Exception('HttpClientEvent not found')


@Function
def getUrl(client, clientMethodConfig, additionalUrl):
    return StringHelper.join(
        [
            StaticConverter.getValueOrDefault(u, c.BLANK) for u in [
                client.url,
                clientMethodConfig.url,
                additionalUrl
            ]
        ],
        character = c.BLANK
    )


@Function
def getHeaders(client, clientMethodConfig, headers):
    return {
        **StaticConverter.getValueOrDefault(client.headers, dict()),
        **{HttpDomain.HeaderKey.CONTENT_TYPE: clientMethodConfig.consumes},
        **StaticConverter.getValueOrDefault(clientMethodConfig.headers, dict()),
        **StaticConverter.getValueOrDefault(headers, dict())
    }


@Function
def getTimeout(client, clientMethodConfig, timeout):
    return StaticConverter.getValueOrDefault(timeout, StaticConverter.getValueOrDefault(clientMethodConfig.timeout, client.timeout))


@Function
def getLogRequest(client, clientMethodConfig, logRequest):
    return client.logRequest and clientMethodConfig.logRequest and logRequest


@Function
def parseParameters(client, clientMethodConfig, additionalUrl, params, headers, body, timeout, logRequest):
    url = getUrl(client, clientMethodConfig, additionalUrl)
    params = StaticConverter.getValueOrDefault(params, dict())
    headers = getHeaders(client, clientMethodConfig, headers)
    body = StaticConverter.getValueOrDefault(body, dict())
    timeout = getTimeout(client, clientMethodConfig, timeout)
    logRequest = getLogRequest(client, clientMethodConfig, logRequest)
    return url, params, headers, body, timeout, logRequest


def raiseException(
    clientResponse,
    exception,
    context = HttpDomain.CLIENT_CONTEXT,
    businessLogMessage = HttpClientConstant.ERROR_AT_CLIENT_CALL_MESSAGE,
    defaultLogMessage = HttpClientConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE
):
    if isinstance(exception, requests.exceptions.ReadTimeout):
        raise ExceptionHandler.getClientGlobalException(
            clientResponse,
            context,
            str(exception),
            exception = exception,
            status = HttpStatus.REQUEST_TIMEOUT
        )
    elif isinstance(exception, requests.exceptions.ConnectionError):
        raise ExceptionHandler.getClientGlobalException(
            clientResponse,
            context,
            str(exception),
            exception = exception,
            status = HttpStatus.SERVICE_UNAVAILABLE
        )
    raise ExceptionHandler.getClientGlobalException(
        clientResponse,
        context,
        getErrorMessage(clientResponse, exception=exception, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage),
        exception = exception
    )


def raiseExceptionIfNeeded(
    clientResponse,
    context = HttpDomain.CLIENT_CONTEXT,
    businessLogMessage = HttpClientConstant.ERROR_AT_CLIENT_CALL_MESSAGE,
    defaultLogMessage = HttpClientConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE
):
    status = FlaskUtil.safellyGetResponseStatus(clientResponse) ###- clientResponse.status_code
    if ObjectHelper.isNone(status) or HttpStatus.INTERNAL_SERVER_ERROR <= status:
        raise ExceptionHandler.getClientGlobalException(
            clientResponse,
            context,
            getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage),
            exception = None,
            status = status
        )
    elif HttpStatus.BAD_REQUEST <= status:
        if HttpStatus.UNAUTHORIZED == status or HttpStatus.FORBIDDEN == status:
            raise ExceptionHandler.getClientGlobalException(
                clientResponse,
                context,
                businessLogMessage,
                exception = None,
                status = HttpStatus.PROXY_ATHENTICATION_REQUIRED,
                message = getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage)
            )
        elif HttpStatus.REQUEST_TIMEOUT == status:
            raise ExceptionHandler.getClientGlobalException(
                clientResponse,
                context,
                getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage),
                exception = None,
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )
        elif HttpStatus.NOT_FOUND == status:
            raise ExceptionHandler.getClientGlobalException(
                clientResponse,
                context,
                getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage),
                exception = None,
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )
        raise ExceptionHandler.getClientGlobalException(
            clientResponse,
            context,
            businessLogMessage,
            exception = None,
            status = status,
            message = getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage)
        )


@Function
def getCompleteResponse(clientResponse, responseClass, produces, fallbackStatus=HttpStatus.INTERNAL_SERVER_ERROR):
    responseBody, responseHeaders, responseStatus = dict(), dict(), fallbackStatus
    responseHeaders = FlaskUtil.safellyGetResponseHeaders(clientResponse)
    responseBody = FlaskUtil.safellyGetResponseJson(clientResponse)
    try :
        responseStatus = HttpStatus.map(HttpStatus.NOT_FOUND if ObjectHelper.isNone(clientResponse.status_code) else clientResponse.status_code)
    except Exception as exception :
        responseStatus = HttpStatus.map(fallbackStatus)
        log.warning(getCompleteResponse, f'Not possible to get client response status. Returning {responseStatus} by default', exception=exception)
    responseHeaders = {
        **{HttpDomain.HeaderKey.CONTENT_TYPE: produces},
        **responseHeaders
    }
    responseStatus = StaticConverter.getValueOrDefault(responseStatus, HttpStatus.map(fallbackStatus))
    if ObjectHelper.isNotNone(responseClass):
        responseBody = Serializer.convertFromJsonToObject(responseBody, responseClass)
    return responseBody, responseHeaders, responseStatus


@Function
def getErrorMessage(
    clientResponse,
    exception = None,
    context = HttpDomain.CLIENT_CONTEXT,
    businessLogMessage = HttpClientConstant.ERROR_AT_CLIENT_CALL_MESSAGE,
    defaultLogMessage = HttpClientConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE
):
    bodyAsJson = getClientResponseBodyAsJson(clientResponse, context=context)
    completeErrorMessage = f'{businessLogMessage}{c.DOT_SPACE}{defaultLogMessage}'
    errorMessage = defaultLogMessage
    possibleErrorMessage = None
    try:
        if ObjectHelper.isNotNone(clientResponse):
            if ObjectHelper.isDictionary(bodyAsJson):
                possibleErrorMessage = getErrorMessageFromClientResponseBodyAsJson(bodyAsJson, defaultLogMessage)
            if ObjectHelper.isList(bodyAsJson) and 0 < len(bodyAsJson):
                possibleErrorMessage = getErrorMessageFromClientResponseBodyAsJson(bodyAsJson[0], defaultLogMessage)
        if ObjectHelper.isNotNone(possibleErrorMessage) and StringHelper.isNotBlank(possibleErrorMessage):
            errorMessage = f'{c.LOG_CAUSE}{possibleErrorMessage}'
        else:
            log.debug(getErrorMessage, f'{context} response {FlaskUtil.safellyGetResponseJson(clientResponse)}')
        exceptionPortion = businessLogMessage if ObjectHelper.isNone(exception) or StringHelper.isBlank(exception) else str(exception)
        completeErrorMessage = f'{exceptionPortion}{c.DOT_SPACE}{errorMessage}'
    except Exception as innerException:
        log.warning(getErrorMessage, f'Not possible to get error message. Returning "{completeErrorMessage}" by default', exception=innerException)
    return completeErrorMessage


def getClientResponseBodyAsJson(clientResponse, context=HttpDomain.CLIENT_CONTEXT):
    bodyAsJson = {}
    try :
        bodyAsJson = clientResponse.json()
    except Exception as exception :
        bodyAsJsonException = FlaskUtil.safellyGetResponseJson(clientResponse)
        log.log(getClientResponseBodyAsJson, f'Invalid {context.lower()} response: {bodyAsJsonException}', exception=exception)
        log.debug(getClientResponseBodyAsJson, f'Not possible to get error message from {context.lower()} response: {bodyAsJsonException}. Proceeding with value {bodyAsJson} by default', exception=exception, muteStackTrace=True)
    return bodyAsJson


def getErrorMessageFromClientResponseBodyAsJson(bodyAsJson, defaultLogMessage):
    return bodyAsJson.get('message', bodyAsJson.get('error', defaultLogMessage)).strip()
