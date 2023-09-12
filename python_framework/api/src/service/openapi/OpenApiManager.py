from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from python_helper import Constant as c
from python_helper import log, StringHelper, ReflectionHelper, ObjectHelper
from python_framework.api.src.util import Serializer
from python_framework.api.src.service.openapi.OpenApiKey import Key as k
from python_framework.api.src.service.openapi.OpenApiValue import Value as v
from python_framework.api.src.service.openapi import OpenApiDocumentationFile
from python_framework.api.src.service.openapi.OpenApiDocumentationFile import KW_OPEN_API, KW_UI
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.constant import JwtConstant, ConfigurationKeyConstant


KW_GET = 'get'
KW_POST = 'post'
KW_PUT = 'put'
KW_PATCH = 'patch'
KW_DELETE = 'delete'
KW_OPTIONS = 'options'

VERB_LIST = [
    KW_GET,
    KW_POST,
    KW_PUT,
    KW_PATCH,
    KW_DELETE,
    KW_OPTIONS
]

ABLE_TO_RECIEVE_BODY_LIST = [
    KW_POST
    , KW_PUT
    , KW_PATCH
    , KW_DELETE
    , KW_OPTIONS
]

TYPE_NUMBER_LIST = [
    c.TYPE_FLOAT,
    'double'
]

DEFAULT_CONTENT_TYPE = 'application/json'
MULTIPART_X_MIXED_REPLACE = 'multipart/x-mixed-replace'
JSON_OBJECT_NAME = 'json'

KW_API = 'api'
KW_INFO = 'info'
KW_DESCRIPTION = 'description'
KW_TITLE = 'title'
KW_VERSION = 'version'
KW_TERMS_OF_SERVICE = 'terms-of-service'
KW_CONTACT = 'contact'
KW_LICENSE = 'license'
KW_NAME = 'name'
KW_EMAIL = 'email'
KW_URL = 'url'
KW_HOST = 'host'
KW_SCHEMES = 'schemes'
KW_PORT: str = 'port'

KW_URL_SET = '__URL_SET__'
KW_DESCRIPTION_LIST = '__DESCRIPTION_LIST__'
KW_CONTROLLER = '__CONTROLLER__'
KW_METHOD = '__METHOD__'

KW_REQUEST = '__KW_REQUEST__'
KW_RESPONSE = '__KW_RESPONSE__'

DOCUMENTATION_ENDPOINT = f'{c.SLASH}{KW_OPEN_API}'
ZERO_DOT_ZERO_DOT_ZERO_DOT_ZERO_HOST = "0.0.0.0"
LOCALHOST_HOST = 'localhost'
SCHEME_HOST_SEPARATOR = '://'
DEFAULT_DOCUMENTATION_PORT = '80'
PORT_80_IN_URL = ':80/'
URL_ENDS_WITH_PORT_80 = ':80'
PORT_80_EXCLUDED_FROM_URL = '/'

def addSwagger(apiInstance, appInstance):
    ###- The ugliest thing I ever seen, but thats the way flask_swagger_ui works...
    documentationUrl = f'{apiInstance.baseUrl}{DOCUMENTATION_ENDPOINT}'
    swaggerUi = get_swaggerui_blueprint(
        documentationUrl,
        OpenApiDocumentationFile.getDocumentationFileName(apiInstance)
    )
    @appInstance.route(f'{documentationUrl}/{OpenApiDocumentationFile.getDocumentationFileName(apiInstance)}', methods=['GET'])
    def getSwagger() :
        return apiInstance.documentation
    appInstance.register_blueprint(swaggerUi, url_prefix=documentationUrl)
    OpenApiDocumentationFile.overrideDocumentation(apiInstance)

def getStaticFolder(apiInstance, appInstance):
    globalsInstance = apiInstance.globals
    pythonFrameworkStaticFiles = f'{globalsInstance.OS_SEPARATOR}python_framework{globalsInstance.OS_SEPARATOR}api{globalsInstance.OS_SEPARATOR}resource'
    swaggerStaticFiles = f'{globalsInstance.OS_SEPARATOR}{KW_OPEN_API}{KW_UI}{globalsInstance.OS_SEPARATOR}'
    apiInstance.documentationFolderPath = f'{globalsInstance.staticPackage}{pythonFrameworkStaticFiles}{swaggerStaticFiles}'
    log.debug(getStaticFolder, f'apiInstance.documentationFolderPath at "{apiInstance.documentationFolderPath}"')
    return apiInstance.documentationFolderPath

