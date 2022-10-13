from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from python_helper import Constant as c
from python_helper import log, Function, ReflectionHelper, ObjectHelper, StringHelper
import globals
from python_framework.api.src.constant import ControllerConstant
from python_framework.api.src.constant import ConfigurationKeyConstant
from python_framework.api.src.constant import StaticConstant
from python_framework.api.src.constant import HealthCheckConstant
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.converter.static import StaticConverter
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service import SqlAlchemyProxy
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service import SchedulerManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.service import DefaultExceptionManager


DOT_PY = '.py'


def getPythonFrameworkResourceByType(resourceType):
    return FlaskManager.PYTHON_FRAMEWORK_RESOURCE_NAME_DICTIONARY.get(resourceType, [])


def isNotPythonFrameworkApiInstance(apiInstance):
    return apiInstance.globals.apiName not in FlaskManager.PYTHON_FRAMEWORK_INTERNAL_MODULE_NAME_LIST


def isFromPythonFramework(apiInstance, resourceType, resourceName):
    return not (resourceName in getPythonFrameworkResourceByType(resourceType) and isNotPythonFrameworkApiInstance(apiInstance))


def getResourceModuleNameAjusted(apiInstance, resourceType, resourceName):
    return resourceName if isFromPythonFramework(apiInstance, resourceType, resourceName) else FlaskManager.PYTHON_FRAMEWORK_MODULE_NAME


def getResourceNameAjusted(apiInstance, resourceType, resourceName):
    return resourceName if isFromPythonFramework(apiInstance, resourceType, resourceName) else f'{resourceName}{c.DOT}{resourceName}'


def isControllerResourceName(resourceName):
    return FlaskManager.KW_CONTROLLER_RESOURCE == resourceName[-len(FlaskManager.KW_CONTROLLER_RESOURCE):]


@Function
def getResourceName(resourceFileName):
    return resourceFileName.split(DOT_PY)[0]


@Function
def isResourceType(resourceFileName, resourceType):
    splitedResourceFileName = resourceFileName.split(resourceType)
    return len(splitedResourceFileName) > 1 and not splitedResourceFileName[0].endswith(FlaskManager.KW_STATIC_RESOURCE_PREFIX) and splitedResourceFileName[1] == DOT_PY


@Function
def getResourceNameList(apiTree, resourceType):
    resourceNameList = []
    if apiTree or type(apiTree).__name__ == c.DICT:
        for package,subPackageTree in apiTree.items():
            if isResourceType(package, resourceType):
                resourceNameList.append(getResourceName(package))
            resourceNameList += getResourceNameList(
                subPackageTree,
                resourceType
            )
    return resourceNameList


@Function
def getControllerNameList(controllerName):
    # controllerNameList = [
    #     name for name in dir(globals.importModule(controllerName)) if not name.startswith(c.UNDERSCORE) and name.endswith(FlaskManager.KW_CONTROLLER_RESOURCE)
    # ]
    controllerNameList = [controllerName]
    for controllerType in ControllerConstant.CONTROLLER_TYPE_LIST:
        controllerNameList.append(f'{controllerName[:-len(FlaskManager.KW_CONTROLLER_RESOURCE)]}{controllerType}{FlaskManager.KW_CONTROLLER_RESOURCE}')
    return controllerNameList


@Function
def getControllerList(resourceName, resourceModuleName):
    controllerNameList = getControllerNameList(resourceName)
    importedControllerList = []
    for controllerName in controllerNameList:
        resource = globals.importResource(controllerName, resourceModuleName=resourceModuleName)
        if ObjectHelper.isNotNone(resource):
            importedControllerList.append(resource)
    if 0 == len(importedControllerList):
        raise Exception(f'Not possible to import {resourceName} controller')
    return importedControllerList


