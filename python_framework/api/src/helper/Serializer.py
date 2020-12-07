import json, importlib
from python_helper import Constant as c
from python_helper import StringHelper, log
from python_framework.api.src.annotation.MethodWrapper import Function, FunctionThrough
from python_framework.api.src.service.SqlAlchemyProxy import DeclarativeMeta, InstrumentedList

def generatorInstance() :
    while True :
        yield False
        break

GENERATOR_CLASS_NAME = 'generator'
UNKNOWN_OBJECT_CLASS_NAME = 'unknown'

METADATA_NAME = 'metadata'

NOT_SERIALIZABLE_CLASS_NAME_LIST = [
    GENERATOR_CLASS_NAME,
    UNKNOWN_OBJECT_CLASS_NAME
]

NATIVE_CLASS_LIST = [
    int,
    str,
    float,
    bytes,
    type(generatorInstance())
]

COLLECTION_CLASS_LIST = [
    list,
    dict,
    tuple,
    set
]

UTF8_ENCODE = 'utf8'

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
def importResource(resourceName, resourceModuleName=None) :
    if not resourceName in IGNORE_REOURCE_LIST :
        resource = None
        if not resourceModuleName :
            resourceModuleName = resourceName
        try :
            module = __import__(resourceModuleName)
        except :
            log.warning(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module. Going for a second attempt')
            try :
                module = importlib.import_module(resourceModuleName)
            except Exception as exception:
                module = None
                log.error(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module in the second attempt either', exception)
        if module :
            try :
                resource = getattr(module, resourceName)
            except Exception as exception :
                log.warning(importResource, f'Not possible to import "{resourceName}" resource from "{resourceModuleName}" module. cause: {str(exception)}')
            return resource

@FunctionThrough
def isList(thing) :
    return type([]) == type(thing) or type(InstrumentedList()) == type(thing)

@FunctionThrough
def isDictionary(thing) :
    return isDictionaryClass(type(thing))

@FunctionThrough
def isDictionaryClass(thingClass) :
    return type({}) == thingClass

@FunctionThrough
def isNone(object) :
    not notNone(object)

@FunctionThrough
def notNone(object) :
    return object or isDictionary(object) or isList(object)

@FunctionThrough
def isNativeClassIsntance(object) :
    return object.__class__ in NATIVE_CLASS_LIST

@FunctionThrough
def isNotNativeClassIsntance(object) :
    return not isNativeClassIsntance(object)

@FunctionThrough
def isNotMethodInstance(object) :
    return object.__class__.__name__ not in [
        'method',
        'builtin_function_or_method'
    ]

@FunctionThrough
def isCollection(object) :
    return object.__class__ in COLLECTION_CLASS_LIST

@FunctionThrough
def getTypeName(thingInstance) :
    if not type(type) == type(thingInstance) :
        return type(thingInstance).__name__
    log.debug(getTypeName, f'Not possible to get object type name')
    return UNKNOWN_OBJECT_CLASS_NAME

@FunctionThrough
def isJsonifyable(thing) :
    return getTypeName(thing) not in NOT_SERIALIZABLE_CLASS_NAME_LIST

@FunctionThrough
def isModel(thing) :
    return (
        isinstance(thing.__class__, DeclarativeMeta) or (
            isinstance(thing, list) and len(thing) > 0 and isinstance(thing[0].__class__, DeclarativeMeta)
        )
    )

@FunctionThrough
def isModelClass(thingClass) :
    return isinstance(thingClass, DeclarativeMeta)

# @FunctionThrough
# def getAttributeSet(object, fieldsToExpand, classTree) :
#     attributeSet = {}
#     presentClass = object.__class__.__name__
#     if presentClass not in classTree :
#         classTree[presentClass] = [object]
#     elif classTree[presentClass].count(object) < 2 :
#         classTree[presentClass].append(object)
#     for attributeName in [name for name in dir(object) if not name.startswith(c.UNDERSCORE) and not name == METADATA_NAME]:
#         attributeValue = object.__getattribute__(attributeName)
#         if classTree[presentClass].count(object) > 1 :
#             attributeSet[attributeName] = None
#             continue
#         if isModel(attributeValue) :
#             if attributeName not in fieldsToExpand :
#                 if EXPAND_ALL_FIELDS not in fieldsToExpand :
#                     attributeSet[attributeName] = None
#                     continue
#         attributeSet[attributeName] = attributeValue
#     return attributeSet

# @FunctionThrough
# def getJsonifier(revisitingItself=False, fieldsToExpand=[EXPAND_ALL_FIELDS], classTree=None):
#     class SqlAlchemyJsonifier(json.JSONEncoder):
#         def default(self, object):
#             if isinstance(object.__class__, DeclarativeMeta) :
#                 # if revisitingItself :
#                 #     if object in verifiedInstanceList:
#                 #         return
#                 #     verifiedInstanceList.append(object)
#                 if object.__class__.__name__ in classTree and classTree[object.__class__.__name__].count(object) > 0 :
#                     return
#                 return getAttributeSet(object, fieldsToExpand, classTree)
#             try :
#                 objectEncoded = json.JSONEncoder.default(self, object)
#             except Exception as exception :
#                 try :
#                     objectEncoded = object.__dict__
#                 except Exception as otherException :
#                     raise Exception(f'Failed to encode object. Cause {str(exception)} and {str(otherException)}')
#             return objectEncoded
#     return SqlAlchemyJsonifier

@FunctionThrough
def getObjectAsDictionary(object, fieldsToExpand=[EXPAND_ALL_FIELDS], visitedInstances=[]) :
    if isNativeClassIsntance(object) or isNone(object) :
        return object
    if object not in visitedInstances :
        innerVisitedInstances = visitedInstances.copy()
        if isDictionary(object) :
            for key,value in object.items() :
                object[key] = getObjectAsDictionary(value, visitedInstances=innerVisitedInstances)
            return object
        elif isList(object) or type(tuple()) == type(object) or type(set()) == type(object) :
            objectValueList = []
            for innerObject in object :
                innerAttributeValue = getObjectAsDictionary(innerObject, visitedInstances=innerVisitedInstances)
                if notNone(innerAttributeValue) :
                    objectValueList.append(innerAttributeValue)
            return objectValueList
        else :
            jsonInstance = {}
            innerVisitedInstances.append(object)
            InstrumentedList
            atributeNameList = getAttributeNameList(object.__class__)
            for attributeName in atributeNameList :
                attributeValue = getattr(object, attributeName)
                if isNotMethodInstance(attributeValue):
                    jsonInstance[attributeName] = getObjectAsDictionary(attributeValue, visitedInstances=innerVisitedInstances)
                else :
                    jsonInstance[attributeName] = None
            if jsonInstance :
                return jsonInstance

@Function
def jsonifyIt(object, fieldsToExpand=[EXPAND_ALL_FIELDS]) :
    if isJsonifyable(object) :
        # jsonCompleted = json.dumps(object, cls=getJsonifier(classTree={}), check_circular = False)
        # return jsonCompleted.replace('}, null]','}]').replace('[null]','[]')
        return json.dumps(getObjectAsDictionary(object), check_circular = False)
    # log.debug(jsonifyIt, f'Not jsonifiable object. Type: {getTypeName(object)}')
    return object

@FunctionThrough
def instanciateItWithNoArgsConstructor(objectClass) :
    args = []
    objectInstance = None
    for ammountOfVariables in range(60) :
        try :
            objectInstance = objectClass(*args)
            break
        except :
            args.append(None)
    if not isinstance(objectInstance, objectClass) :
        raise Exception(f'Not possible to instanciate {objectClass} class in instanciateItWithNoArgsConstructor() method with None as args constructor')
    return objectInstance

@Function
def getAttributeNameList(objectClass) :
    object = instanciateItWithNoArgsConstructor(objectClass)
    return [
        objectAttributeName
        for objectAttributeName in dir(object)
        if objectAttributeName and (
            not objectAttributeName.startswith(f'{2 * c.UNDERSCORE}') and
            not objectAttributeName.startswith(c.UNDERSCORE) and
            not METADATA_NAME == objectAttributeName
        )
    ]

@FunctionThrough
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

@FunctionThrough
def getDtoClassFromFatherClassAndChildMethodName(fatherClass, childAttributeName):
    classRole = getClassRole(fatherClass)
    dtoClassName = getResourceName(childAttributeName, classRole)
    dtoModuleName  = getResourceModuleName(childAttributeName, classRole)
    return importResource(dtoClassName, resourceModuleName=dtoModuleName)

@FunctionThrough
def getListRemovedFromKey(key) :
    return key.replace(LIST_SUFIX, c.NOTHING)

@FunctionThrough
def getResourceName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        sufixResourceNameList = classRole.lower().split(c.UNDERSCORE)
        for sufix in sufixResourceNameList :
            if sufix :
                resourceName += f'{sufix[0].upper()}{sufix[1:]}'
    return resourceName

@FunctionThrough
def getResourceModuleName(key, classRole) :
    filteredKey = getListRemovedFromKey(key)
    resourceModuleName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        resourceModuleName += DTO_SUFIX
    return resourceModuleName

@FunctionThrough
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
    if isNativeClassIsntance(fromJson) and toObjectClass == fromJson.__class__ :
        return fromJson
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
    if isDictionaryClass(toObjectClass) :
        return fromJson
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

@Function
def prettify(objectAsDict) :
    if isNativeClassIsntance(objectAsDict) :
        return objectAsDict
    return StringHelper.stringfyThisDictionary(objectAsDict)