################################################################################

def newDocumentation(apiInstance, appInstance):
    documentation = {
        k.SWAGGER_VERSION : v.SWAGGER_VERSION,
        k.PATHS : {},
        k.DEFINITIONS : {},
        k.TAGS : []
    }
    apiInstance.documentation = documentation
    addHostAndBasePath(apiInstance, appInstance)
    addInfo(apiInstance)

def addInfo(apiInstance):
    globalsInstance = apiInstance.globals
    apiInstance.documentation[k.INFO] = {
        k.TITLE : StaticConverter.getValueOrDefault(globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_TITLE}'), StringHelper.toTitle(globalsInstance.apiName)),
        k.DESCRIPTION : StaticConverter.getValueOrDefault(globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_DESCRIPTION}'), f'This is a {StringHelper.toTitle(globalsInstance.apiName)} service'),
        k.VERSION : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_VERSION}'),
        k.TERMS_OF_SERVICE : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_TERMS_OF_SERVICE}')
    }
    addContact(globalsInstance, apiInstance.documentation)
    addLisence(globalsInstance, apiInstance.documentation)

def addHostAndBasePath(apiInstance, appInstance):
    globalsInstance = apiInstance.globals
    apiInstance.documentation[k.HOST] = globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_HOST}')
    apiInstance.documentation[k.SCHEMES] = globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_SCHEMES}')
    apiInstance.documentation[k.BASE_PATH] = apiInstance.baseUrl
    # completeUrl = appInstance.test_request_context().request.host_url[:-1] ###- request.remote_addr
    # apiInstance.documentation[k.HOST] = completeUrl.split('://')[1]
    # if 'localhost' in apiInstance.documentation[k.HOST] :
    #     apiInstance.documentation[k.HOST] = f'{apiInstance.documentation[k.HOST]}:5000'
    # apiInstance.documentation[k.BASE_PATH] = apiInstance.baseUrl
    # apiInstance.documentation[k.SCHEMES] = [completeUrl.split('://')[0]]

def addEndPointDocumentation(endPointUrl, controllerMethod, controller, apiInstance):
    try :
        url = getUrl(endPointUrl, apiInstance.baseUrl)
        addUrlIfNeeded(url, apiInstance.documentation)
        verb = ReflectionHelper.getName(controllerMethod, muteLogs=True)
        if verb in [KW_GET, KW_POST, KW_PUT, KW_DELETE, KW_PATCH] :
            addVerb(verb, url, apiInstance.documentation)
            addTagToUrlVerb(verb, url, controller.tag, apiInstance.documentation)
            addConsumesAndProducesToUrlVerb(verb, url, controllerMethod.consumes, controllerMethod.produces, apiInstance.documentation)
            addSession(verb, url, controllerMethod.contextRequired, apiInstance.documentation, apiInstance.globals)
            addApiKey(verb, url, controllerMethod.apiKeyRequired, apiInstance.documentation, apiInstance.globals)
            addSecurity(verb, url, controllerMethod.roleRequired, apiInstance.documentation, apiInstance.globals)
            addHeadersListToUrlVerb(verb, url, endPointUrl, controllerMethod.requestHeaderClass, apiInstance.documentation)
            addUrlParamListToUrlVerb(verb, url, endPointUrl, apiInstance.documentation)
            addQueryParamListToUrlVerb(verb, url, endPointUrl, controllerMethod.requestParamClass, apiInstance.documentation)
            addRequestToUrlVerb(verb, url, controllerMethod.requestClass, apiInstance.documentation)
            addResponseToUrlVerb(verb, url, controllerMethod.responseClass, apiInstance.documentation)
    except Exception as exception :
        log.failure(addEndPointDocumentation, 'Not possible to add end point documentation', exception)

def addControllerDocumentation(controller, apiInstance) :
    try :
        tag = getTagByTagName(controller.tag, apiInstance.documentation)
        if not tag :
            apiInstance.documentation[k.TAGS].append({
                k.NAME : controller.tag,
                k.DESCRIPTION : controller.description,
                k.EXTERNAL_DOCS : None
            })
        else :
            tag[k.DESCRIPTION] += f'. {controller.description}'
    except Exception as exception :
        log.failure(addControllerDocumentation, 'Not possible to add controller documentation', exception)

