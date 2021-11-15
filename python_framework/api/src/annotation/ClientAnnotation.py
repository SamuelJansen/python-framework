import requests
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper

from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import ConverterStatic
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.service.ExceptionHandler import GlobalException


CLIENT_DID_NOT_SENT_ANY_MESSAGE = 'Client did not sent any message'
ERROR_AT_CLIENT_CALL_MESSAGE = 'Error at client call'
DEFAULT_TIMEOUT = 30


class HeaderKey:
    CONTENT_TYPE = 'Content-Type'


class Verb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


@Function
def Client(url=c.SLASH, headers=None, timeout=DEFAULT_TIMEOUT, logRequest=False, logResponse=False) :
    clientUrl = url
    clientHeaders = ConverterStatic.getValueOrDefault(headers, dict())
    clientTimeout = timeout
    clientLogRequest = logRequest
    clientLogResponse = logResponse
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Client,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            url = clientUrl
            headers = clientHeaders
            timeout = clientTimeout
            logRequest = clientLogRequest
            logResponse = clientLogResponse
            def __init__(self,*args, **kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args, **kwargs)
                self.globals = apiInstance.globals

            def options(self,
                resourceInstanceMethod,
                aditionalUrl = None,
                params = None,
                headers = None,
                timeout = None,
                logRequest = False,
                **kwargs
            ):
                verb = Verb.OPTIONS
                body = dict()
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.options(
                    url,
                    params = params,
                    headers = headers,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def get(self,
                resourceInstanceMethod,
                aditionalUrl = None,
                params = None,
                headers = None,
                timeout = None,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.GET
                body = dict()
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.get(
                    url,
                    params = params,
                    headers = headers,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def post(self,
                resourceInstanceMethod,
                body,
                aditionalUrl = None,
                headers = None,
                params = None,
                timeout = None,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.POST
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.post(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def put(self,
                resourceInstanceMethod,
                body,
                aditionalUrl = None,
                headers = None,
                params = None,
                timeout = None,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.PUT
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.put(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def delete(self,
                resourceInstanceMethod,
                body,
                aditionalUrl = None,
                headers = None,
                params = None,
                timeout = None,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.DELETE
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.delete(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def patch(self,
                resourceInstanceMethod,
                body,
                aditionalUrl = None,
                headers = None,
                params = None,
                timeout = None,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.PATCH
                url, params, headers, timeout, logRequest = parseParameters(
                    self,
                    resourceInstanceMethod,
                    aditionalUrl,
                    params,
                    headers,
                    timeout,
                    logRequest
                )
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest)
                clientResponse = requests.patch(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return clientResponse

            def logRequest(self, resourceInstanceMethod, verb, url, body, params, headers, logRequest):
                log.info(resourceInstanceMethod, f'Client {verb} - {url}')
                if logRequest:
                    log.prettyJson(
                        resourceInstanceMethod,
                        'Request',
                        {
                            'headers': ConverterStatic.getValueOrDefault(headers, dict()),
                            'query': ConverterStatic.getValueOrDefault(params, dict()),
                            'body': ConverterStatic.getValueOrDefault(body, dict())
                        },
                        condition = True,
                        logLevel = log.INFO
                    )

        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ClientMethod(
    url = c.SLASH,
    headers = None,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    returnOnlyBody = True,
    timeout = None,
    propagateAuthorization = False,
    propagateApiKey = False,
    propagateSession = False,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = False,
    logResponse = False
):
    clientMethodUrl = url
    clientMethodHeaders = headers
    clientMethodRequestHeaderClass = requestHeaderClass
    clientMethodRequestParamClass = requestParamClass
    clientMethodRequestClass = requestClass
    clientMethodResponseClass = responseClass
    clientMethodReturnOnlyBody = returnOnlyBody
    clientMethodTimeout = timeout
    clientMethodPropagateAuthorization = propagateAuthorization
    clientMethodPropagateApiKey = propagateApiKey
    clientMethodPropagateSession = propagateSession
    clientMethodProduces = produces
    clientMethodConsumes = consumes
    clientMethodLogRequest = logRequest
    clientMethodLogResponse = logResponse
    def innerMethodWrapper(resourceInstanceMethod,*args, **kwargs) :
        log.wrapper(ClientMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
        def innerResourceInstanceMethod(*args, **kwargs):
            f'''(*args, {FlaskUtil.KW_HEADERS}={{}}, {FlaskUtil.KW_PARAMETERS}={{}}, **kwargs)'''
            resourceInstance = args[0]
            clientResponse = None
            completeResponse = None
            try :
                FlaskManager.validateKwargs(
                    kwargs,
                    resourceInstance,
                    resourceInstanceMethod,
                    requestHeaderClass,
                    requestParamClass
                )
                FlaskManager.validateArgs(args, requestClass, resourceInstanceMethod)
                clientResponse = None
                try :
                    clientResponse = resourceInstanceMethod(*args, **kwargs)
                except Exception as exception:
                    raiseException(clientResponse, exception)
                raiseExceptionIfNeeded(clientResponse)
                completeResponse = getCompleteResponse(clientResponse, responseClass, produces)
                FlaskManager.validateResponseClass(responseClass, completeResponse)
            except Exception as exception :
                log.log(innerResourceInstanceMethod, 'Failure at client method execution', exception=exception, muteStackTrace=True)
                raise exception
            clientResponseStatus = completeResponse[-1]
            clientResponseHeaders = completeResponse[1]
            clientResponseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : HttpStatus.map(clientResponseStatus).enumName}
            if resourceInstance.logResponse or logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    'Response',
                    {
                        'headers': clientResponseHeaders,
                        'body': Serializer.getObjectAsDictionary(clientResponseBody),
                        'status': clientResponseStatus
                    },
                    condition = True,
                    logLevel = log.INFO
                )
            if returnOnlyBody:
                return completeResponse[0]
            else:
                return completeResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = clientMethodUrl
        innerResourceInstanceMethod.headers = clientMethodHeaders
        innerResourceInstanceMethod.requestHeaderClass = clientMethodRequestHeaderClass
        innerResourceInstanceMethod.requestParamClass = clientMethodRequestParamClass
        innerResourceInstanceMethod.requestClass = clientMethodRequestClass
        innerResourceInstanceMethod.responseClass = clientMethodResponseClass
        innerResourceInstanceMethod.returnOnlyBody = clientMethodReturnOnlyBody
        innerResourceInstanceMethod.timeout = clientMethodTimeout
        innerResourceInstanceMethod.propagateAuthorization = clientMethodPropagateAuthorization
        innerResourceInstanceMethod.propagateApiKey = clientMethodPropagateApiKey
        innerResourceInstanceMethod.propagateSession = clientMethodPropagateSession
        innerResourceInstanceMethod.produces = clientMethodProduces
        innerResourceInstanceMethod.consumes = clientMethodConsumes
        innerResourceInstanceMethod.logRequest = clientMethodLogRequest
        innerResourceInstanceMethod.logResponse = clientMethodLogResponse
        return innerResourceInstanceMethod
    return innerMethodWrapper


@Function
def getUrl(client, resourceInstanceMethod, aditionalUrl):
    return StringHelper.join(
        [
            ConverterStatic.getValueOrDefault(u, c.BLANK) for u in [
                client.url,
                resourceInstanceMethod.url,
                aditionalUrl
            ]
        ],
        character = c.BLANK
    )


@Function
def getHeaders(client, resourceInstanceMethod, headers):
    return {
        **ConverterStatic.getValueOrDefault(client.headers, dict()),
        **{HeaderKey.CONTENT_TYPE: resourceInstanceMethod.consumes},
        **ConverterStatic.getValueOrDefault(resourceInstanceMethod.headers, dict()),
        **ConverterStatic.getValueOrDefault(headers, dict())
    }


@Function
def getTimeout(client, resourceInstanceMethod, timeout):
    return ConverterStatic.getValueOrDefault(timeout, ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, client.timeout))


@Function
def getLogRequest(client, resourceInstanceMethod, logRequest):
    return client.logRequest or resourceInstanceMethod.logRequest or logRequest


@Function
def parseParameters(client, resourceInstanceMethod, aditionalUrl, params, headers, timeout, logRequest):
    url = getUrl(client, resourceInstanceMethod, aditionalUrl)
    params = ConverterStatic.getValueOrDefault(params, dict())
    headers = getHeaders(client, resourceInstanceMethod, headers)
    timeout = getTimeout(client, resourceInstanceMethod, timeout)
    logRequest = getLogRequest(client, resourceInstanceMethod, logRequest)
    return url, params, headers, timeout, logRequest


@Function
def raiseException(clientResponse, exception):
        raise GlobalException(
            logMessage = getErrorMessage(clientResponse, exception=exception)
        )


@Function
def raiseExceptionIfNeeded(clientResponse):
    if ObjectHelper.isDictionary(clientResponse):
        raise Exception('Invalid client response')
    if ObjectHelper.isTuple(clientResponse):
        if ObjectHelper.isNotNone(clientResponse[-1]) and 400 <= clientResponse[-1]:
            raise GlobalException(
                message = getErrorMessage(clientResponse),
                status = HttpStatus.map(clientResponse.status_code),
                logMessage = ERROR_AT_CLIENT_CALL_MESSAGE
            )
        elif ObjectHelper.isNone(clientResponse[-1]) or 500 <= clientResponse[-1]:
            raise GlobalException(logMessage = getErrorMessage(clientResponse))
    else:
        if 400 <= clientResponse.status_code:
            raise GlobalException(
                message = getErrorMessage(clientResponse),
                status = HttpStatus.map(clientResponse.status_code),
                logMessage = ERROR_AT_CLIENT_CALL_MESSAGE
            )
        elif ObjectHelper.isNone(clientResponse.status_code) or 500 <= clientResponse.status_code:
            raise GlobalException(logMessage = getErrorMessage(clientResponse))


@Function
def getCompleteResponse(clientResponse, responseClass, produces, fallbackStatus=HttpStatus.INTERNAL_SERVER_ERROR):
    if ObjectHelper.isDictionary(clientResponse):
        raise Exception('Invalid client response')
    responseBody, responseHeaders, responseStatus = None, None, None
    if ObjectHelper.isTuple(clientResponse):
        if 2 == len(clientResponse):
            responseBody, responseHeaders, responseStatus = clientResponse[0], dict(), clientResponse[-1]
        if 3 == len(clientResponse):
            responseBody, responseHeaders, responseStatus = clientResponse[0], clientResponse[1], clientResponse[-1]
    else:
        try :
            responseBody, responseHeaders, responseStatus = clientResponse.json(), FlaskUtil.safellyGetResponseHeaders(clientResponse), HttpStatus.map(HttpStatus.NOT_FOUND if ObjectHelper.isNone(clientResponse.status_code) else clientResponse.status_code)
        except Exception as exception :
            responseBody, responseStatus = dict(), HttpStatus.map(fallbackStatus)
            log.failure(getCompleteResponse, 'Not possible to parse client response as json', exception=exception, muteStackTrace=True)
        responseHeaders = {
            **{HeaderKey.CONTENT_TYPE: produces},
            **responseHeaders
        }
    if ObjectHelper.isNone(responseClass):
        return responseBody, responseHeaders, responseStatus
    else:
        return Serializer.convertFromJsonToObject(responseBody, responseClass), responseHeaders, responseStatus


@Function
def getErrorMessage(clientResponse, exception=None):
    if ObjectHelper.isDictionary(clientResponse):
        raise Exception('Invalid client response')
    errorMessage = CLIENT_DID_NOT_SENT_ANY_MESSAGE
    possibleErrorMessage = None
    bodyAsJson = {}
    try :
        if ObjectHelper.isTuple(clientResponse):
            bodyAsJson = Serializer.getObjectAsDictionary(clientResponse)
        else:
            bodyAsJson = clientResponse.json()
    except Exception as innerException :
        log.warning(getErrorMessage, f'Not possible to get error message from client response: {safellyGetBody(clientResponse, bodyAsJson)}', exception=innerException)
    if ObjectHelper.isNotNone(clientResponse):
        possibleErrorMessage = bodyAsJson.get('message', bodyAsJson.get('error')).strip()
    if ObjectHelper.isNotNone(possibleErrorMessage) and StringHelper.isNotBlank(possibleErrorMessage):
        errorMessage = f'{c.LOG_CAUSE}{possibleErrorMessage}'
    else:
        log.debug(getErrorMessage, f'Client response {safellyGetBody(clientResponse, bodyAsJson)}')
    exceptionPortion = ERROR_AT_CLIENT_CALL_MESSAGE if ObjectHelper.isNone(exception) or StringHelper.isBlank(exception) else str(exception)
    return f'{exceptionPortion}{c.DOT_SPACE}{errorMessage}'


def safellyGetBody(clientResponse, bodyAsJson):
    return bodyAsJson if ObjectHelper.isNotEmpty(bodyAsJson) else FlaskUtil.safellyGetResponseJson(clientResponse)
