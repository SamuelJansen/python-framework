import json, globals
from uuid import uuid4, UUID
from python_helper import Constant as c
from python_helper import StringHelper, ObjectHelper, log, ReflectionHelper
from python_helper import Function
from python_framework.api.src.service.SqlAlchemyProxy import DeclarativeMeta, InstrumentedList
from python_framework.api.src.annotation import EnumAnnotation

NOT_SERIALIZABLE_CLASS_NAME_LIST = [
    ObjectHelper.GENERATOR_CLASS_NAME,
    ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME
]


SQL_ALCHEMY_RESGITRY_PUBLIC_REFLECTED_ATTRIBUTE_PRETTY_MUCH_THE_WORST_CODE_I_SAW_IN_MY_LIFE = 'registry'


UTF8_ENCODE = 'utf8'

EXPAND_ALL_FIELDS = 'EXPAND_ALL_FIELDS'

DTO_CLASS_ROLE = 'DTO'
MODEL_CLASS_ROLE = 'MODEL'
EXCPLICIT_MODEL_CLASS_ROLE = 'EXPLICITMODEL'

MODEL_SUFIX = 'Model'
DTO_SUFIX = 'Dto'
LIST_SUFIX = 'List'

KW_REQUEST = 'Request'
KW_RESPONSE = 'Response'

KW_POST_VERB = 'Post'
KW_PUT_VERB = 'Put'
KW_GET_VERB = 'Get'
KW_DELETE_VERB = 'Delete'

KW_CREATE_ACTION = 'Create'
KW_UPDATE_ACTION = 'Update'
KW_DELETE_ACTION = 'Delete'
KW_QUERY_ACTION = 'Query'
KW_PARAM_ACTION = 'Param'
KW_HEADER_ACTION = 'Header'
KW_ALL_ACTION = 'All'


MESO_SUFIX_LIST = [
    KW_REQUEST,
    KW_RESPONSE,

    KW_POST_VERB,
    KW_PUT_VERB,
    KW_GET_VERB,
    KW_DELETE_VERB,

    KW_CREATE_ACTION,
    KW_UPDATE_ACTION,
    KW_DELETE_ACTION,
    KW_QUERY_ACTION,
    KW_PARAM_ACTION,
    KW_HEADER_ACTION,
    KW_ALL_ACTION
]

RESERVED_TERM_LIST = [
    MODEL_SUFIX,
    DTO_SUFIX,
    LIST_SUFIX,
    *MESO_SUFIX_LIST
]

DATE_TIME_RELATED = [
    'datetime',
    'date',
    'time',
    'timedelta'
]

SAP_NATIVE_CLASSES_NAMES_AS_STRING_LIST = [
    'Decimal',
    'Float',
    'Integer',
    'Numeric',
    'Interval'
    'String',
    'Bolean',
    'Date',
    'Time',
    'DateTime'
]

def isSerializerNativeClassInstance(instance):
    return (
        (
            ObjectHelper.isNativeClassInstance(instance)
        ) or (
            ReflectionHelper.getClassName(instance) in SAP_NATIVE_CLASSES_NAMES_AS_STRING_LIST
        ) or (
            str(type(instance)).split(c.DOT)[-1] in SAP_NATIVE_CLASSES_NAMES_AS_STRING_LIST
        )
    )


def validateJsonIsNotNone(fromJson, toClass):
    if ObjectHelper.isNone(fromJson):
        log.log(validateJsonIsNotNone, f'fromJson: {fromJson}, toClass: {toClass}')
        raise Exception('''The argument 'fromJson' cannot be none''')


def validateToClassIsNotNone(fromJson, toClass):
    if ObjectHelper.isNone(toClass):
        log.log(validateToClassIsNotNone, f'fromJson: {fromJson}, toClass: {toClass}')
        raise Exception('''The argument 'toClass' cannot be none''')


def raiseUnhandledConversion(fromJson, toClass):
    log.log(raiseUnhandledConversion, f'fromJson: {fromJson}, toClass: {toClass}')
    raise Exception(f'''Unhandled serialization between {"Json Collection" if ObjectHelper.isList(fromJson) else "Json Object"} and {toClass} ''')


def newUuid():
    return uuid4()