################################################################################

def getTagByTagName(tagName, documentation):
    for tag in documentation[k.TAGS] :
        if tagName == tag[k.NAME] :
            return tag

def addContact(globalsInstance, documentation):
    documentation[k.INFO][k.CONTACT] = {
        k.NAME : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_CONTACT}.{KW_NAME}'),
        k.EMAIL : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_CONTACT}.{KW_EMAIL}')
    }

def addLisence(globalsInstance, documentation):
    documentation[k.INFO][k.LICENSE] = {
        k.NAME : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_LICENSE}.{KW_NAME}'),
        k.URL : globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_INFO}.{KW_LICENSE}.{KW_URL}')
    }

def addUrlIfNeeded(url, documentation):
    if not documentation[k.PATHS].get(url) :
        documentation[k.PATHS][url] = {}

def addVerb(verb, url, documentation):
    if not documentation[k.PATHS][url].get(verb) :
        documentation[k.PATHS][url][verb] = {
            k.PARAMETERS : [],
            k.TAGS : [],
            k.CONSUMES : [],
            k.PRODUCES : []
        }
    else :
        raise Exception(f'Duplicated "{verb}" verb in {url} url')

def addTagToUrlVerb(verb, url, tag, documentation):
    if not tag in documentation[k.PATHS][url][verb][k.TAGS] :
        documentation[k.PATHS][url][verb][k.TAGS].append(tag)

def addConsumesAndProducesToUrlVerb(verb, url, consumes, produces, documentation) :
    if not consumes in documentation[k.PATHS][url][verb][k.CONSUMES] :
        documentation[k.PATHS][url][verb][k.CONSUMES].append(consumes)
    if not produces in documentation[k.PATHS][url][verb][k.PRODUCES] :
        documentation[k.PATHS][url][verb][k.PRODUCES].append(produces)

def addUrlParamListToUrlVerb(verb, url, endPointUrl, documentation):
    if c.LESSER in endPointUrl :
        attributeList = endPointUrl.split(c.LESSER)
        for attributeUrl in attributeList :
            if c.BIGGER in attributeUrl :
                filteredAttributeUrl = attributeUrl.split(c.BIGGER)[0]
                attributeUrlTypeAndName = filteredAttributeUrl.split(c.COLON)
                documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                    k.NAME : attributeUrlTypeAndName[1],
                    k.TYPE : getAttributeType(attributeUrlTypeAndName[0]),
                    k.IN : v.PATH,
                    k.REQUIRED: True,
                    k.DESCRIPTION : None
                })

def addQueryParamListToUrlVerb(verb, url, endPointUrl, requestParamClass, documentation):
    if ObjectHelper.isList(requestParamClass) and 0 == len(requestParamClass):
        log.warning(addQueryParamListToUrlVerb, f'Invalid request param class. requestParamClass: {requestParamClass}')
    if ObjectHelper.isNotNone(requestParamClass):
        log.log(addQueryParamListToUrlVerb, f'verb: {verb}, url: {url}, requestParamClass: {requestParamClass}')
        if ObjectHelper.isNotList(requestParamClass):
            for attributeName in ReflectionHelper.getAttributeOrMethodNameList(requestParamClass):
                documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                    k.NAME : attributeName,
                    k.TYPE : v.STRING,
                    k.IN : v.QUERY,
                    k.REQUIRED: False,
                    k.DESCRIPTION : None
                })
        elif 1 == len(requestParamClass) :
            if ObjectHelper.isNotNone(requestParamClass[0]):
                if ObjectHelper.isNotList(requestParamClass[0]):
                    addQueryParamListToUrlVerb(verb, url, endPointUrl, requestParamClass[0], documentation) ###-, where=where
                elif ObjectHelper.isList(requestParamClass[0]) and 1 == len(requestParamClass[0]):
                    if ObjectHelper.isNotNone(requestParamClass[0][0]) and ObjectHelper.isNotList(requestParamClass[0][0]) :
                        # addQueryParamListToUrlVerb(verb, url, endPointUrl, requestParamClass[0][0], documentation) ###-, where=where
                        log.warning(addQueryParamListToUrlVerb, f'Request param class as list not implemented yet. requestParamClass: {requestParamClass}')
        else:
            log.warning(addQueryParamListToUrlVerb, f'Unexpected request param class. requestParamClass: {requestParamClass}')

