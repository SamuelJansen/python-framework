import json, globals
from python_helper import Constant as c
from python_helper import StringHelper, ObjectHelper, log, ReflectionHelper
from python_helper import Function
from python_framework.api.src.service.SqlAlchemyProxy import DeclarativeMeta, InstrumentedList

NOT_SERIALIZABLE_CLASS_NAME_LIST = [
    ObjectHelper.GENERATOR_CLASS_NAME,
    ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME
]

UTF8_ENCODE = 'utf8'

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
    return ObjectHelper.isNotNone(requestBody) and (ObjectHelper.isDictionary(requestBody) or ObjectHelper.isList(requestBody))

@Function
def jsonifyIt(instance, fieldsToExpand=[EXPAND_ALL_FIELDS]) :
    if isJsonifyable(instance) :
        # jsonCompleted = json.dumps(instance, cls=getJsonifier(classTree={}), check_circular = False)
        # return jsonCompleted.replace('}, null]','}]').replace('[null]','[]')
        # print(f'getObjectAsDictionary(instance): {getObjectAsDictionary(instance)}')
        return json.dumps(getObjectAsDictionary(instance), check_circular = False)
    # log.debug(jsonifyIt, f'Not jsonifiable instance. Type: {getTypeName(instance)}')
    return instance

@Function
def serializeIt(fromJson, toClass, fatherClass=None) :
    # print(f'toClass: {toClass}')
    if ObjectHelper.isDictionary(fromJson) and ObjectHelper.isDictionaryClass(toClass) :
        # objectInstance = {}
        # for key, value in fromJson.items() :
        #     innerToClass = getTargetClassFromFatherClassAndChildMethodName(fatherClass, key)
        #     objectInstance[key] = serializeIt(fromJson, innerToClass, fatherClass=fatherClass)
        # return objectInstance
        return fromJson
    # print()
    # print()
    # print(fromJson)
    # print(f'fromJson: {fromJson}')
    # print(f'toClass: {toClass}')
    if ObjectHelper.isNativeClassIsntance(fromJson) and toClass == fromJson.__class__ :
        return fromJson
    attributeNameList = getAttributeNameList(toClass)
    classRole = getClassRole(toClass)
    # print(f'        classRole = {classRole}')
    # print(f'        attributeNameList = {attributeNameList}')
    fromJsonToDictionary = {}
    for attributeName in attributeNameList :
        # print(f'        fromJson.get({attributeName}) = {fromJson.get(attributeName)}')
        jsonAttributeValue = fromJson.get(attributeName)
        if ObjectHelper.isNotNone(jsonAttributeValue) :
            # print(f'jsonAttributeValue: {jsonAttributeValue}')
            fromJsonToDictionary[attributeName] = resolveValue(jsonAttributeValue, attributeName, classRole, fatherClass=fatherClass)
            # logList = [
            #     f'jsonAttributeValue: {jsonAttributeValue}',
            #     f'attributeName: {attributeName}',
            #     f'classRole: {classRole}',
            #     f'fromJsonToDictionary: {fromJsonToDictionary}',
            #     f'toClass: {toClass}'
            # ]
            # log.prettyPython(serializeIt, 'logList', logList, logLevel=log.DEBUG)
        else :
            fromJsonToDictionary[attributeName] = jsonAttributeValue
        # if jsonAttributeValue :
        #     ReflectionHelper.setAttributeOrMethod(fromObject, attributeName, jsonAttributeValue)
    args = []
    kwargs = fromJsonToDictionary.copy()
    # print(f'fromJsonToDictionary = {fromJsonToDictionary}')
    objectInstance = None
    for key,value in fromJsonToDictionary.items() :
        # print(f'*args{args},**kwargs{kwargs}')
        try :
            objectInstance = toClass(*args,**kwargs)
            break
        except :
            args.append(value)
            del kwargs[key]
        # print(f'args = {args}, kwargs = {kwargs}')
    if ObjectHelper.isNone(objectInstance) :
        raise Exception(f'Not possible to instanciate {ReflectionHelper.getName(toClass, muteLogs=True)} class')
    # print(objectInstance)
    # print()
    # print()
    # if objectInstance is [] :
    #     print(fromJson, toClass, fatherClass)
    return objectInstance

@Function
def convertFromJsonToObject(fromJson, toClass, fatherClass=None) :
    if ObjectHelper.isNone(fatherClass) :
        fatherClass = toClass
    if isSerializerList(toClass) :
        for innerToObjectClass in toClass :
            if isSerializerList(innerToObjectClass) :
                objectList = []
                for fromJsonElement in fromJson :
                    objectList.append(convertFromJsonToObject(fromJsonElement, innerToObjectClass[0], fatherClass=fatherClass))
                # print(f'convertFromJsonToObject: {objectList}')
                return objectList
            else :
                return convertFromJsonToObject(fromJson, innerToObjectClass, fatherClass=fatherClass)
    else :
        return serializeIt(fromJson, toClass, fatherClass=fatherClass)

@Function
def convertFromObjectToObject(fromObject, toClass) :
    fromJson = json.loads(jsonifyIt(fromObject))
    # log.prettyPython(convertFromObjectToObject, 'convertFromObjectToObject', fromJson, logLevel=log.DEBUG)
    return convertFromJsonToObject(fromJson, toClass)