def newUuidAsString():
    return str(newUuid())


def isUuid(thing):
    return isinstance(thing, UUID)


def isDatetimeRelated(thing):
    return ReflectionHelper.getName(type(thing)) in DATE_TIME_RELATED


def isSerializerList(instance):
    return ObjectHelper.isList(instance) or type(instance) == InstrumentedList


def isSerializerCollection(instance):
    return ObjectHelper.isCollection(instance) or type(instance) == InstrumentedList


def isNotSerializerList(instance):
    return not isSerializerList(instance)


def requestBodyIsPresent(requestBody):
    return ObjectHelper.isNotNone(requestBody) and (ObjectHelper.isDictionary(requestBody) or ObjectHelper.isList(requestBody))


@Function
def jsonifyIt(instance, fieldsToExpand=[EXPAND_ALL_FIELDS]):
    if isJsonifyable(instance):
        # jsonCompleted = json.dumps(instance, cls=getJsonifier(classTree={}), check_circular = False)
        # return jsonCompleted.replace('}, null]','}]').replace('[null]','[]')
        # print(f'getObjectAsDictionary(instance): {getObjectAsDictionary(instance)}')
        return json.dumps(getObjectAsDictionary(instance), check_circular = False)
    # log.debug(jsonifyIt, f'Not jsonifiable instance. Type: {getTypeName(instance)}')
    return instance


@Function
def pleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy(toClass, fromJsonToDictionary, muteLogs=False):
    args = []
    kwargs = fromJsonToDictionary.copy()
    objectInstance = None
    args = []
    kwargs = fromJsonToDictionary.copy()
    if SQL_ALCHEMY_RESGITRY_PUBLIC_REFLECTED_ATTRIBUTE_PRETTY_MUCH_THE_WORST_CODE_I_SAW_IN_MY_LIFE in kwargs:
        kwargs.pop(SQL_ALCHEMY_RESGITRY_PUBLIC_REFLECTED_ATTRIBUTE_PRETTY_MUCH_THE_WORST_CODE_I_SAW_IN_MY_LIFE) ###- this particular job from SqlAlchemy was a big shity one...
    objectInstance = None
    possibleErrorSet = set()
    for key,value in fromJsonToDictionary.items():
        try :
            objectInstance = toClass(*args,**kwargs)
            break
        except Exception as exception :
            args.append(value)
            kwargs.pop(key)
            possibleErrorSet.add(str(exception))
    if not muteLogs and ObjectHelper.isNotEmpty(possibleErrorSet):
        log.log(pleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy, f'Not possible to instantiate toClass. Possible causes: {possibleErrorSet}')
    return objectInstance


@Function
def getAttributeNameList_andPleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy(instanceClass, muteLogs=False):
    attributeNameList = ReflectionHelper.getAttributeNameList(instanceClass, muteLogs=muteLogs)
    return attributeNameList if not isModelClass(instanceClass) else [attributeName for attributeName in attributeNameList if not SQL_ALCHEMY_RESGITRY_PUBLIC_REFLECTED_ATTRIBUTE_PRETTY_MUCH_THE_WORST_CODE_I_SAW_IN_MY_LIFE == attributeName]


