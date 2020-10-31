from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from python_helper import Constant as c
from python_helper import log, StringHelper
from python_framework.api.src.helper import Serializer
from python_framework.api.src.service.openapi.OpenApiKey import Key as k
from python_framework.api.src.service.openapi.OpenApiValue import Value as v
from python_framework.api.src.service.openapi import OpenApiDocumentationFile
from python_framework.api.src.service.openapi.OpenApiDocumentationFile import DOCUMENTATION_FILE, KW_OPEN_API, KW_RESOURCE, KW_UI

COLON_DOUBLE_BAR = '://'
LOCAL_HOST = 'localhost'

KW_GET = 'get'
KW_POST = 'post'
KW_PUT = 'put'
KW_PATCH = 'patch'
KW_DELETE = 'delete'

VERB_LIST = [
    KW_GET,
    KW_POST,
    KW_PUT,
    KW_PATCH,
    KW_DELETE
]

ABLE_TO_RECIEVE_BODY_LIST = [
    KW_POST,
    KW_PUT,
    KW_PATCH
]

DEFAULT_CONTENT_TYPE = 'application/json'

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

KW_URL_SET = '__URL_SET__'
KW_DESCRIPTION_LIST = '__DESCRIPTION_LIST__'
KW_CONTROLLER = '__CONTROLLER__'
KW_METHOD = '__METHOD__'

KW_REQUEST = '__KW_REQUEST__'
KW_RESPONSE = '__KW_RESPONSE__'

def addSwagger(apiInstance, appInstance):
    globals = apiInstance.globals
    documentationUrl = f'{c.SLASH}{apiInstance.baseUrl}{c.SLASH}{KW_OPEN_API}'
    swaggerUi = get_swaggerui_blueprint(
        documentationUrl,
        DOCUMENTATION_FILE
    )
    selfSrcPath = f"""src{globals.OS_SEPARATOR}service{globals.OS_SEPARATOR}openapi{globals.OS_SEPARATOR}{__name__.split('.')[-1]}.py"""
    log.debug(addSwagger, f'selfSrcPath at "{selfSrcPath}"')

    apiInstance.documentationFolderPath = f'''{__file__.split(selfSrcPath)[0]}{KW_RESOURCE}{globals.OS_SEPARATOR}{KW_OPEN_API}{KW_UI}'''
    log.debug(addSwagger, f'apiInstance.documentationFolderPath at "{apiInstance.documentationFolderPath}"')

    # apiInstance.documentationFolderPath = f'''{__file__.split(selfSrcPath)[0]}{KW_RESOURCE}{globals.OS_SEPARATOR}{KW_OPEN_API}{KW_UI}{globals.OS_SEPARATOR}'''
    # log.debug(addSwagger, f'apiInstance.documentationFolderPath at "{apiInstance.documentationFolderPath}"')

    swaggerUi._static_folder = apiInstance.documentationFolderPath
    log.debug(addSwagger, f'swaggerUi._static_folder at "{swaggerUi._static_folder}"')

    # apiInstance.documentationFolderPath = swaggerUi._static_folder
    # log.debug(addSwagger, f'apiInstance.documentationFolderPath at "{apiInstance.documentationFolderPath}"')

    appInstance.register_blueprint(swaggerUi, url_prefix=documentationUrl)
    OpenApiDocumentationFile.overrideDocumentation(apiInstance)

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
    globals = apiInstance.globals
    apiInstance.documentation[k.INFO] = {
        k.TITLE : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_TITLE}'),
        k.DESCRIPTION : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_DESCRIPTION}'),
        k.VERSION : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_VERSION}'),
        k.TERMS_OF_SERVICE : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_TERMS_OF_SERVICE}')
    }
    addContact(globals, apiInstance.documentation)
    addLisence(globals, apiInstance.documentation)

def addHostAndBasePath(apiInstance, appInstance):
    globals = apiInstance.globals
    apiInstance.documentation[k.HOST] = globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_HOST}')
    apiInstance.documentation[k.SCHEMES] = globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_SCHEMES}')
    apiInstance.documentation[k.BASE_PATH] = apiInstance.baseUrl
    # completeUrl = appInstance.test_request_context().request.host_url[:-1] ###- request.remote_addr
    # apiInstance.documentation[k.HOST] = completeUrl.split(COLON_DOUBLE_BAR)[1]
    # if LOCAL_HOST in apiInstance.documentation[k.HOST] :
    #     apiInstance.documentation[k.HOST] = f'{apiInstance.documentation[k.HOST]}:5000'
    # apiInstance.documentation[k.BASE_PATH] = apiInstance.baseUrl
    # apiInstance.documentation[k.SCHEMES] = [completeUrl.split(COLON_DOUBLE_BAR)[0]]

def addEndPointDocumentation(endPointUrl, controllerMethod, controller, apiInstance):
    url = getUrl(endPointUrl, apiInstance.baseUrl)
    addUrlIfNeeded(url, apiInstance.documentation)
    verb = controllerMethod.__name__
    if verb in [KW_GET, KW_POST, KW_PUT, KW_DELETE, KW_PATCH] :
        addVerb(verb, url, apiInstance.documentation)
        addTagToUrlVerb(verb, url, controller.tag, apiInstance.documentation)
        addConsumesAndProducesToUrlVerb(verb, url, controllerMethod.consumes, controllerMethod.produces, apiInstance.documentation)
        addSecurity(verb, url, controllerMethod.roleRequired, apiInstance.documentation)
        addUrlParamListToUrlVerb(verb, url, endPointUrl, apiInstance.documentation)
        addRequestToUrlVerb(verb, url, controllerMethod.requestClass, apiInstance.documentation)
        addResponseToUrlVerb(verb, url, controllerMethod.responseClass, apiInstance.documentation)

