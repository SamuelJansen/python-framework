from flask import Flask
from flask_restful import Api
from python_helper import Constant as c
from python_helper import log, Function, ReflectionHelper, SettingHelper, ObjectHelper, StringHelper
import globals
from python_framework.api.src.helper import Serializer
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service import SqlAlchemyProxy
from python_framework.api.src.service import Security
from python_framework.api.src.service.openapi import OpenApiManager

DOT_PY = '.py'

def getPythonFrameworkResourceByType(resourceType) :
    return FlaskManager.PYTHON_FRAMEWORK_RESOURCE_NAME_DICTIONARY.get(resourceType, [])

def isNotPythonFrameworkApiInstance(apiInstance) :
    return apiInstance.globals.apiName not in FlaskManager.PYTHON_FRAMEWORK_INTERNAL_MODULE_NAME_LIST

def isFromPythonFramework(apiInstance, resourceType, resourceName) :
    return not (resourceName in getPythonFrameworkResourceByType(resourceType) and isNotPythonFrameworkApiInstance(apiInstance))

def getResourceModuleNameAjusted(apiInstance, resourceType, resourceName) :
    return resourceName if isFromPythonFramework(apiInstance, resourceType, resourceName) else FlaskManager.PYTHON_FRAMEWORK_MODULE_NAME

def getResourceNameAjusted(apiInstance, resourceType, resourceName) :
    return resourceName if isFromPythonFramework(apiInstance, resourceType, resourceName) else f'{resourceName}{c.DOT}{resourceName}'

def isControllerResourceName(resourceName) :
    return FlaskManager.KW_CONTROLLER_RESOURCE == resourceName[-len(FlaskManager.KW_CONTROLLER_RESOURCE):]

@Function
def getResourceName(resourceFileName) :
    return resourceFileName.split(DOT_PY)[0]

@Function
def isResourceType(resourceFileName,resourceType) :
    splitedResourceFileName = resourceFileName.split(resourceType)
    return len(splitedResourceFileName)>1 and splitedResourceFileName[1] == DOT_PY

@Function
def getResourceNameList(apiTree, resourceType) :
    resourceNameList = []
    if apiTree or type(apiTree).__name__ == c.DICT :
        for package,subPackageTree in apiTree.items() :
            if isResourceType(package, resourceType) :
                resourceNameList.append(getResourceName(package))
            resourceNameList += getResourceNameList(
                subPackageTree,
                resourceType
            )
    return resourceNameList

@Function
def getControllerNameList(controllerName) :
    controllerNameList = [controllerName]
    controllerNameList.append(f'{controllerName[:-len(FlaskManager.KW_CONTROLLER_RESOURCE)]}{Serializer.KW_BATCH}{FlaskManager.KW_CONTROLLER_RESOURCE}')
    # controllerNameList = [name for name in dir(__import__(controllerName)) if not name.startswith(c.UNDERSCORE)]
    # return ReflectionHelper.getAttributeOrMethodNameList(__import__(controllerName))
    return controllerNameList

@Function
def getControllerList(resourceName, resourceModuleName) :
    controllerNameList = getControllerNameList(resourceName)
    importedControllerList = []
    for controllerName in controllerNameList :
        resource = globals.importResource(controllerName, resourceModuleName=resourceModuleName)
        if resource :
            importedControllerList.append(resource)
    return importedControllerList

@Function
def getResourceList(apiInstance, resourceType) :
    resourceNameList = getResourceNameList(
        apiInstance.globals.apiTree[apiInstance.globals.apiPackage],
        resourceType
    )
    if isNotPythonFrameworkApiInstance(apiInstance) :
        resourceNameList += getPythonFrameworkResourceByType(resourceType)
    resourceList = []
    for resourceName in resourceNameList :
        ajustedResourceName = getResourceNameAjusted(apiInstance, resourceType, resourceName)
        ajustedResourceModuleName = getResourceModuleNameAjusted(apiInstance, resourceType, resourceName)
        if isControllerResourceName(resourceName) :
            resourceList += getControllerList(ajustedResourceName, ajustedResourceModuleName)
        else :
            resource = globals.importResource(ajustedResourceName, resourceModuleName=ajustedResourceModuleName)
            if resource :
                resourceList.append(resource)
    return resourceList

@Function
def addGlobalsTo(apiInstance) :
    FlaskManager.validateFlaskApi(apiInstance)
    apiInstance.globals = FlaskManager.getGlobals()
    apiInstance.globals.api = apiInstance
    apiInstance.bindResource = FlaskManager.bindResource

@Function
def initialize(
    rootName,
    refferenceModel,
) :

    app = Flask(rootName)
    api = Api(app)
    addGlobalsTo(api)
    securityKey = api.globals.getSetting('api.security.secret')
    if SettingHelper.LOCAL_ENVIRONMENT == SettingHelper.getActiveEnvironment() :
        log.setting(initialize, f'JWT secret: {securityKey}')
    jwt = Security.getJwtMannager(app, securityKey)

    args = [api, app, jwt]
    for resourceType in FlaskManager.KW_RESOURCE_LIST :
        args.append(getResourceList(api, resourceType))
    args.append(refferenceModel)
    addFlaskApiResources(*args)

    return api, app, jwt