def addHeadersListToUrlVerb(verb, url, endPointUrl, requestHeaderClass, documentation):
    if ObjectHelper.isList(requestHeaderClass) and 0 == len(requestHeaderClass):
        log.warning(addHeadersListToUrlVerb, f'Invalid request header class. requestHeaderClass: {requestHeaderClass}')
    if ObjectHelper.isNotNone(requestHeaderClass):
        log.log(addHeadersListToUrlVerb, f'verb: {verb}, url: {url}, requestHeaderClass: {requestHeaderClass}')
        if ObjectHelper.isNotList(requestHeaderClass):
            for attributeName in ReflectionHelper.getAttributeOrMethodNameList(requestHeaderClass):
                documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                    k.NAME : attributeName,
                    k.IN : v.HEADER,
                    k.TYPE : v.STRING,
                    k.REQUIRED: True,
                    k.DESCRIPTION : None
                })
        elif 1 == len(requestHeaderClass) :
            if ObjectHelper.isNotNone(requestHeaderClass[0]):
                if ObjectHelper.isNotList(requestHeaderClass[0]):
                    addHeadersListToUrlVerb(verb, url, endPointUrl, requestHeaderClass[0], documentation) ###-, where=where
                elif ObjectHelper.isList(requestHeaderClass[0]) and 1 == len(requestHeaderClass[0]):
                    if ObjectHelper.isNotNone(requestHeaderClass[0][0]) and ObjectHelper.isNotList(requestHeaderClass[0][0]) :
                        # addHeadersListToUrlVerb(verb, url, endPointUrl, requestHeaderClass[0][0], documentation) ###-, where=where
                        log.warning(addHeadersListToUrlVerb, f'Request header class as list not implemented yet. requestHeaderClass: {requestHeaderClass}')
        else:
            log.warning(addHeadersListToUrlVerb, f'Unexpected request header class. requestHeaderClass: {requestHeaderClass}')

def getAttributeType(typeUrlParam):
    if c.TYPE_INTEGER == typeUrlParam :
        return v.INTEGER
    if c.TYPE_STRING == typeUrlParam:
        return v.STRING
    if typeUrlParam in TYPE_NUMBER_LIST:
        return v.NUMBER
    return typeUrlParam

def getUrl(endPointUrl, baseUrl):
    endPointUrlList = endPointUrl.replace(baseUrl, c.NOTHING).split(c.SLASH)
    urlList = []
    for urlPiece in endPointUrlList :
        if urlPiece :
            splittedUrlPiece = urlPiece.split(c.COLON)
            if len(splittedUrlPiece) > 1 :
                if c.BIGGER in splittedUrlPiece[1] :
                    urlList.append(f'{c.OPEN_DICTIONARY}{splittedUrlPiece[1].split(c.BIGGER)[0]}{c.CLOSE_DICTIONARY}')
            else :
                urlList.append(urlPiece)
    return f'{c.SLASH}{c.SLASH.join(urlList)}'