@Function
def serializeIt(fromJson, toClass, fatherClass=None, muteLogs=False):
    if ObjectHelper.isNotDictionary(fromJson):
        if isSerializerNativeClassInstance(fromJson) and toClass == fromJson.__class__ :
            return fromJson
        if isUuid(fromJson):
            return str(fromJson)
        raiseUnhandledConversion(fromJson, toClass)
    # print(f'fromJson: {fromJson}, toClass: {toClass}, fatherClass: {fatherClass}')
    else:
        validateToClassIsNotNone(fromJson, toClass)
        validateJsonIsNotNone(fromJson, toClass)
        if ObjectHelper.isDictionaryClass(toClass):
            # objectInstance = {}
            # for key, value in fromJson.items():
            #     innerToClass = getTargetClassFromFatherClassAndChildMethodName(fatherClass, key)
            #     objectInstance[key] = serializeIt(fromJson, innerToClass, fatherClass=fatherClass)
            # return objectInstance
            return fromJson
        # print(fromJson)
        # print(f'fromJson: {fromJson}')
        # print(f'toClass: {toClass}')
        attributeNameList = getAttributeNameList_andPleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy(toClass, muteLogs=muteLogs)
        classRole = getClassRole(toClass)
        # print(f'        classRole = {classRole}')
        # print(f'        attributeNameList = {attributeNameList}')
        fromJsonToDictionary = {}
        for attributeName in attributeNameList :
            # print(f'        fromJson.get({attributeName}) = {fromJson.get(attributeName)}')
            jsonAttributeValue = fromJson.get(attributeName)
            if ObjectHelper.isNone(jsonAttributeValue):
                jsonAttributeValue = fromJson.get(f'{attributeName[0].upper()}{attributeName[1:].lower()}')
            if ObjectHelper.isNotNone(jsonAttributeValue):
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

        if isModelClass(toClass):
            objectInstance = pleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy(toClass, fromJsonToDictionary, muteLogs=muteLogs)
        else:
            args = []
            kwargs = fromJsonToDictionary.copy()
            # print(f'fromJsonToDictionary = {fromJsonToDictionary}')
            objectInstance = None
            possibleErrorSet = set()
            for key,value in fromJsonToDictionary.items():
                # print(f'*args{args},**kwargs{kwargs}')
                try :
                    objectInstance = toClass(*args,**kwargs)
                    break
                except Exception as exception :
                    # print(exception)
                    args.append(value)
                    # del kwargs[key]
                    kwargs.pop(key)
                    possibleErrorSet.add(str(exception))
            if not muteLogs and ObjectHelper.isNotEmpty(possibleErrorSet):
                log.log(serializeIt, f'Not possible to instantiate toClass. Possible causes: {possibleErrorSet}')

        if ObjectHelper.isNone(objectInstance):
            raise Exception(f'Not possible to instanciate {ReflectionHelper.getName(toClass, muteLogs=True)} class. Check LOG logs level for more information')
        # print(objectInstance)
        # if objectInstance is [] :
        #     print(fromJson, toClass, fatherClass)
        return objectInstance


@Function
def convertFromJsonToDictionary(string):
    if isinstance(string, str):
        return json.loads(string)
    return string


@Function
def convertFromJsonToObject(fromJson, toClass, fatherClass=None, muteLogs=False):
    # if isinstance(fromJson, str):
    #     return convertFromJsonToObject(
    #         convertFromJsonToDictionary(fromJson),
    #         toClass,
    #         fatherClass=fatherClass,
    #         muteLogs=muteLogs
    #     )
    if ObjectHelper.isNone(fromJson) or ObjectHelper.isNone(toClass):
        return fromJson
    # validateToClassIsNotNone(fromJson, toClass)
    # validateJsonIsNotNone(fromJson, toClass)
    if ObjectHelper.isNone(fatherClass):
        fatherClass = toClass
    # print(f'isSerializerList(toClass): {isSerializerList(toClass)}')
    if isSerializerList(toClass):
        for innerToObjectClass in toClass :
            if isSerializerList(innerToObjectClass) and ObjectHelper.isList(fromJson):
                objectList = []
                for fromJsonElement in fromJson :
                    objectList.append(convertFromJsonToObject(fromJsonElement, innerToObjectClass[0], fatherClass=fatherClass, muteLogs=muteLogs))
                # print(f'convertFromJsonToObject: {objectList}')
                return objectList
            elif not isSerializerList(innerToObjectClass) and not ObjectHelper.isList(fromJson):
                return convertFromJsonToObject(fromJson, innerToObjectClass, fatherClass=fatherClass, muteLogs=muteLogs)
    else:
        return serializeIt(fromJson, toClass, fatherClass=fatherClass, muteLogs=muteLogs)
    raiseUnhandledConversion(fromJson, toClass)


@Function
def convertFromObjectToObject(fromObject, toClass):
    ###- It used to be
    ###- fromJson = json.loads(jsonifyIt(fromObject))
    ###- return convertFromJsonToObject(fromJson, toClass)
    # return convertFromJsonToObject(json.loads(jsonifyIt(fromObject)), toClass)
    return convertFromJsonToObject(getObjectAsDictionary(fromObject), toClass)


