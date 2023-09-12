from abc import ABCMeta
from python_helper import Constant as c
from python_helper import log, ReflectionHelper, ObjectHelper, StringHelper

ENUM_VALUE_AS_STRING_KEY = 'enumValue'
ENUM_NAME_AS_STRING_KEY = 'enumName'
ENUM_AS_STRING_KEY = 'enum'

MAP_METHOD_NAME = 'map'
ENUM_STATIC_METHOD_NAME_LIST = [
    MAP_METHOD_NAME
]

def isEnumItemInstance(instance):
    return EnumItem == type(instance)

def areUnsafellyEnumItemInstance(one, theOther):
    return type(one) == type(theOther)

def areEnumItemInstance(one, theOther):
    return isEnumItemInstance(one) and areUnsafellyEnumItemInstance(one, theOther)

def mustUpdateInnerAttributeValueType(possibleEnumInnerValueType, value):
    return ObjectHelper.isNotNone(possibleEnumInnerValueType) and value not in DERIVATED_ENUM_ITEM_CLASS_SET

def updateEnumItem(enumItem, key, value):
    enumItem.__enumItemMap__[key] = value
    enumItem.__enumItemEqMap__[key] = str(value)
    setInnerAttributeValue(enumItem, key, value)

def setInnerAttributeValue(instance, attributeName, value):
    EnumInnerValueType = ENUM_ITEM_CLASS_DICTIONARY.get(type(value))
    # print(f'    -> {value=}')
    # print(f'    -> {EnumInnerValueType=}')
    if mustUpdateInnerAttributeValueType(EnumInnerValueType, value):
        ReflectionHelper.setAttributeOrMethod(instance, attributeName, EnumInnerValueType(value))
    else:
        ReflectionHelper.setAttributeOrMethod(instance, attributeName, value)
    # print(f'ReflectionHelper.getAttributeOrMethod({instance}, {attributeName}, {value}): {ReflectionHelper.getAttributeOrMethod(instance, attributeName)}')


class EnumItemStr(str):
    __name__ = 'EnumItemStr'

class EnumItemInt(int):
    __name__ = 'EnumItemInt'

class EnumItemFloat(float):
    __name__ = 'EnumItemFloat'

class EnumItemDict(dict):
    __name__ = 'EnumItemDict'

class EnumItemSet(set):
    __name__ = 'EnumItemSet'

class EnumItemTuple(tuple):
    __name__ = 'EnumItemTuple'

class EnumItemList(list):
    __name__ = 'EnumItemList'

class EnumClass(object):
    ...

class EnumItem(metaclass=ABCMeta):

    ###- __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        # print(f'__init__({self}, *{args}, **{kwargs})')
        # print(f'    type({self}): {type(self)}')
        # print(f'    !---!---> isinstance({self}, EnumItem): {isinstance(self, EnumItem)}')
        ###- if type(self) not in STRICTLY_DERIVATED_ENUM_ITEM_CLASS_SET:
        self.__enumItemMap__ = {}
        self.__enumItemEqMap__ = {}
        self.enumName = None
        for key, value in kwargs.items():
            updateEnumItem(self, key, value)

    def isInstance(self, other):
        return areUnsafellyEnumItemInstance(self, other)

    def __get__(self, obj, objtype=None):
        return self if not ReflectionHelper.hasAttributeOrMethod(self, ENUM_VALUE_AS_STRING_KEY) else self.enumValue

    def __str__(self):
        return str(ReflectionHelper.getAttributeOrMethod(self, ENUM_VALUE_AS_STRING_KEY, muteLogs=True))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.isInstance(other):
            return str(other.__enumItemEqMap__) == str(self.__enumItemEqMap__)
        return self.enumValue == other

    def __ne__(self, other):
        if self.isInstance(other):
            return str(other.__enumItemEqMap__) != str(self.__enumItemEqMap__)
        return self.enumValue != other

    def __lt__(self, other):
        if self.isInstance(other) and not self.isInstance(self.enumValue):
            return self.enumValue < other.enumValue
        return self < other

    def __gt__(self, other):
        if self.isInstance(other) and not self.isInstance(self.enumValue):
            return self.enumValue > other.enumValue

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __hash__(self):
        return hash(self.__str__())

    ###- def __instancecheck__(self, instance):
    ###-     return type(instance) in DERIVATED_ENUM_ITEM_CLASS_SET
    ###- def __subclasscheck__(self, instance):
    ###-     return type(instance) == EnumItem

EnumItem.register(EnumItemStr)
EnumItem.register(EnumItemInt)
EnumItem.register(EnumItemFloat)
EnumItem.register(EnumItemDict)
EnumItem.register(EnumItemSet)
EnumItem.register(EnumItemTuple)
EnumItem.register(EnumItemList)

