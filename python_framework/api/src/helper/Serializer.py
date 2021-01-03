import json, importlib
from python_helper import Constant as c
from python_helper import StringHelper, ObjectHelper, log
from python_framework.api.src.annotation.MethodWrapper import Function, FunctionThrough
from python_framework.api.src.service.SqlAlchemyProxy import DeclarativeMeta, InstrumentedList

NOT_SERIALIZABLE_CLASS_NAME_LIST = [
    ObjectHelper.GENERATOR_CLASS_NAME,
    ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME
]

UTF8_ENCODE = 'utf8'

global IGNORE_REOURCE_LIST
IGNORE_REOURCE_LIST += [
    'FlaskManager',
    'MethodWrapper',
    'ResourceManager',
    'SqlAlchemyProxy'
]

EXPAND_ALL_FIELDS = 'EXPAND_ALL_FIELDS'

DTO_CLASS_ROLE = 'DTO'
MODEL_CLASS_ROLE = 'MODEL'

DTO_SUFIX = 'Dto'
LIST_SUFIX = 'List'

KW_BATCH = 'Batch'

KW_REQUEST = 'Request'
KW_RESPONSE = 'Response'

KW_POST_VERB = 'Post'
KW_PUT_VERB = 'Put'
KW_GET_VERB = 'Get'
KW_DELETE_VERB = 'Delete'

KW_CREATE_ACTION = 'Create'
KW_UPDATE_ACTION = 'Update'
KW_QUERY_ACTION = 'Query'
KW_DELETE_ACTION = 'Delete'

MESO_SUFIX_LIST = [
    KW_REQUEST,
    KW_RESPONSE,

    KW_POST_VERB,
    KW_PUT_VERB,
    KW_GET_VERB,
    KW_DELETE_VERB,

    KW_CREATE_ACTION,
    KW_UPDATE_ACTION,
    KW_QUERY_ACTION,
    KW_DELETE_ACTION
]

def isSerializerList(instance) :
    return ObjectHelper.isList(instance) or type(instance) == InstrumentedList

def isSerializerCollection(instance) :
    return ObjectHelper.isCollection(instance) or type(instance) == InstrumentedList

def requestBodyIsPresent(requestBody) :
    return ObjectHelper.isNotNone(requestBody) and (isinstance(requestBody, dict) or isinstance(requestBody, list)) :

# @Function
# def importResource(resourceName, resourceModuleName=None) :
#     if not resourceName in IGNORE_REOURCE_LIST :
#         resource = None
#         module = None
#         if not resourceModuleName :
#             resourceModuleName = resourceName
#         try :
#             module = importlib.import_module(resourceModuleName)
#         except Exception as exception:
#             log.warning(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module. Going for a second attempt')
#             try :
#                 module = __import__(resourceModuleName)
#             except :
#                 log.error(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module in the second attempt either', exception)
#         if module :
#             try :
#                 resource = getattr(module, resourceName)
#             except Exception as exception :
#                 log.warning(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module. cause: {str(exception)}')
#             return resource

@Function
def jsonifyIt(instance, fieldsToExpand=[EXPAND_ALL_FIELDS]) :
    if isJsonifyable(instance) :
        # jsonCompleted = json.dumps(instance, cls=getJsonifier(classTree={}), check_circular = False)
        # return jsonCompleted.replace('}, null]','}]').replace('[null]','[]')
        return json.dumps(getObjectAsDictionary(instance), check_circular = False)
    # log.debug(jsonifyIt, f'Not jsonifiable instance. Type: {getTypeName(instance)}')
    return instance

@Function
def serializeIt(fromJson, toClass) :
    if isNativeClassIsntance(fromJson) and toClass == fromJson.__class__ :
        return fromJson
    attributeNameList = getAttributeNameList(toClass)
    classRole = getClassRole(toClass)
    # print(f'        classRole = {classRole}')
    # print(f'        attributeNameList = {attributeNameList}')
    fromJsonToDictionary = {}
    for attributeName in attributeNameList :
        # print(f'        fromJson.get({attributeName}) = {fromJson.get(attributeName)}')
        jsonAttributeValue = fromJson.get(attributeName)
        if jsonAttributeValue or 0 == jsonAttributeValue :
            fromJsonToDictionary[attributeName] = resolveValue(jsonAttributeValue, attributeName, classRole)
        # if jsonAttributeValue :
        #     setattr(fromObject, attributeName, jsonAttributeValue)
    args = []
    kwargs = fromJsonToDictionary.copy()
    # print(f'fromJsonToDictionary = {fromJsonToDictionary}')
    for key,value in fromJsonToDictionary.items() :
        try :
            toClass(*args,**kwargs)
        except :
            newValue = kwargs.copy()[key]
            args.append(newValue)
            del kwargs[key]
        # print(f'args = {args}, kwargs = {kwargs}')
    objectInstance = toClass(*args,**kwargs)
    if not objectInstance and not 0 == objectInstance :
        raise Exception(f'Not possible to instanciate {toClass.__name__} class in convertFromJsonToObject() method')
    return objectInstance

@Function
def convertFromJsonToObject(fromJson, toClass) :
    if ObjectHelper.isDictionaryClass(toClass) and ObjectHelper.isDictionary(fromJson):
        return fromJson
    if isSerializerList(toClass) :
        objectArgs = []
        for innerToObjectClass in toClass :
            if isSerializerList(innerToObjectClass) :
                objectList = []
                for fromJsonElement in fromJson :
                    objectList.append(convertFromJsonToObject(fromJsonElement, innerToObjectClass[0]))
                objectArgs.append(objectList)
            else :
                objectArgs.append(convertFromJsonToObject(fromJson, innerToObjectClass))
        return objectArgs
    else :
        return serializeIt(fromJson, toClass)

