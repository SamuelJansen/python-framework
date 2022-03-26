from python_helper import Constant as c
from python_helper import ObjectHelper, log, Function, StringHelper

from python_framework.api.src.constant import HttpClientConstant
from python_framework.api.src.domain import HttpDomain
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import ConverterStatic
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service import ExceptionHandler
from python_framework.api.src.service.ExceptionHandler import GlobalException


class HttpClientEvent(Exception):
    def __init__(self, verb, *args, eventContext=HttpDomain.CLIENT_CONTEXT, **kwargs):
        if ObjectHelper.isNone(verb):
            raise Exception(f'Http {eventContext.lower()} event verb cannot be none')
        Exception.__init__(self, f'Http {eventContext.lower()} {verb} event')
        self.verb = verb
        self.args = args
        self.kwargs = kwargs


class ManualHttpClientEvent(Exception):
    def __init__(self, completeResponse, eventContext=HttpDomain.CLIENT_CONTEXT):
        Exception.__init__(self, f'ManualHttpClientEvent')
        self.completeResponse = completeResponse


def getHttpClientEvent(resourceInstanceMethod, *args, eventContext=HttpDomain.CLIENT_CONTEXT, **kwargs):
    completeResponse = None
    try:
        completeResponse = resourceInstanceMethod(*args, eventContext=eventContext, **kwargs)
    except HttpClientEvent as httpClientEvent:
        return httpClientEvent
    except Exception as exception:
        raise exception
    if ObjectHelper.isNotNone(completeResponse):
        return ManualHttpClientEvent(completeResponse, eventContext=eventContext)


def raiseHttpClientEventNotFoundException(*args, **kwargs):
    raise Exception('HttpClientEvent not found')


@Function
def getUrl(client, clientMethodConfig, additionalUrl):
    return StringHelper.join(
        [
            ConverterStatic.getValueOrDefault(u, c.BLANK) for u in [
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
        **ConverterStatic.getValueOrDefault(client.headers, dict()),
        **{HttpDomain.HeaderKey.CONTENT_TYPE: clientMethodConfig.consumes},
        **ConverterStatic.getValueOrDefault(clientMethodConfig.headers, dict()),
        **ConverterStatic.getValueOrDefault(headers, dict())
    }


@Function
def getTimeout(client, clientMethodConfig, timeout):
    return ConverterStatic.getValueOrDefault(timeout, ConverterStatic.getValueOrDefault(clientMethodConfig.timeout, client.timeout))


@Function
def getLogRequest(client, clientMethodConfig, logRequest):
    return client.logRequest or clientMethodConfig.logRequest or logRequest


@Function
def parseParameters(client, clientMethodConfig, additionalUrl, params, headers, body, timeout, logRequest):
    url = getUrl(client, clientMethodConfig, additionalUrl)
    params = ConverterStatic.getValueOrDefault(params, dict())
    headers = getHeaders(client, clientMethodConfig, headers)
    body = ConverterStatic.getValueOrDefault(body, dict())
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
    if ObjectHelper.isNone(status) or 500 <= status:
        raise ExceptionHandler.getClientGlobalException(
            clientResponse,
            context,
            getErrorMessage(clientResponse, context=context, businessLogMessage=businessLogMessage, defaultLogMessage=defaultLogMessage),
            exception = None,
            status = status
        )
    elif 400 <= status:
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
    responseStatus = ConverterStatic.getValueOrDefault(responseStatus, HttpStatus.map(fallbackStatus))
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