ENUM_ITEM_CLASS_DICTIONARY = {
    str : EnumItemStr,
    EnumItemStr : EnumItemStr,
    int : EnumItemInt,
    EnumItemInt : EnumItemInt,
    float : EnumItemFloat,
    EnumItemFloat : EnumItemFloat,
    dict : EnumItemDict,
    EnumItemDict : EnumItemDict,
    set : EnumItemSet,
    EnumItemSet : EnumItemSet,
    tuple : EnumItemTuple,
    EnumItemTuple : EnumItemTuple,
    list : EnumItemList,
    EnumItemList : EnumItemList,
    EnumItem : EnumItem
}

STRICTLY_DERIVATED_ENUM_ITEM_CLASS_SET = {
    EnumItemStr,
    EnumItemInt,
    EnumItemFloat,
    EnumItemDict,
    EnumItemSet,
    EnumItemTuple,
    EnumItemList
}

DERIVATED_ENUM_ITEM_CLASS_SET = set([
    EnumItem,
    *STRICTLY_DERIVATED_ENUM_ITEM_CLASS_SET
])


def isEnum(possibleEnum):
    itIs = False
    try :
        itIs = isinstance(possibleEnum, Enum)
    except Exception as exception :
        log.error(isEnum, f'Not possible to evaluate. Returning {itIs} by default', exception)
    return itIs


def isEnumItem(possibleEnumItem):
    itIs = False
    try :
        itIs = isinstance(possibleEnumItem, EnumItem)
    except Exception as exception :
        log.error(isEnumItem, f'Not possible to evaluate. Returning {itIs} by default', exception)
    return itIs


