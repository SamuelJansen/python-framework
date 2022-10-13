import requests
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function

from python_framework.api.src.constant import HttpClientConstant, LogConstant
from python_framework.api.src.domain import HttpDomain
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.util import Serializer
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.enumeration.HttpStatus import HttpStatus
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service import ExceptionHandler
from python_framework.api.src.service.ExceptionHandler import GlobalException
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.util import ClientUtil
from python_framework.api.src.util.ClientUtil import HttpClientEvent, ManualHttpClientEvent


@Function
def HttpClient(
    url = c.BLANK,
    headers = None,
    timeout = HttpClientConstant.DEFAULT_TIMEOUT,
    eventContext = HttpDomain.CLIENT_CONTEXT,
    logRequest = False,
    logResponse = False
):
    def Wrapper(OuterClass, *args, **kwargs):
        clientUrl = url
        clientHeaders = StaticConverter.getValueOrDefault(headers, dict())
        clientTimeout = timeout
        clientEventContext = eventContext
        clientLogRequest = logRequest
        clientLogResponse = logResponse
        log.wrapper(HttpClient,f'''wrapping {OuterClass.__name__}''')
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
            def options(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.OPTIONS, *args, eventContext=clientEventContext, **kwargs)
            def get(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.GET, *args, eventContext=clientEventContext, **kwargs)
            def post(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.POST, *args, eventContext=clientEventContext, **kwargs)
            def put(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.PUT, *args, eventContext=clientEventContext, **kwargs)
            def patch(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.PATCH, *args, eventContext=clientEventContext, **kwargs)
            def delete(self, *args, **kwargs):
                return HttpClientEvent(HttpDomain.Verb.DELETE, *args, eventContext=clientEventContext, **kwargs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


class ClientMethodConfig:
    def __init__(self,
        url = None,
        headers = None,
        requestHeaderClass = None,
        requestParamClass = None,
        requestClass = None,
        responseClass = None,
        returnOnlyBody = None,
        timeout = None,
        propagateAuthorization = None,
        propagateApiKey = None,
        propagateSession = None,
        produces = None,
        consumes = None,
        logRequest = None,
        logResponse = None
    ):
        self.url = url
        self.headers = headers
        self.requestHeaderClass = requestHeaderClass
        self.requestParamClass = requestParamClass
        self.requestClass = requestClass
        self.responseClass = responseClass
        self.returnOnlyBody = returnOnlyBody
        self.timeout = timeout
        self.propagateAuthorization = propagateAuthorization
        self.propagateApiKey = propagateApiKey
        self.propagateSession = propagateSession
        self.produces = produces
        self.consumes = consumes
        self.logRequest = logRequest
        self.logResponse = logResponse


@Function
def HttpClientMethod(
    url = c.BLANK,
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
    logRequest = True,
    logResponse = True,
    debugIt = False
):
    clientMethodConfig = ClientMethodConfig(
        url = url,
        headers = headers,
        requestHeaderClass = requestHeaderClass,
        requestParamClass = requestParamClass,
        requestClass = requestClass,
        responseClass = responseClass,
        returnOnlyBody = returnOnlyBody,
        timeout = timeout,
        propagateAuthorization = propagateAuthorization,
        propagateApiKey = propagateApiKey,
        propagateSession = propagateSession,
        produces = produces,
        consumes = consumes,
        logRequest = logRequest,
        logResponse = logResponse,
    )
    def innerMethodWrapper(resourceInstanceMethod,*args, **kwargs) :

        def options(
            resourceInstance,
            body = None,
            additionalUrl = None,
            params = None,
            headers = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.OPTIONS
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.options(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def get(
            resourceInstance,
            body = None,
            additionalUrl = None,
            params = None,
            headers = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.GET
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.get(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def post(
            resourceInstance,
            body = None,
            additionalUrl = None,
            headers = None,
            params = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.POST
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.post(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def put(
            resourceInstance,
            body = None,
            additionalUrl = None,
            headers = None,
            params = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.PUT
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.put(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def patch(
            resourceInstance,
            body = None,
            additionalUrl = None,
            headers = None,
            params = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.PATCH
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.patch(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def delete(
            resourceInstance,
            body = None,
            additionalUrl = None,
            headers = None,
            params = None,
            timeout = None,
            logRequest = True,
            **kwargs
        ):
            verb = HttpDomain.Verb.DELETE
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                clientMethodConfig,
                additionalUrl,
                params,
                headers,
                body,
                timeout,
                logRequest
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            clientResponse = requests.delete(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return clientResponse

        def doLogRequest(verb, url, body, params, headers, logRequest, requestKwargs):
            log.info(resourceInstanceMethod, f'{LogConstant.CLIENT_SPACE}{verb}{c.SPACE_DASH_SPACE}{url}')
            if logRequest:
                parsetRequestKwargs = {} if ObjectHelper.isEmpty(requestKwargs) else {'requestKwargs': {**requestKwargs}}
                log.prettyJson(
                    resourceInstanceMethod,
                    LogConstant.CLIENT_REQUEST,
                    {
                        'headers': StaticConverter.getValueOrDefault(headers, dict()),
                        'query': StaticConverter.getValueOrDefault(params, dict()),
                        'body': StaticConverter.getValueOrDefault(body, dict()),
                        **parsetRequestKwargs
                    },
                    condition = True,
                    logLevel = log.INFO
                )

        HTTP_CLIENT_RESOLVERS_MAP = {
            HttpDomain.Verb.OPTIONS : options,
            HttpDomain.Verb.GET : get,
            HttpDomain.Verb.POST : post,
            HttpDomain.Verb.PUT : put,
            HttpDomain.Verb.PATCH : patch,
            HttpDomain.Verb.DELETE : delete
        }

        log.wrapper(HttpClientMethod,f'''wrapping {resourceInstanceMethod.__name__}''')
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
                httpClientEvent = ClientUtil.getHttpClientEvent(resourceInstanceMethod, *args, **kwargs)
                if isinstance(httpClientEvent, ManualHttpClientEvent):
                    completeResponse = httpClientEvent.completeResponse
                elif isinstance(httpClientEvent, HttpClientEvent):
                    try :
                        clientResponse = StaticConverter.getValueOrDefault(
                            HTTP_CLIENT_RESOLVERS_MAP.get(
                                httpClientEvent.verb,
                                ClientUtil.raiseHttpClientEventNotFoundException
                            ),
                            ClientUtil.raiseHttpClientEventNotFoundException
                        )(
                            resourceInstance,
                            *httpClientEvent.args,
                            **httpClientEvent.kwargs
                        )
                    except Exception as exception:
                        ClientUtil.raiseException(clientResponse, exception)
                    ClientUtil.raiseExceptionIfNeeded(clientResponse)
                    completeResponse = ClientUtil.getCompleteResponse(clientResponse, responseClass, produces)
                    FlaskManager.validateCompleteResponse(responseClass, completeResponse)
                else:
                    raise Exception('Unknown http client event')
            except Exception as exception:
                log.log(innerResourceInstanceMethod, 'Failure at client method execution', exception=exception, muteStackTrace=True)
                FlaskManager.raiseAndHandleGlobalException(exception, resourceInstance, resourceInstanceMethod, context=HttpDomain.CLIENT_CONTEXT)
            clientResponseStatus = completeResponse[-1]
            clientResponseHeaders = completeResponse[1]
            clientResponseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : HttpStatus.map(clientResponseStatus).enumName}
            if resourceInstance.logResponse and logResponse :
                log.prettyJson(
                    resourceInstanceMethod,
                    LogConstant.CLIENT_RESPONSE,
                    {
                        'headers': clientResponseHeaders,
                        'body': Serializer.getObjectAsDictionary(clientResponseBody, muteLogs=not debugIt),
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
        innerResourceInstanceMethod.url = clientMethodConfig.url
        innerResourceInstanceMethod.headers = clientMethodConfig.headers
        innerResourceInstanceMethod.requestHeaderClass = clientMethodConfig.requestHeaderClass
        innerResourceInstanceMethod.requestParamClass = clientMethodConfig.requestParamClass
        innerResourceInstanceMethod.requestClass = clientMethodConfig.requestClass
        innerResourceInstanceMethod.responseClass = clientMethodConfig.responseClass
        innerResourceInstanceMethod.returnOnlyBody = clientMethodConfig.returnOnlyBody
        innerResourceInstanceMethod.timeout = clientMethodConfig.timeout
        innerResourceInstanceMethod.propagateAuthorization = clientMethodConfig.propagateAuthorization
        innerResourceInstanceMethod.propagateApiKey = clientMethodConfig.propagateApiKey
        innerResourceInstanceMethod.propagateSession = clientMethodConfig.propagateSession
        innerResourceInstanceMethod.produces = clientMethodConfig.produces
        innerResourceInstanceMethod.consumes = clientMethodConfig.consumes
        innerResourceInstanceMethod.logRequest = clientMethodConfig.logRequest
        innerResourceInstanceMethod.logResponse = clientMethodConfig.logResponse

        return innerResourceInstanceMethod
    return innerMethodWrapper
