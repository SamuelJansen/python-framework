import json, importlib
from python_helper import Constant as c
from python_helper import log
from python_framework.api.src.annotation.MethodWrapper import Function
from python_framework.api.src.service.SqlAlchemyProxy import DeclarativeMeta, InstrumentedList

IGNORE_REOURCE_LIST = [
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

@Function
def isList(thing) :
    return type([]) == type(thing) or type(InstrumentedList()) == type(thing)

@Function
def isDictionary(thing) :
    return type({}) == type(thing)


@Function
def importResource(resourceName, resourceModuleName=None) :
    if not resourceName in IGNORE_REOURCE_LIST :
        resource = None
        if not resourceModuleName :
            resourceModuleName = resourceName
        try :
            module = __import__(resourceModuleName)
        except :
            try :
                module = importlib.import_module(resourceModuleName)
            except :
                module = None
        if module :
            try :
                resource = getattr(module, resourceName)
            except Exception as exception :
                log.warning(importResource, f'Not possible to import {resourceName} from {resourceModuleName}. cause: {str(exception)}')
            return resource

@Function
def isSerializable(attributeValue) :
    return (isinstance(attributeValue.__class__, DeclarativeMeta) or
        (isinstance(attributeValue, list) and len(attributeValue) > 0 and isinstance(attributeValue[0].__class__, DeclarativeMeta)))

@Function
def getAttributeSet(object, fieldsToExpand, classTree, verifiedClassList) :
    attributeSet = {}
    presentClass = object.__class__.__name__
    if presentClass not in classTree :
        classTree[presentClass] = [object]
    elif classTree[presentClass].count(object) < 2 :
        classTree[presentClass].append(object)
    for attributeName in [name for name in dir(object) if not name.startswith(c.UNDERSCORE) and not name == 'metadata']:
        attributeValue = object.__getattribute__(attributeName)
        if classTree[presentClass].count(object) > 1 :
            attributeSet[attributeName] = None
            continue
        if isSerializable(attributeValue) :
            if attributeName not in fieldsToExpand :
                if EXPAND_ALL_FIELDS not in fieldsToExpand :
                    attributeSet[attributeName] = None
                    continue
        attributeSet[attributeName] = attributeValue
    return attributeSet

@Function
def getJsonifier(revisitingItself=False, fieldsToExpand=[EXPAND_ALL_FIELDS], classTree=None, verifiedClassList=None):
    visitedObjectList = []
    class SqlAlchemyJsonifier(json.JSONEncoder):
        def default(self, object):
            if isinstance(object.__class__, DeclarativeMeta) :
                if revisitingItself :
                    if object in visitedObjectList:
                        return
                    visitedObjectList.append(object)
                if object.__class__.__name__ in classTree and classTree[object.__class__.__name__].count(object) > 0 :
                    return
                return getAttributeSet(object, fieldsToExpand, classTree, verifiedClassList)
            try :
                objectEncoded = json.JSONEncoder.default(self, object)
            except Exception as exception :
                try :
                    objectEncoded = object.__dict__
                except Exception as otherException :
                    raise Exception(f'Failed to encode object. Cause {str(exception)} and {str(otherException)}')
            return objectEncoded
    return SqlAlchemyJsonifier

@Function
def jsonifyIt(object, fieldsToExpand=[EXPAND_ALL_FIELDS]) :
    jsonCompleted = json.dumps(object, cls=getJsonifier(classTree={}, verifiedClassList=[]), check_circular = False)
    return jsonCompleted.replace('}, null]','}]').replace('[null]','[]')

@Function
def instanciateItWithNoArgsConstructor(objectClass) :
    args = []
    objectInstance = None
    for ammountOfVariables in range(60) :
        try :
            objectInstance = objectClass(*args)
            break
        except :
            args.append(None)
    if not objectInstance :
        raise Exception(f'Not possible to instanciate {objectClass} class in instanciateItWithNoArgsConstructor() method')
    return objectInstance

@Function
def getAttributeNameList(objectClass) :
    object = instanciateItWithNoArgsConstructor(objectClass)
    return [
        objectAttributeName
        for objectAttributeName in dir(object)
        if (not objectAttributeName.startswith(f'{2 * c.UNDERSCORE}') and not objectAttributeName.startswith(c.UNDERSCORE))
    ]

@Function
def getClassRole(objectClass) :
    if DTO_SUFIX == objectClass.__name__[-len(DTO_SUFIX):] :
        sufixList = [str(DTO_CLASS_ROLE)]
        concatenatedSufix = str(DTO_SUFIX)
        for mesoSufix in MESO_SUFIX_LIST :
            if mesoSufix == objectClass.__name__[-(len(mesoSufix)+len(concatenatedSufix)):-len(concatenatedSufix)] :
                concatenatedSufix += mesoSufix
                sufixList = [mesoSufix.upper()] + sufixList
        return c.UNDERSCORE.join(sufixList)
    return MODEL_CLASS_ROLE

def getDtoClassFromFatherClassAndChildMethodName(fatherClass, childAttributeName):
    classRole = getClassRole(fatherClass)
    dtoClassName = getResourceName(childAttributeName, classRole)
    dtoModuleName  = getResourceModuleName(childAttributeName, classRole)
    return importResource(dtoClassName, resourceModuleName=dtoModuleName)

@Function
def getListRemovedFromKey(key) :
    return key.replace(LIST_SUFIX, c.NOTHING)

@Function
def getResourceName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        sufixResourceNameList = classRole.lower().split(c.UNDERSCORE)
        for sufix in sufixResourceNameList :
            if sufix :
                resourceName += f'{sufix[0].upper()}{sufix[1:]}'
    return resourceName

@Function
def getResourceModuleName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceModuleName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        resourceModuleName += DTO_SUFIX
    return resourceModuleName

@Function
def resolveValue(value, key, classRole) :
    if isList(value) :
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

@Function
def serializeIt(fromJson, toObjectClass) :
    attributeNameList = getAttributeNameList(toObjectClass)
    classRole = getClassRole(toObjectClass)
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
            toObjectClass(*args,**kwargs)
        except :
            newValue = kwargs.copy()[key]
            args.append(newValue)
            del kwargs[key]
        # print(f'args = {args}, kwargs = {kwargs}')
    objectInstance = toObjectClass(*args,**kwargs)
    if not objectInstance and not 0 == objectInstance :
        raise Exception(f'Not possible to instanciate {toObjectClass.__name__} class in convertFromJsonToObject() method')
    return objectInstance

@Function
def convertFromJsonToObject(fromJson, toObjectClass) :
    if isList(toObjectClass) :
        objectArgs = []
        for innerToObjectClass in toObjectClass :
            if isList(innerToObjectClass) :
                objectList = []
                for fromJsonElement in fromJson :
                    objectList.append(convertFromJsonToObject(fromJsonElement, innerToObjectClass[0]))
                objectArgs.append(objectList)
            else :
                objectArgs.append(convertFromJsonToObject(fromJson, innerToObjectClass))
        return objectArgs
    else :
        return serializeIt(fromJson, toObjectClass)

@Function
def convertFromObjectToObject(fromObject, toObjectClass) :
    fromJson = json.loads(jsonifyIt(fromObject))
    return convertFromJsonToObject(fromJson,toObjectClass)