@Function
def prettify(objectAsDict):
    if isSerializerNativeClassInstance(objectAsDict):
        return objectAsDict
    ###- someone please give a hint on SqlAlchemy developers on this fucking "registry" thing...
    return StringHelper.prettyJson(objectAsDict, ignoreKeyList=[SQL_ALCHEMY_RESGITRY_PUBLIC_REFLECTED_ATTRIBUTE_PRETTY_MUCH_THE_WORST_CODE_I_SAW_IN_MY_LIFE] if isModel(objectAsDict) else [])


def getTypeName(thingInstance):
    if not type(type) == type(thingInstance):
        return ReflectionHelper.getName(type(thingInstance))
    log.log(getTypeName, f'Not possible to get instance type name')
    return ObjectHelper.UNKNOWN_OBJECT_CLASS_NAME


def isJsonifyable(thing):
    return getTypeName(thing) not in NOT_SERIALIZABLE_CLASS_NAME_LIST


def isModel(thing):
    if ObjectHelper.isNone(thing):
        return False
    return (
        isinstance(thing, DeclarativeMeta) or isModelClass(thing.__class__) or (
            isSerializerCollection(thing) and len(thing) > 0 and isModel(thing[0]) if ObjectHelper.isNotDictionary(thing) else isModel(thing.values()[0])
        )
    )


def isModelClass(thingClass):
    return ObjectHelper.isNotNone(thingClass) and (thingClass == DeclarativeMeta or isinstance(thingClass, DeclarativeMeta))


def getObjectAsDictionary(instance, fieldsToExpand=[EXPAND_ALL_FIELDS], visitedIdInstances=None, muteLogs=False):
    # print(instance)
    if ObjectHelper.isNone(visitedIdInstances):
        visitedIdInstances = []
    if isSerializerNativeClassInstance(instance) or ObjectHelper.isNone(instance):
        return instance
    if EnumAnnotation.isEnumItem(instance):
        return instance.enumValue
    if isDatetimeRelated(instance) or isUuid(instance):
        return str(instance)
    # print(f'{instance} not in {visitedIdInstances}: {instance not in visitedIdInstances}')
    isVisitedInstance = id(instance) in visitedIdInstances
    innerVisitedIdInstances = [*visitedIdInstances.copy()]
    if ObjectHelper.isDictionary(instance) and not isVisitedInstance :
        # for key,value in instance.items():
        #     instance[key] = getObjectAsDictionary(value, visitedIdInstances=innerVisitedIdInstances, muteLogs=muteLogs)
        # return instance
        return {key: getObjectAsDictionary(value, visitedIdInstances=innerVisitedIdInstances, muteLogs=muteLogs) for key, value in instance.items() }
    elif isSerializerCollection(instance):
        objectValueList = []
        for innerObject in instance :
            innerAttributeValue = getObjectAsDictionary(innerObject, visitedIdInstances=innerVisitedIdInstances, muteLogs=muteLogs)
            if ObjectHelper.isNotNone(innerAttributeValue):
                objectValueList.append(innerAttributeValue)
        return objectValueList
    elif not isVisitedInstance :
        jsonInstance = {}
        try :
            # print(id(instance))
            innerVisitedIdInstances.append(id(instance))
            atributeNameList = getAttributeNameList_andPleaseSomeoneSlapTheFaceOfTheGuyWhoDidItInSqlAlchemy(instance.__class__, muteLogs=muteLogs)
            for attributeName in atributeNameList :
                attributeValue = getattr(instance, attributeName)
                if ReflectionHelper.isNotMethodInstance(attributeValue, muteLogs=muteLogs):
                    jsonInstance[attributeName] = getObjectAsDictionary(attributeValue, visitedIdInstances=innerVisitedIdInstances, muteLogs=muteLogs)
                else :
                    jsonInstance[attributeName] = None
        except Exception as exception :
            LOGGER = log.log if muteLogs else log.debug
            LOGGER(getObjectAsDictionary, f'Not possible to get attribute name list from {ReflectionHelper.getName(ReflectionHelper.getClass(instance, muteLogs=True), muteLogs=True)}', exception=exception)
        if ObjectHelper.isNotEmpty(jsonInstance):
            return jsonInstance
        return str(instance)