def getApiUrl(apiInstance):
    ###- return f'{apiInstance.scheme}{SCHEME_HOST_SEPARATOR}{apiInstance.host}{apiInstance.baseUrl}'.replace(ZERO_DOT_ZERO_DOT_ZERO_DOT_ZERO_HOST, LOCALHOST_HOST)
    globalsInstance = apiInstance.globals
    sheme = StaticConverter.getValueOrDefault(StaticConverter.getValueOrDefault(globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_SCHEMES}'), [apiInstance.scheme]), [apiInstance.scheme])[0]
    host = StaticConverter.getValueOrDefault(globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_HOST}'), apiInstance.host).replace(ZERO_DOT_ZERO_DOT_ZERO_DOT_ZERO_HOST, LOCALHOST_HOST)
    colonPortIfAny = StaticConverter.getValueOrDefault(f"{c.COLON}{globalsInstance.getSetting(f'{KW_OPEN_API}.{KW_PORT}')}", c.BLANK).replace(PORT_80_IN_URL, PORT_80_EXCLUDED_FROM_URL).replace(f'{c.COLON}None', c.BLANK)
    exposedHostApiUrl = f'{sheme}{SCHEME_HOST_SEPARATOR}{host}{colonPortIfAny}{apiInstance.baseUrl}'
    return f'{exposedHostApiUrl}'.replace(PORT_80_IN_URL, PORT_80_EXCLUDED_FROM_URL).replace(ZERO_DOT_ZERO_DOT_ZERO_DOT_ZERO_HOST, LOCALHOST_HOST)

def getDocumentationUrl(apiInstance):
    return f'{getApiUrl(apiInstance)}{DOCUMENTATION_ENDPOINT}'

def addDtoToUrlVerb(verb, url, dtoClass, documentation, dtoType=v.OBJECT, where=None):
    log.log(addDtoToUrlVerb, f'verb: {verb}, url: {url}, dtoClass: {dtoClass}, dtoType: {dtoType}, where: {where}')
    if dtoClass :
        if not isinstance(dtoClass, list) :
            if not c.TYPE_DICT == ReflectionHelper.getName(dtoClass, muteLogs=True) :
                dtoName = getDtoDocumentationName(dtoClass)
                if KW_REQUEST == where :
                    documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                        k.NAME : v.BODY,
                        k.TYPE : v.OBJECT,
                        k.IN : v.BODY,
                        k.REQUIRED: True,
                        k.DESCRIPTION : None,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    })
                elif KW_RESPONSE == where :
                    documentation[k.PATHS][url][verb][k.RESPONSES][k.DEFAULT_STATUS_CODE] = {
                        k.DESCRIPTION : v.DEFAULT_RESPONSE,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    }
                if not dtoName in documentation[k.DEFINITIONS] :
                    dtoClassDoc = {}
                    documentation[k.DEFINITIONS][dtoName] = dtoClassDoc
                    dtoClassDoc[k.TYPE] = v.OBJECT
                    dtoClassDoc[k.PROPERTIES] = {}
                    dtoClassDoc[k.REQUIRED] = ReflectionHelper.getAttributeNameList(dtoClass)
                    for attributeName in dtoClassDoc[k.REQUIRED] :
                        attributeType = getTypeFromAttributeNameAndChildDtoClass(attributeName, dtoType)
                        childDtoClass = getNullableChildDtoClass(attributeName, dtoClass,  verb, url, documentation)
                        if childDtoClass :
                            dtoClassDoc[k.PROPERTIES][attributeName] = getDtoSchema(attributeName, attributeType, childDtoClass)
                        else :
                            dtoClassDoc[k.PROPERTIES][attributeName] = {
                                k.TYPE : attributeType,
                                k.EXAMPLE : None
                            }
            else :
                dtoName = getDtoDocumentationName(dtoClass)
                if KW_REQUEST == where :
                    documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                        k.NAME : v.BODY,
                        k.TYPE : v.OBJECT,
                        k.IN : v.BODY,
                        k.REQUIRED: True,
                        k.DESCRIPTION : None,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    })
                elif KW_RESPONSE == where :
                    documentation[k.PATHS][url][verb][k.RESPONSES][k.DEFAULT_STATUS_CODE] = {
                        k.DESCRIPTION : v.DEFAULT_RESPONSE,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    }
                if not dtoName in documentation[k.DEFINITIONS] :
                    dtoClassDoc = {}
                    documentation[k.DEFINITIONS][dtoName] = dtoClassDoc
                    dtoClassDoc[k.TYPE] = v.OBJECT
                    dtoClassDoc[k.PROPERTIES] = {}
                    dtoClassDoc[k.REQUIRED] = []

        elif 1 == len(dtoClass) :
            if dtoClass[0] and not isinstance(dtoClass[0], list) :
                addDtoToUrlVerb(verb, url, dtoClass[0], documentation, where=where)
            elif 1 == len(dtoClass[0]) :
                if dtoClass[0][0] and not isinstance(dtoClass[0][0], list) :
                    addDtoToUrlVerb(verb, url, dtoClass[0][0], documentation, dtoType=v.ARRAY, where=where)

def addRequestToUrlVerb(verb, url, requestClass, documentation):
    addDtoToUrlVerb(verb, url, requestClass, documentation, where=KW_REQUEST)