@Function
def convertFromObjectToObject(fromObject, toClass) :
    fromJson = json.loads(jsonifyIt(fromObject))
    return convertFromJsonToObject(fromJson, toClass)

@Function
def prettify(objectAsDict) :
    if isNativeClassIsntance(objectAsDict) :
        return objectAsDict
    return StringHelper.prettyJson(objectAsDict)

@Function
def getAttributeNameList(instanceClass) :
    instance = instanciateItWithNoArgsConstructor(instanceClass)
    return [
        objectAttributeName
        for objectAttributeName in dir(instance)
        if objectAttributeName and (
            not objectAttributeName.startswith(f'{2 * c.UNDERSCORE}') and
            not objectAttributeName.startswith(c.UNDERSCORE) and
            not ObjectHelper.METADATA_NAME == objectAttributeName
        )
    ]

def getTypeName(thingInstance) :
    if not type(type) == type(thingInstance) :
        return type(thingInstance).__name__
    log.debug(getTypeName, f'Not possible to get instance type name')
    return ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME

def isJsonifyable(thing) :
    return getTypeName(thing) not in NOT_SERIALIZABLE_CLASS_NAME_LIST

def isModel(thing) :
    return (
        isinstance(thing.__class__, DeclarativeMeta) or (
            isinstance(thing, list) and len(thing) > 0 and isinstance(thing[0].__class__, DeclarativeMeta)
        )
    )

def isModelClass(thingClass) :
    return isinstance(thingClass, DeclarativeMeta)

def getObjectAsDictionary(instance, fieldsToExpand=[EXPAND_ALL_FIELDS], visitedInstances=[]) :
    if isNativeClassIsntance(instance) or isNone(instance) :
        return instance
    if instance not in visitedInstances :
        innerVisitedInstances = visitedInstances.copy()
        if ObjectHelper.isDictionary(instance) :
            for key,value in instance.items() :
                instance[key] = getObjectAsDictionary(value, visitedInstances=innerVisitedInstances)
            return instance
        elif isSerializerCollection(instance) :
            objectValueList = []
            for innerObject in instance :
                innerAttributeValue = getObjectAsDictionary(innerObject, visitedInstances=innerVisitedInstances)
                if notNone(innerAttributeValue) :
                    objectValueList.append(innerAttributeValue)
            return objectValueList
        else :
            jsonInstance = {}
            innerVisitedInstances.append(instance)
            InstrumentedList
            atributeNameList = getAttributeNameList(instance.__class__)
            for attributeName in atributeNameList :
                attributeValue = getattr(instance, attributeName)
                if isNotMethodInstance(attributeValue):
                    jsonInstance[attributeName] = getObjectAsDictionary(attributeValue, visitedInstances=innerVisitedInstances)
                else :
                    jsonInstance[attributeName] = None
            if jsonInstance :
                return jsonInstance

def instanciateItWithNoArgsConstructor(instanceClass) :
    args = []
    objectInstance = None
    for ammountOfVariables in range(60) :
        try :
            objectInstance = instanceClass(*args)
            break
        except :
            args.append(None)
    if not isinstance(objectInstance, instanceClass) :
        raise Exception(f'Not possible to instanciate {instanceClass} class in instanciateItWithNoArgsConstructor() method with None as args constructor')
    return objectInstance

def getClassRole(instanceClass) :
    if DTO_SUFIX == instanceClass.__name__[-len(DTO_SUFIX):] :
        sufixList = [str(DTO_CLASS_ROLE)]
        concatenatedSufix = str(DTO_SUFIX)
        for mesoSufix in MESO_SUFIX_LIST :
            if mesoSufix == instanceClass.__name__[-(len(mesoSufix)+len(concatenatedSufix)):-len(concatenatedSufix)] :
                concatenatedSufix += mesoSufix
                sufixList = [mesoSufix.upper()] + sufixList
        return c.UNDERSCORE.join(sufixList)
    return MODEL_CLASS_ROLE

def getDtoClassFromFatherClassAndChildMethodName(fatherClass, childAttributeName):
    classRole = getClassRole(fatherClass)
    dtoClassName = getResourceName(childAttributeName, classRole)
    dtoModuleName  = getResourceModuleName(childAttributeName, classRole)
    return importResource(dtoClassName, resourceModuleName=dtoModuleName)

def getListRemovedFromKey(key) :
    return key.replace(LIST_SUFIX, c.NOTHING)

def getResourceName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        sufixResourceNameList = classRole.lower().split(c.UNDERSCORE)
        for sufix in sufixResourceNameList :
            if sufix :
                resourceName += f'{sufix[0].upper()}{sufix[1:]}'
    return resourceName

def getResourceModuleName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceModuleName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        resourceModuleName += DTO_SUFIX
    return resourceModuleName

def resolveValue(value, key, classRole) :
    if ObjectHelper.isList(value) :
        if LIST_SUFIX == key[-4:] :
            resourceName = getResourceName(key, classRole)
            resourceModuleName = getResourceModuleName(key, classRole)
            keyClass = importResource(resourceName, resourceModuleName=resourceModuleName)
            convertedValue = []
            for jsonItem in value :
                if jsonItem :
                    convertedItem = convertFromJsonToObject(jsonItem,keyClass)
                    convertedValue.append(convertedItem)
            return convertedValue
    return value
