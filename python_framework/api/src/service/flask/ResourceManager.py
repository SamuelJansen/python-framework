from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from python_helper import Constant as c
from python_helper import log, Function, ReflectionHelper, ObjectHelper, StringHelper, SettingHelper
import globals
from python_framework.api.src.util import Serializer
from python_framework.api.src.util import FlaskUtil
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service import SqlAlchemyProxy
from python_framework.api.src.service import SessionManager
from python_framework.api.src.service import ApiKeyManager
from python_framework.api.src.service import SecurityManager
from python_framework.api.src.service import SchedulerManager
from python_framework.api.src.service.openapi import OpenApiManager
from python_framework.api.src.constant import ConfigurationKeyConstant


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
def isResourceType(resourceFileName,resourceType):
    splitedResourceFileName = resourceFileName.split(resourceType)
    return len(splitedResourceFileName)>1 and splitedResourceFileName[1] == DOT_PY

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
    controllerNameList = [controllerName]
    controllerNameList.append(f'{controllerName[:-len(FlaskManager.KW_CONTROLLER_RESOURCE)]}{Serializer.KW_BATCH}{FlaskManager.KW_CONTROLLER_RESOURCE}')
    # controllerNameList = [name for name in dir(__import__(controllerName)) if not name.startswith(c.UNDERSCORE)]
    # return ReflectionHelper.getAttributeOrMethodNameList(__import__(controllerName))
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
            raise Exception(f'Error while importing {ajustedResourceName} resource from {ajustedResourceModuleName} module. Resource not found.')
        elif ObjectHelper.isList(resource):
            resourceList += resource
        else:
            resourceList.append(resource)
    return resourceList


def getStaticBaseUrl(globalsInstance):
    if SettingHelper.activeEnvironmentIsLocal():
        return c.BLANK
    return globalsInstance.getSetting(ConfigurationKeyConstant.API_SERVER_BASE_URL)


@Function
def addGlobalsTo(apiInstance, globalsInstance=None):
    FlaskUtil.validateFlaskApi(apiInstance)
    apiInstance.globals = globalsInstance if ObjectHelper.isNotNone(globalsInstance) else FlaskUtil.getGlobals()
    apiInstance.globals.api = apiInstance
    apiInstance.bindResource = FlaskManager.bindResource
    apiInstance.scheme = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SERVER_SCHEME)
    apiInstance.host = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SERVER_HOST)
    apiInstance.port = apiInstance.globals.getApiSetting(ConfigurationKeyConstant.API_SERVER_PORT)
    apiInstance.baseUrl = getStaticBaseUrl(apiInstance.globals)


@Function
def initialize(
    rootName,
    refferenceModel,
    managerList = None,
    staticPackage = 'static',
    viewsPackage = 'views',
    staticUrl = str(c.BLANK)
    **kwargs
):

    if ObjectHelper.isNone(managerList):
        managerList = []

    globalsInstance = FlaskUtil.getGlobals()

    app = Flask(
        rootName,
        static_folder = staticPackage,
        template_folder = viewsPackage,
        static_url_path = staticUrl if StringHelper.isNotEmpty(staticUrl) else getStaticBaseUrl(globalsInstance)
        **kwargs
    )
    api = Api(app)
    api.app = app
    api.app.api = api
    api.managerList = managerList

    addGlobalsTo(api, globalsInstance=globalsInstance)
    api.cors = CORS(app, resources={f"{api.baseUrl}/{c.ASTERISK}": {'origins': c.ASTERISK}})
    api.cors.api = api

    OpenApiManager.newDocumentation(api, app)
    SqlAlchemyProxy.addResource(api, app, baseModel=refferenceModel, echo=False)
    SchedulerManager.addResource(api, app)
    SessionManager.addResource(api, app)
    ApiKeyManager.addResource(api, app)
    SecurityManager.addResource(api, app)
    for manager in api.managerList:
        manager.addResource(api, app)
    addFlaskApiResources(*[api, app, *[getResourceList(api, resourceType) for resourceType in FlaskManager.KW_RESOURCE_LIST]])
    for manager in api.managerList:
        manager.onHttpRequestCompletion(api, app)
    SessionManager.onHttpRequestCompletion(api, app)
    ApiKeyManager.onHttpRequestCompletion(api, app)
    SecurityManager.onHttpRequestCompletion(api, app)
    SchedulerManager.onHttpRequestCompletion(api, app)
    SqlAlchemyProxy.onHttpRequestCompletion(api, app)
    return app