@Function
def getResourceList(apiInstance, resourceType):
    resourceNameList = getResourceNameList(
        apiInstance.globals.apiTree[apiInstance.globals.apiPackage],
        resourceType
    )
    if isNotPythonFrameworkApiInstance(apiInstance):
        resourceNameList += getPythonFrameworkResourceByType(resourceType)
    resourceList = []
    for resourceName in resourceNameList:
        resource = None
        ajustedResourceName = getResourceNameAjusted(apiInstance, resourceType, resourceName)
        ajustedResourceModuleName = getResourceModuleNameAjusted(apiInstance, resourceType, resourceName)
        if isControllerResourceName(resourceName):
            resource = getControllerList(ajustedResourceName, ajustedResourceModuleName)
        else:
            resource = globals.importResource(ajustedResourceName, resourceModuleName=ajustedResourceModuleName, required=True)
        if ObjectHelper.isEmpty(resource):
            resource = globals.importResource(ajustedResourceName, resourceModuleName=ajustedResourceModuleName, required=True)
            if ObjectHelper.isNone(resource):
                raise Exception(f'Error while importing "{ajustedResourceName}" resource from "{ajustedResourceModuleName}" module. Resource not found')
            resourceList.append(resource)
        elif ObjectHelper.isList(resource):
            resourceList += resource
        else:
            resourceList.append(resource)
    return resourceList


@Function
def fixInitializeKwargs(initializeKwargs):
    if ObjectHelper.isNotEmpty(initializeKwargs):
        for key in [
            'static_url_path',
            'static_folder',
            'template_folder'
        ]:
            if key in initializeKwargs:
                initializeKwargs.remove(key)


@Function
def getBaseUrl(globalsInstance):
    return globalsInstance.getSetting(ConfigurationKeyConstant.API_SERVER_BASE_URL)


@Function
def getStaticBaseUrl(staticPackage, givenBaseStaticUrl, globalsInstance):
    if ObjectHelper.isNotEmpty(givenBaseStaticUrl):
        return givenBaseStaticUrl
    return f'{getBaseUrl(globalsInstance)}{c.FOWARD_SLASH}{staticPackage}'


@Function
def addGlobalsTo(apiInstance, globalsInstance=None):
    FlaskUtil.validateFlaskApi(apiInstance)
    apiInstance.globals = globalsInstance if ObjectHelper.isNotNone(globalsInstance) else FlaskUtil.getGlobals()
    apiInstance.globals.api = apiInstance
    apiInstance.bindResource = FlaskManager.bindResource


@Function
def getApiUrl(app=None, api=None):
    if ObjectHelper.isNone(api):
        api = app.api
    exposedHost = StaticConverter.getValueOrDefault(api.exposedHost, api.globals.getApiSetting(ConfigurationKeyConstant.API_SERVER_EXPOSED_HOST))
    if ObjectHelper.isNotNone(exposedHost):
        return f'{exposedHost}{api.baseUrl}'
    return f'{api.documentationUrl[:-(len(api.baseUrl)+len(OpenApiManager.DOCUMENTATION_ENDPOINT))]}{api.baseUrl}'


@Function
def getApiStaticUrl(app=None, api=None, staticUrl=None):
    if ObjectHelper.isNotNone(staticUrl):
        return staticUrl
    if ObjectHelper.isNone(api):
        api = app.api
    exposedStaticHost = StaticConverter.getValueOrDefault(api.exposedStaticHost, api.globals.getApiSetting(ConfigurationKeyConstant.API_SERVER_EXPOSED_STATIC_HOST))
    if ObjectHelper.isNotNone(exposedStaticHost):
        return f'{exposedStaticHost}{api.baseStaticUrl}'
    return f'{api.documentationUrl[:-(len(api.baseUrl)+len(OpenApiManager.DOCUMENTATION_ENDPOINT))]}{api.baseStaticUrl}'