@Function
def addControllerListTo(apiInstance, controllerList) :
    for controller in controllerList :
        OpenApiManager.addControllerDocumentation(controller, apiInstance)
        mainUrl = f'{apiInstance.baseUrl}{controller.url}'
        urlList = [mainUrl]
        infoList = [f'Controller: {mainUrl}']
        controllerMethodList = ReflectionHelper.getAttributePointerList(controller)
        for controllerMethod in controllerMethodList :
            if ReflectionHelper.hasAttributeOrMethod(controllerMethod, FlaskManager.KW_URL) and ObjectHelper.isNotEmpty(controllerMethod.url) :
                controllerUrl = f'{mainUrl}{controllerMethod.url}'
                if controllerUrl not in urlList :
                    urlList.append(controllerUrl)
                    infoList.append(f'{c.TAB}{ReflectionHelper.getName(controllerMethod)}: {controllerUrl}')
                # subUrlList = controllerMethod.url.split(c.SLASH)
                # concatenatedSubUrl = c.NOTHING
                # for subUrl in subUrlList :
                #     if subUrl :
                #         concatenatedSubUrl += f'{c.SLASH}{subUrl}'
                #         if c.LESSER == subUrl[0] and c.BIGGER == subUrl[-1] :
                #             newUrl = f'{apiInstance.baseUrl}{controller.url}{concatenatedSubUrl}'
                #             if not newUrl in urlList :
                #                 urlList.append(newUrl)
                OpenApiManager.addEndPointDocumentation(controllerUrl, controllerMethod, controller, apiInstance)
        log.debug(addControllerListTo, f'{controller.url} -> {StringHelper.prettyPython(infoList)}')
        apiInstance.add_resource(controller, *urlList)

@Function
def addServiceListTo(apiInstance,serviceList) :
    for service in serviceList :
        apiInstance.bindResource(apiInstance,service())

@Function
def addClientListTo(apiInstance,clientList) :
    for client in clientList :
        apiInstance.bindResource(apiInstance,client())

@Function
def addRepositoryTo(apiInstance, repositoryList, model) :
    apiInstance.repository = SqlAlchemyProxy.SqlAlchemyProxy(
        model,
        apiInstance.globals,
        echo = False
    )
    for repository in repositoryList :
        apiInstance.bindResource(apiInstance,repository())

@Function
def addValidatorListTo(apiInstance,validatorList) :
    for validator in validatorList :
        apiInstance.bindResource(apiInstance,validator())

def addMapperListTo(apiInstance,mapperList) :
    for mapper in mapperList :
        apiInstance.bindResource(apiInstance,mapper())

@Function
def addHelperListTo(apiInstance,helperList) :
    for helper in helperList :
        apiInstance.bindResource(apiInstance,helper())

@Function
def addConverterListTo(apiInstance,converterList) :
    for converter in converterList :
        apiInstance.bindResource(apiInstance,converter())

class FlaskResource:
    ...

@Function
def addResourceAttibutes(apiInstance) :
    ReflectionHelper.setAttributeOrMethod(apiInstance, FlaskManager.KW_RESOURCE, FlaskResource())
    for resourceName in FlaskManager.KW_RESOURCE_LIST :
        ReflectionHelper.setAttributeOrMethod(apiInstance.resource, f'{resourceName[0].lower()}{resourceName[1:]}', FlaskResource())

@Function
def addFlaskApiResources(
        apiInstance,
        appInstance,
        jwtInstance,
        controllerList,
        serviceList,
        clientList,
        repositoryList,
        validatorList,
        mapperList,
        helperList,
        converterList,
        model
    ) :
    apiInstance.scheme = apiInstance.globals.getSetting('api.server.scheme')
    apiInstance.host = apiInstance.globals.getSetting('api.server.host')
    apiInstance.port = apiInstance.globals.getSetting('api.server.port')
    apiInstance.baseUrl = apiInstance.globals.getSetting('api.server.base-url')
    OpenApiManager.newDocumentation(apiInstance, appInstance)
    addResourceAttibutes(apiInstance)
    addRepositoryTo(apiInstance, repositoryList, model)
    addServiceListTo(apiInstance, serviceList)
    addClientListTo(apiInstance, clientList)
    addControllerListTo(apiInstance, controllerList)
    addValidatorListTo(apiInstance, validatorList)
    addMapperListTo(apiInstance, mapperList)
    addHelperListTo(apiInstance, helperList)
    addConverterListTo(apiInstance, converterList)
    Security.addJwt(jwtInstance)
    OpenApiManager.addSwagger(apiInstance, appInstance)