def addControllerDocumentation(controller, apiInstance) :
    tag = getTagByTagName(controller.tag, apiInstance.documentation)
    if not tag :
        apiInstance.documentation[k.TAGS].append({
            k.NAME : controller.tag,
            k.DESCRIPTION : controller.description,
            k.EXTERNAL_DOCS : None
        })
    else :
        tag[k.DESCRIPTION] += f'. {controller.description}'

################################################################################

def getTagByTagName(tagName, documentation):
    for tag in documentation[k.TAGS] :
        if tagName == tag[k.NAME] :
            return tag

def addContact(globals, documentation):
    documentation[k.INFO][k.CONTACT] = {
        k.NAME : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_CONTACT}.{KW_NAME}'),
        k.EMAIL : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_CONTACT}.{KW_EMAIL}')
    }

def addLisence(globals, documentation):
    documentation[k.INFO][k.LICENSE] = {
        k.NAME : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_LICENSE}.{KW_NAME}'),
        k.URL : globals.getApiSetting(f'{KW_API}.{KW_INFO}.{KW_LICENSE}.{KW_URL}')
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
    # if c.LESSER in url :
    #     attributeList = url.split(c.LESSER)
    #     for attributeUrl in attributeList :
    #         if c.BIGGER in attributeUrl :
    #             filteredAttributeUrl = attributeUrl.split(c.BIGGER)[0]
    #             attributeUrlTypeAndName = filteredAttributeUrl.split(c.COLON)
    #             documentation[k.PATHS][url][verb][k.PARAMETERS].append({
    #                 k.NAME : attributeUrlTypeAndName[1],
    #                 k.TYPE : getAttributeType(attributeUrlTypeAndName[0]),
    #                 k.IN : v.PATH,
    #                 k.REQUIRED: True,
    #                 k.DESCRIPTION : None
    #             })
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

def getAttributeType(typeUrlParam):
    if c.TYPE_INTEGER == typeUrlParam :
        return v.INTEGER
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

def addDtoToUrlVerb(verb, url, dtoClass, documentation, dtoType=v.OBJECT, where=None):
    if dtoClass :
        if not isinstance(dtoClass, list) :
            if not c.TYPE_DICT == dtoClass.__name__ :
                dtoName = dtoClass.__name__
                if KW_REQUEST == where :
                    documentation[k.PATHS][url][verb][k.PARAMETERS].append({
                        k.NAME : v.BODY,
                        k.TYPE : v.OBJECT,
                        k.IN : v.BODY,
                        k.REQUIRED: True,
                        k.DESCRIPTION : None,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    })
                if KW_RESPONSE == where :
                    documentation[k.PATHS][url][verb][k.RESPONSES][k.DEFAULT_STATUS_CODE] = {
                        k.DESCRIPTION : v.DEFAULT_RESPONSE,
                        k.SCHEMA : getDtoSchema(dtoName, dtoType, dtoClass)
                    }
                if not dtoClass.__name__ in documentation[k.DEFINITIONS] :
                    dtoClassDoc = {}
                    documentation[k.DEFINITIONS][dtoClass.__name__] = dtoClassDoc
                    dtoClassDoc[k.TYPE] = v.OBJECT
                    dtoClassDoc[k.PROPERTIES] = {}
                    dtoClassDoc[k.REQUIRED] = Serializer.getAttributeNameList(dtoClass)
                    for attributeName in dtoClassDoc[k.REQUIRED] :
                        attributeType = getTypeFromAttributeNameAndChildDtoClass(attributeName)
                        childDtoClass = getNullableChildDtoClass(attributeName, dtoClass,  verb, url, documentation)
                        if childDtoClass :
                            dtoClassDoc[k.PROPERTIES][attributeName] = getDtoSchema(attributeName, attributeType, childDtoClass)
                        else :
                            dtoClassDoc[k.PROPERTIES][attributeName] = {
                                k.TYPE : attributeType,
                                k.EXAMPLE : None
                            }
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

def getTypeFromAttributeNameAndChildDtoClass(attributeName):
    if attributeName :
        if Serializer.DTO_SUFIX in attributeName :
            return v.OBJECT
        if Serializer.LIST_SUFIX in attributeName :
            return v.ARRAY

def getRefferenceValue(name):
    return f'#/{k.DEFINITIONS}/{name}'

def getDtoSchema(attributeName, attributeType, dtoClass):
    if dtoClass :
        dtoName = dtoClass.__name__
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

def addSecurity(verb, url, roleRequired, documentation):
    if roleRequired :
        documentation[k.PATHS][url][verb][k.PARAMETERS].append({
            k.NAME : v.AUTHORIZATION,
            k.DESCRIPTION : v.BEARER_TOKEN,
            k.IN : v.HEADER,
            k.REQUIRED: True,
            k.TYPE : v.STRING
        })


def getNullableChildDtoClass(attributeName, dtoClass, verb, url, documentation):
    childDtoClass = Serializer.getDtoClassFromFatherClassAndChildMethodName(dtoClass, attributeName)
    if childDtoClass :
        addDtoToUrlVerb(verb, url, childDtoClass, documentation)
    return childDtoClass