@Function
def initialize(
    rootName,
    refferenceModel,
    managerList = None,
    staticPackage = StaticConstant.KW_STATIC_FOLDER,
    viewPackage = StaticConstant.KW_VIEW_FOLDER,
    staticUrl = None,
    **kwargs
):
    fixInitializeKwargs(kwargs)
    if ObjectHelper.isNone(managerList):
        managerList = []

    globalsInstance = FlaskUtil.getGlobals()

    baseStaticUrl = getStaticBaseUrl(staticPackage, staticUrl, globalsInstance)

    app = Flask(
        rootName,
        static_folder = staticPackage,
        template_folder = viewPackage,
        static_url_path = baseStaticUrl,
        **kwargs
    )
    api = Api(app)

    ###- app.config['TEMPLATES_AUTO_RELOAD'] = True

    api.app = app
    api.app.api = api
    api.managerList = [
        DefaultExceptionManager,
        SecurityManager,
        ApiKeyManager,
        SessionManager,
        SchedulerManager,
        *managerList
    ]

    try:
        addGlobalsTo(api, globalsInstance=globalsInstance)

        api.scheme = globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SERVER_SCHEME)
        api.host = globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SERVER_HOST)
        api.port = globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SERVER_PORT)
        api.baseUrl = getBaseUrl(globalsInstance)
        api.baseStaticUrl = baseStaticUrl
        api.internalUrl = FlaskManager.getInternalUrl(api)
        api.exposedHost = globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SERVER_EXPOSED_HOST)
        api.exposedStaticHost = globalsInstance.getApiSetting(ConfigurationKeyConstant.API_SERVER_EXPOSED_STATIC_HOST)

        api.cors = CORS(app, resources={f"{api.baseUrl}/{c.ASTERISK}": {'origins': c.ASTERISK}}, supports_credentials=True)
        api.cors.api = api

        addResourceList(api)

        OpenApiManager.newDocumentation(api, app)
        SqlAlchemyProxy.addResource(api, app, baseModel=refferenceModel, echo=False)
        addManagerListTo(api, api.managerList)

        addFlaskApiResources(*[api, app, *[getResourceList(api, resourceType) for resourceType in FlaskManager.KW_RESOURCE_LIST]])

        for manager in api.managerList[::-1]:
            manager.onHttpRequestCompletion(api, app)
        SqlAlchemyProxy.onHttpRequestCompletion(api, app)

        api.documentationUrl = OpenApiManager.getDocumentationUrl(api)
        api.healthCheckUrl = f'{api.documentationUrl[:-len(OpenApiManager.DOCUMENTATION_ENDPOINT)]}{HealthCheckConstant.URI}'
        api.exposedUrl = getApiUrl(api=api)
        api.exposedStaticUrl = getApiStaticUrl(api=api, staticUrl=staticUrl)
    except Exception as exception:
        log.debug(initialize, 'Error while adding api resources. Initiating shutdown', exception=exception, muteStackTrace=True)
        for manager in api.managerList[::-1]:
            try:
                manager.onShutdown(api, api.app)
            except Exception as onShutdownException:
                log.log(initialize, f'Error while handling onShutdown call', exception=onShutdownException)
        SqlAlchemyProxy.onShutdown(api, api.app)
        raise exception

    return app


@Function
def addManagerListTo(apiInstance, managerList):
    for manager in managerList:
        manager.addResource(apiInstance, apiInstance.app)


@Function
def addControllerListTo(apiInstance, controllerList):
    for controller in controllerList:
        OpenApiManager.addControllerDocumentation(controller, apiInstance)
        mainUrl = f'{apiInstance.baseUrl}{controller.url}'
        urlList = []
        controllerInfoList = [f'Controller: {mainUrl}']
        controllerMethodList = ReflectionHelper.getAttributePointerList(controller)
        for controllerMethod in controllerMethodList:
            if ReflectionHelper.hasAttributeOrMethod(controllerMethod, FlaskManager.KW_URL) and ObjectHelper.isNotEmpty(controllerMethod.url):
                controllerUrl = f'{mainUrl}{controllerMethod.url}'
                if controllerUrl.endswith(c.SLASH):
                    controllerUrl = controllerUrl[:-1]
                if f'{apiInstance.baseUrl}' == controllerUrl or f'{apiInstance.baseUrl}{c.SLASH}' == controllerUrl:
                    raise Exception(f'Invalid controller url: {controllerUrl}')
                if controllerUrl not in urlList:
                    urlList.append(controllerUrl)
                controllerInfo = f'{c.TAB}{ReflectionHelper.getName(controllerMethod)}: {controllerUrl}'
                if controllerInfo not in controllerInfoList:
                    controllerInfoList.append(controllerInfo)
                # subUrlList = controllerMethod.url.split(c.SLASH)
                # concatenatedSubUrl = c.NOTHING
                # for subUrl in subUrlList:
                #     if subUrl:
                #         concatenatedSubUrl += f'{c.SLASH}{subUrl}'
                #         if c.LESSER == subUrl[0] and c.BIGGER == subUrl[-1]:
                #             newUrl = f'{apiInstance.baseUrl}{controller.url}{concatenatedSubUrl}'
                #             if not newUrl in urlList:
                #                 urlList.append(newUrl)
                OpenApiManager.addEndPointDocumentation(controllerUrl, controllerMethod, controller, apiInstance)
        log.debug(addControllerListTo, f'{controller.url} -> {StringHelper.prettyPython(controllerInfoList)}')
        apiInstance.add_resource(controller, *urlList)