def addResponseToUrlVerb(verb, url, responseClass, documentation):
    if not documentation[k.PATHS][url][verb].get(k.RESPONSES) :
        documentation[k.PATHS][url][verb][k.RESPONSES] = {
            k.DEFAULT_STATUS_CODE : {
                k.DESCRIPTION : v.DEFAULT_RESPONSE
            }
        }
    addDtoToUrlVerb(verb, url, responseClass, documentation, where=KW_RESPONSE)

def getTypeFromAttributeNameAndChildDtoClass(attributeName, fatherType):
    if attributeName :
        if Serializer.LIST_SUFIX in attributeName :
            return v.ARRAY
        if Serializer.DTO_SUFIX in attributeName or v.OBJECT == fatherType :
            return v.OBJECT

def getRefferenceValue(name):
    return f'#/{k.DEFINITIONS}/{name}'

def getDtoDocumentationName(objectClass) :
    if ObjectHelper.isDictionaryClass(objectClass) :
        return JSON_OBJECT_NAME
    else:
        return ReflectionHelper.getName(objectClass, muteLogs=True)

def getDtoSchema(attributeName, attributeType, dtoClass):
    log.log(getDtoSchema, f'attributeName: {attributeName}, attributeType: {attributeType}, dtoClass: {dtoClass}')
    if dtoClass :
        dtoName = getDtoDocumentationName(dtoClass)
        if v.ARRAY == attributeType :
            return {
                k.TYPE : v.ARRAY,
                k.ITEMS : {
                    k.TYPE : v.OBJECT,
                    k.S_REF : getRefferenceValue(dtoName)
                }
            }
        if v.OBJECT == attributeType :
            return {
                k.S_REF : getRefferenceValue(dtoName)
            }
        return {}

def addSession(verb, url, contextRequired, documentation, globalsInstance):
    if contextRequired :
        documentation[k.PATHS][url][verb][k.PARAMETERS].append({
            k.NAME : StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SESSION_HEADER), JwtConstant.DEFAULT_JWT_SESSION_HEADER_NAME),
            k.DESCRIPTION : f'{StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SESSION_TYPE), JwtConstant.DEFAULT_JWT_SESSION_HEADER_TYPE)}{c.SPACE}{v.TOKEN_DESCRIPTION}',
            k.IN : v.HEADER,
            k.REQUIRED: True,
            k.TYPE : v.STRING
        })

def addApiKey(verb, url, apiKeyRequired, documentation, globalsInstance):
    if apiKeyRequired :
        documentation[k.PATHS][url][verb][k.PARAMETERS].append({
            k.NAME : StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_API_KEY_HEADER), JwtConstant.DEFAULT_JWT_API_KEY_HEADER_NAME),
            k.DESCRIPTION : f'{StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_API_KEY_TYPE), JwtConstant.DEFAULT_JWT_API_KEY_HEADER_TYPE)}{c.SPACE}{v.TOKEN_DESCRIPTION}',
            k.IN : v.HEADER,
            k.REQUIRED: True,
            k.TYPE : v.STRING
        })

def addSecurity(verb, url, roleRequired, documentation, globalsInstance):
    if roleRequired :
        documentation[k.PATHS][url][verb][k.PARAMETERS].append({
            k.NAME : StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SECURITY_HEADER), JwtConstant.DEFAULT_JWT_SECURITY_HEADER_NAME),
            k.DESCRIPTION : f'{StaticConverter.getValueOrDefault(globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SECURITY_TYPE), JwtConstant.DEFAULT_JWT_API_KEY_HEADER_TYPE)}{c.SPACE}{v.TOKEN_DESCRIPTION}',
            k.IN : v.HEADER,
            k.REQUIRED: True,
            k.TYPE : v.STRING
        })


def getNullableChildDtoClass(attributeName, dtoClass, verb, url, documentation):
    log.log(getNullableChildDtoClass, f'attributeName: {attributeName}, dtoClass: {dtoClass}, verb: {verb}, url: {url}')
    childDtoClass = Serializer.getTargetClassFromFatherClassAndChildMethodName(dtoClass, attributeName)
    log.log(getNullableChildDtoClass, f'childDtoClass: {childDtoClass}')
    if childDtoClass :
        if ReflectionHelper.getName(type(type)) == ReflectionHelper.getName(type(childDtoClass)) :
            addDtoToUrlVerb(verb, url, childDtoClass, documentation)
        else :
            addDtoToUrlVerb(verb, url, type(childDtoClass), documentation)
    return childDtoClass
