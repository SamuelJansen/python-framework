from flask import Flask
from flask_restful import Api
from python_helper import Constant as c, log
from python_framework.api.src.annotation.MethodWrapper import Function
from python_framework.api.src.helper import Serializer
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.service import SqlAlchemyProxy
from python_framework.api.src.service import Security
from python_framework.api.src.service.openapi import OpenApiManager

DOT_PY = '.py'

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
    # return Serializer.getAttributeNameList(__import__(controllerName))
    return controllerNameList

@Function
def getControllerList(resourceName):
    controllerNameList = getControllerNameList(resourceName)
    importedControllerList = []
    for controllerName in controllerNameList :
        resource = Serializer.importResource(controllerName, resourceModuleName=resourceName)
        if resource :
            importedControllerList.append(resource)
    return importedControllerList

@Function
def getResourceList(apiInstance, resourceType) :
    resourceNameList = getResourceNameList(
        apiInstance.globals.apiTree[apiInstance.globals.apiPackage],
        resourceType
    )
    resourceList = []
    for resourceName in resourceNameList :
        if FlaskManager.KW_CONTROLLER_RESOURCE == resourceName[-len(FlaskManager.KW_CONTROLLER_RESOURCE):] :
            resourceList += getControllerList(resourceName)
        else :
            resource = Serializer.importResource(resourceName)
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
        baseUrl = c.NOTHING,
        databaseEnvironmentVariable  = None,
        localStorageName = None,
        jwtSecret = None
    ) :

        # # bluePrint = Blueprint('feature-manager', __name__, url_prefix='/api/')
        # # api = Api(version='1.0', title='Feature dataset manager', description='A feature manager api')
        # # ns = api.namespace('test', description='Just a test')
        # # app = Flask(rootName)
        # # app.register_blueprint(api)
        #
        # from werkzeug.contrib.fixers import ProxyFix
        # app = Flask(rootName)
        # # app.wsgi_app = ProxyFix(app.wsgi_app)
        # api = Api(app, version='1.0', title='Feature dataset manager', description='A feature manager api')
        # # ns = api.namespace('test', description='Just a test')
        #
        # # from flask import Blueprint
        # # from flask_restplus import Namespace
        # #
        # # blueprint = Blueprint('api', rootName, url_prefix='/api')
        # # api = Api(blueprint)
        # # global_namespace = Namespace('global', path='/global')
        # # api.add_namespace(global_namespace)
        # # app = Flask(__name__)
        # # app.register_blueprint(blueprint, url_prefix='')
        app = Flask(rootName)
        api = Api(app)
        jwt = Security.getJwtMannager(app, jwtSecret)

        addGlobalsTo(api)
        args = [api, app, baseUrl, jwt]
        for resourceType in FlaskManager.KW_RESOURCE_LIST :
            args.append(getResourceList(api,resourceType))
        args.append(refferenceModel)
        kwargs = {
            'databaseEnvironmentVariable' : databaseEnvironmentVariable,
            'localStorageName' : localStorageName
        }
        addFlaskApiResources(*args, **kwargs)

        return api, app, jwt

@Function
def addControllerListTo(apiInstance, controllerList) :
    for controller in controllerList :
        OpenApiManager.addControllerDocumentation(controller, apiInstance)
        mainUrl = f'{apiInstance.baseUrl}{controller.url}'
        urlList = [mainUrl]
        controllerMethodList = FlaskManager.getAttributePointerList(controller)
        for controllerMethod in controllerMethodList :
            if hasattr(controllerMethod, FlaskManager.KW_URL) and controllerMethod.url :
                controllerUrl = f'{mainUrl}{controllerMethod.url}'
                if controllerUrl not in urlList :
                    urlList.append(controllerUrl)
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
        log.debug(addControllerListTo, f'{controller.url} -> {urlList}')
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
def addRepositoryTo(apiInstance, repositoryList, model, databaseEnvironmentVariable=None, localStorageName=None) :
    apiInstance.repository = SqlAlchemyProxy.SqlAlchemyProxy(
        databaseEnvironmentVariable = databaseEnvironmentVariable,
        localName = localStorageName,
        model = model,
        globals = apiInstance.globals,
        echo = False,
        checkSameThread = False
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
    setattr(apiInstance, FlaskManager.KW_RESOURCE, FlaskResource())
    for resourceName in FlaskManager.KW_RESOURCE_LIST :
        setattr(apiInstance.resource, resourceName.lower(), FlaskResource())

@Function
def addFlaskApiResources(
        apiInstance,
        appInstance,
        baseUrl,
        jwtInstance,
        controllerList,
        serviceList,
        clientList,
        repositoryList,
        validatorList,
        mapperList,
        helperList,
        converterList,
        model,
        databaseEnvironmentVariable = None,
        localStorageName = None
    ) :
    apiInstance.host = apiInstance.globals.getApiSetting('api.host')
    apiInstance.baseUrl = baseUrl
    OpenApiManager.newDocumentation(apiInstance, appInstance)
    addResourceAttibutes(apiInstance)
    addRepositoryTo(apiInstance, repositoryList, model, databaseEnvironmentVariable=databaseEnvironmentVariable, localStorageName=localStorageName)
    addServiceListTo(apiInstance, serviceList)
    addClientListTo(apiInstance, clientList)
    addControllerListTo(apiInstance, controllerList)
    addValidatorListTo(apiInstance, validatorList)
    addMapperListTo(apiInstance, mapperList)
    addHelperListTo(apiInstance, helperList)
    addConverterListTo(apiInstance, converterList)
    Security.addJwt(jwtInstance)
    OpenApiManager.addSwagger(apiInstance, appInstance)