def getClassRole(instanceClass):
    instanceClassName = ReflectionHelper.getName(instanceClass)
    if instanceClassName.endswith(DTO_SUFIX):
        sufixList = [str(DTO_CLASS_ROLE)]
        concatenatedSufix = str(DTO_SUFIX)
        for mesoSufix in MESO_SUFIX_LIST :
            if mesoSufix == ReflectionHelper.getName(instanceClass)[-(len(mesoSufix)+len(concatenatedSufix)):-len(concatenatedSufix)] :
                concatenatedSufix += mesoSufix
                sufixList = [mesoSufix.upper()] + sufixList
        return c.UNDERSCORE.join(sufixList)
    elif instanceClassName.endswith(MODEL_SUFIX):
        return EXCPLICIT_MODEL_CLASS_ROLE
    return MODEL_CLASS_ROLE


def getTargetClassFromFatherClassAndChildMethodName(fatherClass, childAttributeName):
    classRole = getClassRole(fatherClass)
    className = getResourceName(childAttributeName, classRole)
    moduleName  = getResourceModuleName(childAttributeName, classRole)
    # print(f'classRole: {classRole}, className: {className}, moduleName: {moduleName}')
    return importResource(className, resourceModuleName=moduleName)


def getListRemovedFromKey(key):
    return key.replace(LIST_SUFIX, c.NOTHING)


def getResourceName(key, classRole):
    filteredKey = getListRemovedFromKey(key)
    resourceName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        sufixResourceNameList = classRole.lower().split(c.UNDERSCORE)
        for sufix in sufixResourceNameList :
            if sufix :
                resourceName += f'{sufix[0].upper()}{sufix[1:]}'
    elif EXCPLICIT_MODEL_CLASS_ROLE == classRole:
        resourceName += MODEL_SUFIX
    return resourceName


def getResourceModuleName(key, classRole):
    filteredKey = getListRemovedFromKey(key)
    resourceModuleName = f'{filteredKey[0].upper()}{filteredKey[1:]}'
    if DTO_CLASS_ROLE in classRole :
        resourceModuleName += DTO_SUFIX
    elif EXCPLICIT_MODEL_CLASS_ROLE == classRole:
        resourceModuleName += MODEL_SUFIX
    return resourceModuleName


def resolveValue(value, key, classRole, fatherClass=None):
    if isSerializerNativeClassInstance(value):
        return value
    if ObjectHelper.isList(value):
        if key.endswith(LIST_SUFIX):
            resourceName = getResourceName(key, classRole)
            resourceModuleName = getResourceModuleName(key, classRole)
            resourceClass = importResource(resourceName, resourceModuleName=resourceModuleName)
            return [
                convertFromJsonToObject(jsonItem, resourceClass, fatherClass=fatherClass) for jsonItem in value if jsonItem
            ]
        else:
            try:
                resourceName = getResourceName(key, classRole)
                resourceModuleName = getResourceModuleName(key, classRole)
                resourceClass = importResource(resourceName, resourceModuleName=resourceModuleName)
                return [
                    convertFromJsonToObject(jsonItem, resourceClass, fatherClass=fatherClass) for jsonItem in value if jsonItem
                ]
            except Exception as exception:
                log.log(resolveValue, 'Not possible to resolve list value properly. returning received value by default', exception=exception)
                return value
    else:
        resourceName = getResourceName(key, classRole)
        resourceModuleName = getResourceModuleName(key, classRole)
        resourceClass = importResource(resourceName, resourceModuleName=resourceModuleName)
        if ObjectHelper.isNone(resourceClass):
            return value
        else :
            return convertFromJsonToObject(value, resourceClass, fatherClass=fatherClass)


def getUncheckedKeyValue(key, value):
    if key.endswith(LIST_SUFIX) and ObjectHelper.isNotList(value):
        return [
            value
        ] if not isinstance(value, str) else [
            v.strip()
            for v in value.split(c.COMA)
        ]
    return value


def importResource(resourceName, resourceModuleName=None):
    # resourceClass = globals.importResource(resourceName, resourceModuleName=resourceModuleName)
    # if ObjectHelper.isNone(resourceClass):
    #     resourceClass = globals.importResource(resourceName)
    # return resourceClass
    return globals.importResource(resourceName, resourceModuleName=resourceModuleName)


#######################################################