@Function
def addServiceListTo(apiInstance, serviceList):
    for service in serviceList:
        apiInstance.bindResource(apiInstance, service())


@Function
def addSchedulerListTo(apiInstance, schedulerList):
    for scheduler in schedulerList:
        apiInstance.bindResource(apiInstance,scheduler())


@Function
def addClientListTo(apiInstance, clientList):
    for client in clientList:
        apiInstance.bindResource(apiInstance, client())


@Function
def addListenerTo(apiInstance, listenerList):
    for listener in listenerList:
        apiInstance.bindResource(apiInstance, listener())


@Function
def addEmitterTo(apiInstance, emitterList):
    for emitter in emitterList:
        apiInstance.bindResource(apiInstance, emitter())


@Function
def addRepositoryTo(apiInstance, repositoryList):
    for repository in repositoryList:
        apiInstance.bindResource(apiInstance, repository())


@Function
def addValidatorListTo(apiInstance, validatorList):
    for validator in validatorList:
        apiInstance.bindResource(apiInstance, validator())


def addMapperListTo(apiInstance, mapperList):
    for mapper in mapperList:
        apiInstance.bindResource(apiInstance, mapper())


@Function
def addHelperListTo(apiInstance, helperList):
    for helper in helperList:
        apiInstance.bindResource(apiInstance, helper())


@Function
def addConverterListTo(apiInstance, converterList):
    for converter in converterList:
        apiInstance.bindResource(apiInstance, converter())


class FlaskResource:
    ...


@Function
def addResource(instance, resourceName, resourceInstance):
    camelCaseResourceName = StringHelper.toCamelCase(resourceName) ###- f'{resourceName[0].lower()}{resourceName[1:]}'
    if not ReflectionHelper.hasAttributeOrMethod(instance, camelCaseResourceName):
        ReflectionHelper.setAttributeOrMethod(instance, camelCaseResourceName, resourceInstance)


@Function
def addResourceList(apiInstance):
    ReflectionHelper.setAttributeOrMethod(apiInstance, FlaskManager.KW_RESOURCE, FlaskResource())
    for resourceName in [FlaskManager.KW_MANAGER, *FlaskManager.KW_RESOURCE_LIST]:
        addResource(apiInstance.resource, resourceName, FlaskResource())


@Function
def addFlaskApiResources(
        apiInstance,
        appInstance,
        controllerList,
        schedulerList,
        serviceList,
        clientList,
        listenerList,
        emitterList,
        repositoryList,
        validatorList,
        mapperList,
        helperList,
        converterList,
        *args
    ):
    addRepositoryTo(apiInstance, repositoryList)
    addSchedulerListTo(apiInstance, schedulerList)
    addClientListTo(apiInstance, clientList)
    addListenerTo(apiInstance, listenerList)
    addEmitterTo(apiInstance, emitterList)
    addServiceListTo(apiInstance, serviceList)
    addControllerListTo(apiInstance, controllerList)
    addValidatorListTo(apiInstance, validatorList)
    addMapperListTo(apiInstance, mapperList)
    addHelperListTo(apiInstance, helperList)
    addConverterListTo(apiInstance, converterList)
    SqlAlchemyProxy.initialize(apiInstance, appInstance)
    # SchedulerManager.initialize(apiInstance, appInstance)
    # SecurityManager.initialize(apiInstance, appInstance)
    # ApiKeyManager.initialize(apiInstance, appInstance)
    # SessionManager.initialize(apiInstance, appInstance)
    for manager in apiInstance.managerList:
        manager.initialize(apiInstance, appInstance)
    OpenApiManager.addSwagger(apiInstance, appInstance)