@Function
def addControllerListTo(apiInstance, controllerList):
    for controller in controllerList:
        OpenApiManager.addControllerDocumentation(controller, apiInstance)
        mainUrl = f'{apiInstance.baseUrl}{controller.url}'
        urlList = [mainUrl]
        infoList = [f'Controller: {mainUrl}']
        controllerMethodList = ReflectionHelper.getAttributePointerList(controller)
        for controllerMethod in controllerMethodList:
            if ReflectionHelper.hasAttributeOrMethod(controllerMethod, FlaskManager.KW_URL) and ObjectHelper.isNotEmpty(controllerMethod.url):
                controllerUrl = f'{mainUrl}{controllerMethod.url}'
                if controllerUrl not in urlList:
                    urlList.append(controllerUrl)
                    infoList.append(f'{c.TAB}{ReflectionHelper.getName(controllerMethod)}: {controllerUrl}')
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
        log.debug(addControllerListTo, f'{controller.url} -> {StringHelper.prettyPython(infoList)}')
        apiInstance.add_resource(controller, *urlList)


@Function
def addServiceListTo(apiInstance,serviceList):
    for service in serviceList:
        apiInstance.bindResource(apiInstance,service())


@Function
def addSchedulerListTo(apiInstance,schedulerList):
    for scheduler in schedulerList:
        apiInstance.bindResource(apiInstance,scheduler())


@Function
def addClientListTo(apiInstance,clientList):
    for client in clientList:
        apiInstance.bindResource(apiInstance,client())


@Function
def addListenerTo(apiInstance,listenerList):
    for listener in listenerList:
        apiInstance.bindResource(apiInstance,listener())


@Function
def addEmitterTo(apiInstance, emitterList):
    for emitter in emitterList:
        apiInstance.bindResource(apiInstance,emitter())


@Function
def addRepositoryTo(apiInstance, repositoryList):
    for repository in repositoryList:
        apiInstance.bindResource(apiInstance,repository())


@Function
def addValidatorListTo(apiInstance,validatorList):
    for validator in validatorList:
        apiInstance.bindResource(apiInstance,validator())


def addMapperListTo(apiInstance,mapperList):
    for mapper in mapperList:
        apiInstance.bindResource(apiInstance,mapper())


@Function
def addHelperListTo(apiInstance,helperList):
    for helper in helperList:
        apiInstance.bindResource(apiInstance,helper())


@Function
def addConverterListTo(apiInstance,converterList):
    for converter in converterList:
        apiInstance.bindResource(apiInstance,converter())


class FlaskResource:
    ...

@Function
def addResourceAttibutes(apiInstance):
    ReflectionHelper.setAttributeOrMethod(apiInstance, FlaskManager.KW_RESOURCE, FlaskResource())
    for resourceName in FlaskManager.KW_RESOURCE_LIST:
        ReflectionHelper.setAttributeOrMethod(apiInstance.resource, f'{resourceName[0].lower()}{resourceName[1:]}', FlaskResource())

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
    addResourceAttibutes(apiInstance)
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
    SchedulerManager.initialize(apiInstance, appInstance)
    SecurityManager.initialize(apiInstance, appInstance)
    ApiKeyManager.initialize(apiInstance, appInstance)
    SessionManager.initialize(apiInstance, appInstance)
    for manager in apiInstance.managerList:
        manager.initialize(apiInstance, appInstance)
    OpenApiManager.addSwagger(apiInstance, appInstance)