def Enum(instanceLog=False, associateReturnsTo=ENUM_VALUE_AS_STRING_KEY):
    def Wrapper(OuterEnum, *args, **kwargs):
        def __raiseBadImplementation__(enumValue, enum=None):
            raise Exception(f'Not possible to implement "{enumValue}" enum value in {enum} enum')
        def __raiseEnumValueNotImplemented__(enumValue, enumClass=None, enumEqList=None, enumMap=None):
            raise Exception(f'Not possible to retrieve "{enumValue}" of type: {type(enumValue)} enum value from {ReflectionHelper.getName(enumClass)}: {enumEqList} enum. Enum.__enumMap__ = {enumMap}')
        if instanceLog :
            log.log(Enum,f'''wrapping {OuterEnum.__name__}''')
        class InnerEnum(OuterEnum, EnumClass):
            OuterEnum.__enumMap__ = {}
            OuterEnum.__enumEqList__ = []
            def __init__(self,*args,**kwargs):
                originalClassAttributeValueList = ReflectionHelper.getAttributeNameList(OuterEnum)
                if instanceLog :
                    log.prettyPython(OuterEnum, 'originalClassAttributeValueList', originalClassAttributeValueList)
                OuterEnum.__init__(self,*args,**kwargs)
                self.__associateReturnsTo__ = associateReturnsTo
                attributeDataList = ReflectionHelper.getAttributeDataList(self)
                if instanceLog :
                    log.prettyPython(OuterEnum, 'attributeDataList', attributeDataList)
                for attribute, enumValue in attributeDataList :
                    if enumValue not in ENUM_STATIC_METHOD_NAME_LIST and enumValue not in originalClassAttributeValueList :
                        __raiseBadImplementation__(enumValue, enum=self)
                    nativeClassDataList = []
                    attributeAttributeDataList = ReflectionHelper.getAttributeDataList(attribute)
                    if instanceLog :
                        log.prettyPython(OuterEnum, 'attributeAttributeDataList', attributeAttributeDataList)
                        # print(f'type({attribute}): {type(attribute)}')
                    association = ReflectionHelper.getAttributeOrMethod(attribute, self.__associateReturnsTo__, muteLogs=True)
                    # if type(association) is type(None):
                    if ObjectHelper.isNone(association):
                        # print('type(association) is type(None)')
                        setInnerAttributeValue(attribute, ENUM_VALUE_AS_STRING_KEY, enumValue)
                        nativeClassDataList = ReflectionHelper.getAttributeDataList(type(enumValue)())
                        # print(f'type({enumValue}): {type(enumValue)}, type({type(enumValue)}()): {type(type(enumValue)())}')
                    else :
                        # print('not type(association) is type(None)')
                        setInnerAttributeValue(attribute, ENUM_VALUE_AS_STRING_KEY, association)
                        nativeClassDataList = ReflectionHelper.getAttributeDataList(type(association)())
                        # print(f'type({association}): {type(association)}, type({type(association)}()): {type(type(association)())}')
                    # print()
                    attribute.enumValue.enumName = enumValue
                    ReflectionHelper.setAttributeOrMethod(attribute, ENUM_NAME_AS_STRING_KEY, enumValue)
                    # print(f'    ---> {attribute.enumValue.enumName=}')
                    # print(f'    ---> {attribute.enumValue=}')
                    # print(f'    ---> {attribute.enumName=}')
                    # if isinstance(attribute, EnumItem) and type(attribute) not in STRICTLY_DERIVATED_ENUM_ITEM_CLASS_SET:
                    if isEnumItemInstance(attribute) and type(attribute):
                        # print(attribute, attribute.enumName, attribute)
                        updateEnumItem(attribute, attribute.enumName, attribute) ###- so that __eq__ does not crash
                    if not c.TYPE_FUNCTION == ReflectionHelper.getClassName(attribute):
                        attribute.enumValue.__enumItemMap__ = attribute.__enumItemMap__
                        attribute.enumValue.__enumItemEqMap__ = attribute.__enumItemEqMap__
                    for dataInstance, dataName in attributeAttributeDataList :
                        nativeData = False
                        for _, name in nativeClassDataList :
                            if dataName == name :
                                nativeData = True
                                break
                        if not nativeData :
                            ReflectionHelper.setAttributeOrMethod(attribute.enumValue, dataName, dataInstance)
                    ReflectionHelper.setAttributeOrMethod(attribute.enumValue, ENUM_VALUE_AS_STRING_KEY, ReflectionHelper.getAttributeOrMethod(attribute, self.__associateReturnsTo__, muteLogs=True))
                    ReflectionHelper.setAttributeOrMethod(attribute.enumValue, ENUM_NAME_AS_STRING_KEY, enumValue)
                    ReflectionHelper.setAttributeOrMethod(attribute.enumValue, ENUM_AS_STRING_KEY, self)
                if ObjectHelper.isEmpty(OuterEnum.__enumEqList__):
                    for attribute, value in attributeDataList :
                        # print(f'type({value}): {type(value)}')
                        # print(f'type({attribute}): {type(attribute)}')
                        valueAsString = str(attribute.enumValue)
                        # print(f'    --> {valueAsString=}')
                        if valueAsString not in ENUM_STATIC_METHOD_NAME_LIST :
                            if valueAsString not in self.__enumMap__ :
                                self.__enumMap__[valueAsString] = attribute.enumValue ###- ReflectionHelper.getAttributeOrMethod(attribute, valueAsString, muteLogs=True) ###- attribute
                            else :
                                __raiseBadImplementation__(valueAsString, enum=self)
                            if value not in self.__enumMap__ :
                                self.__enumMap__[value] = attribute
                            elif not self.__enumMap__[value] == attribute :
                                __raiseBadImplementation__(valueAsString, enum=self)
                            self.__enumEqList__.append(f'{value}({self.__associateReturnsTo__}:{valueAsString})')

            def __eq__(self, other):
                return str(self) == str(other)

            def __ne__(self, other):
                return str(self) != str(other)

            def __str__(self):
                return StringHelper.join([ReflectionHelper.getName(OuterEnum), c.COLON_SPACE, str(self.__enumEqList__)])

            def __repr__(self):
                return self.__str__()

            @staticmethod
            def map(enumItemOrEnumItemValue):
                if instanceLog :
                    log.log(OuterEnum,f'''enumItemOrEnumItemValue: {enumItemOrEnumItemValue}''')
                if ObjectHelper.isNone(enumItemOrEnumItemValue):
                    return enumItemOrEnumItemValue
                else :
                    # try :
                    #     print(f'''not ReflectionHelper.hasAttributeOrMethod({enumItemOrEnumItemValue}, 'enumName') --> {str(enumItemOrEnumItemValue)}''')
                    # except :
                    #     print(f'''ReflectionHelper.hasAttributeOrMethod({enumItemOrEnumItemValue}, 'enumName') --> {enumItemOrEnumItemValue.enumName}''')
                    mappedEnum = OuterEnum.__enumMap__.get(str(enumItemOrEnumItemValue) if not ReflectionHelper.hasAttributeOrMethod(enumItemOrEnumItemValue, 'enumName') else enumItemOrEnumItemValue.enumName)
                    return mappedEnum if ObjectHelper.isNotNone(mappedEnum) else __raiseEnumValueNotImplemented__(enumItemOrEnumItemValue, enumClass=OuterEnum, enumEqList=OuterEnum.__enumEqList__, enumMap=OuterEnum.__enumMap__)

            def getItems(self):
                return [
                    *ReflectionHelper.getAttributeDataDictionary(self).values()
                ]

            def getItemsAsString(self):
                return [
                    enumItem.enumName
                    for enumItem in ReflectionHelper.getAttributeDataDictionary(self).values()
                    # if ReflectionHelper.isNotMethodClass(enumItem)
                ]

        ReflectionHelper.overrideSignatures(InnerEnum, OuterEnum)
        return InnerEnum
    return Wrapper
