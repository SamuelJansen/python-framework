import json
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function

from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import ConverterStatic
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.service.ExceptionHandler import GlobalException


CLIENT_DID_NOT_SENT_ANY_MESSAGE = 'Client did not sent any message'
ERROR_AT_CLIENT_CALL_MESSAGE = 'Error at client call'


class Verb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


@Function
def Client(url=c.SLASH, defaultHeaders=None, defautlTimeout=10, logRequest=False, logResponse=False) :
    clientUrl = url
    clientDefaultTimeout = defautlTimeout
    clientDefaultHeaders = ConverterStatic.getValueOrDefault(defaultHeaders, dict())
    clientLogRequest = logRequest
    clientLogResponse = logResponse
    def Wrapper(OuterClass, *args, **kwargs):
        log.wrapper(Client,f'''wrapping {OuterClass.__name__}''')
        class InnerClass(OuterClass):
            url = clientUrl
            defautlTimeout = clientDefaultTimeout
            defaultHeaders = clientDefaultHeaders
            logRequest = clientLogRequest
            logResponse = clientLogResponse
            def __init__(self,*args, **kwargs):
                log.wrapper(OuterClass,f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                apiInstance = FlaskManager.getApi()
                OuterClass.__init__(self,*args, **kwargs)
                self.globals = apiInstance.globals

            def options(self,
                resourceInstanceMethod,
                url,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.OPTIONS
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.options(
                    url,
                    params = params,
                    headers = headers,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def get(self,
                resourceInstanceMethod,
                url,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.GET
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.get(
                    url,
                    params = params,
                    headers = headers,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def post(self,
                resourceInstanceMethod,
                url,
                body,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.POST
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                body = ConverterStatic.getValueOrDefault(body, dict())
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.post(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def put(self,
                resourceInstanceMethod,
                url,
                body,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.PUT
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                body = ConverterStatic.getValueOrDefault(body, dict())
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.put(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def delete(self,
                resourceInstanceMethod,
                url,
                body,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.DELETE
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                body = ConverterStatic.getValueOrDefault(body, dict())
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.delete(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def patch(self,
                resourceInstanceMethod,
                url,
                body,
                headers = None,
                params = None,
                timeout = defautlTimeout,
                logRequest = logRequest,
                **kwargs
            ):
                verb = Verb.PATCH
                params = ConverterStatic.getValueOrDefault(params, dict())
                headers = {**self.defaultHeaders, **ConverterStatic.getValueOrDefault(headers, dict())}
                body = ConverterStatic.getValueOrDefault(body, dict())
                timeout = ConverterStatic.getValueOrDefault(resourceInstanceMethod.timeout, timeout)
                self.logRequest(resourceInstanceMethod, verb, url, body, params, headers, logRequest=logRequest or self.logRequest)
                response = requests.patch(
                    url,
                    params = params,
                    headers = headers,
                    json = body,
                    timeout = timeout,
                    **kwargs
                )
                return response

            def logRequest(self, resourceInstanceMethod, verb, url, body, params, headers, logRequest=False):
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
                        condition = logRequest,
                        logLevel = log.INFO
                    )
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def ClientMethod(
    url = c.SLASH,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    returnOnlyBody = True,
    timeout = 10,
    propagateAuthorization = False,
    propagateApiKey = False,
    propagateSession = False,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = False,
    logResponse = False
):
    clientMethodUrl = url
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
                response = None
                try :
                    response = resourceInstanceMethod(*args, **kwargs)
                except Exception as exception:
                    raiseException(response, exception)
                raiseExceptionIfNeeded(response)
                completeResponse = getCompleteResponse(response, responseClass)
                FlaskManager.validateResponseClass(responseClass, completeResponse)
            except Exception as exception :
                log.debug(innerResourceInstanceMethod, 'Not posssible to complete request', exception=exception)
                raise exception
            clientResponseStatus = completeResponse[-1]
            clientResponseHeaders = completeResponse[1]
            clientResponseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : HttpStatus.map(clientResponseStatus).enumName}
            if logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    'Response',
                    {
                        'headers': clientResponseHeaders,
                        'body': Serializer.getObjectAsDictionary(clientResponseBody),
                        'status': clientResponseStatus
                    },
                    condition = logResponse,
                    logLevel = log.INFO
                )
            if returnOnlyBody:
                return completeResponse[0]
            else:
                return completeResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        innerResourceInstanceMethod.url = clientMethodUrl
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


def raiseException(response, exception):
        raise GlobalException(
            logMessage = getErrorMessage(response, exception=exception)
        )

def raiseExceptionIfNeeded(response):
    if ObjectHelper.isNone(response) or ObjectHelper.isNone(response.status_code) or 500 <= response.status_code:
        raise GlobalException(logMessage = getErrorMessage(response))
    elif 400 <= response.status_code :
        raise GlobalException(
            message = getErrorMessage(response),
            status = HttpStatus.map(response.status_code),
            logMessage = ERROR_AT_CLIENT_CALL_MESSAGE
        )

def getCompleteResponse(response, responseClass, fallbackStatus=HttpStatus.INTERNAL_SERVER_ERROR):
    responseBody, responseHeaders, responseStatus = None, None, None
    try :
        responseBody, responseHeaders, responseStatus = response.json(), dict(response.headers), HttpStatus.map(HttpStatus.NOT_FOUND if ObjectHelper.isNone(response.status_code) else response.status_code)
    except Exception as exception :
        tempStatus = None
        responseBody, responseStatus = None, HttpStatus.map(fallbackStatus)
        log.failure(getCompleteResponse, 'Not possible to parse response as json', exception=exception, muteStackTrace=True)
    if ObjectHelper.isNone(responseClass):
        return responseBody, responseHeaders, responseStatus
    else:
        return Serializer.convertFromJsonToObject(responseBody, responseClass), responseHeaders, responseStatus

def getErrorMessage(response, exception=None):
    errorMessage = CLIENT_DID_NOT_SENT_ANY_MESSAGE
    possibleErrorMessage = None
    try :
        if ObjectHelper.isNotNone(response):
            possibleErrorMessage = response.json().get('message', response.json().get('error')).strip()
        if ObjectHelper.isNotNone(possibleErrorMessage) and StringHelper.isNotBlank(possibleErrorMessage):
            errorMessage = f'{c.DOT_SPACE_CAUSE}{possibleErrorMessage}'
        else:
            log.prettyPython(getErrorMessage, 'Client response', response.json(), logLevel=log.DEBUG)
    except Exception as innerException :
        log.warning(getErrorMessage, 'Not possible to get error message from response', exception=innerException)
    exceptionPortion = ERROR_AT_CLIENT_CALL_MESSAGE if ObjectHelper.isNone(exception) or StringHelper.isBlank(exception) else str(exception)
    return f'{exceptionPortion}{c.DOT_SPACE}{errorMessage}'