@Function
def prettify(objectAsDict) :
    if ObjectHelper.isNativeClassIsntance(objectAsDict) :
        return objectAsDict
    return StringHelper.prettyJson(objectAsDict)

@Function
def getAttributeNameList(instanceClass) :
    instance = ReflectionHelper.instanciateItWithNoArgsConstructor(instanceClass)
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
        return ReflectionHelper.getName(type(thingInstance))
    log.debug(getTypeName, f'Not possible to get instance type name')
    return ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME

def isJsonifyable(thing) :
    return getTypeName(thing) not in NOT_SERIALIZABLE_CLASS_NAME_LIST

def isModel(thing) :
    return (
        isModelClass(thing.__class__) or (
            isSerializerCollection(thing) and len(thing) > 0 and isModel(thing[0]) if ObjectHelper.isNotDictionary(thing) else isModel(thing.values()[0])
        )
    )

def isModelClass(thingClass) :
    return isinstance(thingClass, DeclarativeMeta)

def getObjectAsDictionary(instance, fieldsToExpand=[EXPAND_ALL_FIELDS], visitedIdInstances=None) :
    # print(instance)
    if ObjectHelper.isNone(visitedIdInstances) :
        visitedIdInstances = []
    if ObjectHelper.isNativeClassIsntance(instance) or ObjectHelper.isNone(instance) :
        return instance
    # print(f'{instance} not in {visitedIdInstances}: {instance not in visitedIdInstances}')
    isVisitedInstance = id(instance) in visitedIdInstances
    innerVisitedIdInstances = [*visitedIdInstances.copy()]
    if ObjectHelper.isDictionary(instance) and not isVisitedInstance :
        for key,value in instance.items() :
            instance[key] = getObjectAsDictionary(value, visitedIdInstances=innerVisitedIdInstances)
        return instance
    elif isSerializerCollection(instance) :
        objectValueList = []
        for innerObject in instance :
            innerAttributeValue = getObjectAsDictionary(innerObject, visitedIdInstances=innerVisitedIdInstances)
            if ObjectHelper.isNotNone(innerAttributeValue) :
                objectValueList.append(innerAttributeValue)
        return objectValueList
    elif not isVisitedInstance :
        jsonInstance = {}
        try :
            # print(id(instance))
            innerVisitedIdInstances.append(id(instance))
            atributeNameList = getAttributeNameList(instance.__class__)
            for attributeName in atributeNameList :
                attributeValue = getattr(instance, attributeName)
                if ReflectionHelper.isNotMethodInstance(attributeValue):
                    jsonInstance[attributeName] = getObjectAsDictionary(attributeValue, visitedIdInstances=innerVisitedIdInstances)
                else :
                    jsonInstance[attributeName] = None
        except Exception as exception :
            log.warning(getObjectAsDictionary, f'Not possible to get attribute name list from {ReflectionHelper.getName(ReflectionHelper.getClass(instance, muteLogs=True), muteLogs=True)}', exception=exception)
        if jsonInstance :
            return jsonInstance

def getClassRole(instanceClass) :
    if DTO_SUFIX == ReflectionHelper.getName(instanceClass)[-len(DTO_SUFIX):] :
        sufixList = [str(DTO_CLASS_ROLE)]
        concatenatedSufix = str(DTO_SUFIX)
        for mesoSufix in MESO_SUFIX_LIST :
            if mesoSufix == ReflectionHelper.getName(instanceClass)[-(len(mesoSufix)+len(concatenatedSufix)):-len(concatenatedSufix)] :
                concatenatedSufix += mesoSufix
                sufixList = [mesoSufix.upper()] + sufixList
        return c.UNDERSCORE.join(sufixList)
    return MODEL_CLASS_ROLE

def getTargetClassFromFatherClassAndChildMethodName(fatherClass, childAttributeName):
    classRole = getClassRole(fatherClass)
    dtoClassName = getResourceName(childAttributeName, classRole)
    dtoModuleName  = getResourceModuleName(childAttributeName, classRole)
    return globals.importResource(dtoClassName, resourceModuleName=dtoModuleName)

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

def resolveValue(value, key, classRole, fatherClass=None) :
    if ObjectHelper.isNativeClassIsntance(value) :
        return value
    if ObjectHelper.isList(value) :
        if LIST_SUFIX == key[-4:] :
            resourceName = getResourceName(key, classRole)
            resourceModuleName = getResourceModuleName(key, classRole)
            keyClass = globals.importResource(resourceName, resourceModuleName=resourceModuleName)
            convertedValue = []
            for jsonItem in value :
                if jsonItem :
                    convertedItem = convertFromJsonToObject(jsonItem, keyClass, fatherClass=fatherClass)
                    convertedValue.append(convertedItem)
            return convertedValue
    resourceName = getResourceName(key, classRole)
    resourceModuleName = getResourceModuleName(key, classRole)
    keyClass = globals.importResource(resourceName, resourceModuleName=resourceModuleName)
    if ObjectHelper.isNone(keyClass) :
        return value
    else :
        return convertFromJsonToObject(value, keyClass, fatherClass=fatherClass)
