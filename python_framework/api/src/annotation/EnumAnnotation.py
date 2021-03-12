from python_helper import Constant as c
from python_helper import log, ReflectionHelper, ObjectHelper, StringHelper

ENUM_VALUE_AS_STRING_KEY = 'enumValue'
ENUM_NAME_AS_STRING_KEY = 'enumName'
ENUM_AS_STRING_KEY = 'enum'

MAP_METHOD_NAME = 'map'
ENUM_STATIC_METHOD_NAME_LIST = [
    MAP_METHOD_NAME
]

class EnumClass(object) :
    ...

class EnumItem :
    def __init__(self, *args, **kwargs) :
        self.__enumItemMap__ = {}
        self.__enumItemEqMap__ = {}
        for key, value in kwargs.items() :
            self.__enumItemMap__[key] = value
            self.__enumItemEqMap__[key] = value
            ReflectionHelper.setAttributeOrMethod(self, key, ENUM_ITEM_CLASS_DICTIONARY.get(type(value))(value))

    def __get__(self, obj, objtype=None) :
        return self if not ReflectionHelper.hasAttributeOrMethod(self, ENUM_VALUE_AS_STRING_KEY) else self.enumValue

    def __str__(self) :
        return c.NOTHING.join(StringHelper.prettyPython(self.__enumItemEqMap__, tabCount=2, quote=c.NOTHING))

    def __repr__(self) :
        return __str__()

    def __eq__(self, other) :
        if isinstance(other, EnumItem) :
            return str(other.__enumItemEqMap__) == str(self.__enumItemEqMap__)
        return self.enumValue == other

    def __ne__(self, other) :
        if isinstance(other, EnumItem) :
            return str(other.__enumItemEqMap__) != str(self.__enumItemEqMap__)
        return self.enumValue != other

class EnumItemStr(str) :
    ...
class EnumItemInt(int) :
    ...
class EnumItemFloat(float) :
    ...
class EnumItemDict(dict) :
    ...
class EnumItemSet(set) :
    ...
class EnumItemTuple(tuple) :
    ...
class EnumItemList(list) :
    ...
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
    EnumItemList : EnumItemList
}

def isEnumItem(possibleEnumItem) :
    itIs = False
    try :
        itIs = isinstance(possibleEnumItem, EnumItem)
    except Exception as exception :
        log.error(isEnumItem, f'Not possible to evaluate. Returning {itIs} by default', exception)
    return itIs

def Enum(instanceLog=False, associateReturnsTo = ENUM_VALUE_AS_STRING_KEY) :
    def Wrapper(OuterEnum, *args, **kwargs):
        def __raiseBadImplementation__(enumValue, enum=None) :
            raise Exception(f'Not possible to implement "{enumValue}" enum value in {StringHelper.prettyPython(enum, quote=c.NOTHING)} enum')
        def __raiseEnumValueNotImplemented__(enumValue, enumClass=None, enumEqList=None) :
            raise Exception(f'Not possible to retrieve "{enumValue}" enum value from {ReflectionHelper.getName(enumClass)}: {StringHelper.prettyPython(enumEqList, quote=c.NOTHING)} enum')
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
                    association = ReflectionHelper.getAttributeOrMethod(attribute, self.__associateReturnsTo__, muteLogs=True)
                    if type(association) is type(None) :
                        ReflectionHelper.setAttributeOrMethod(attribute, ENUM_VALUE_AS_STRING_KEY, ENUM_ITEM_CLASS_DICTIONARY.get(type(enumValue))(enumValue))
                        nativeClassDataList = ReflectionHelper.getAttributeDataList(type(enumValue)())
                    else :
                        ReflectionHelper.setAttributeOrMethod(attribute, ENUM_VALUE_AS_STRING_KEY, ENUM_ITEM_CLASS_DICTIONARY.get(type(association))(association))
                        nativeClassDataList = ReflectionHelper.getAttributeDataList(type(association)())
                    ReflectionHelper.setAttributeOrMethod(attribute, ENUM_NAME_AS_STRING_KEY, enumValue)
                    if not c.TYPE_FUNCTION == ReflectionHelper.getClassName(attribute) :
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
                if ObjectHelper.isEmpty(OuterEnum.__enumEqList__) :
                    for attribute, value in attributeDataList :
                        if str(attribute.enumValue) not in ENUM_STATIC_METHOD_NAME_LIST :
                            valueAsString = str(attribute.enumValue)
                            if valueAsString not in self.__enumMap__ :
                                self.__enumMap__[valueAsString] = attribute
                            else :
                                __raiseBadImplementation__(valueAsString, enum=self)
                            if value not in self.__enumMap__ :
                                self.__enumMap__[value] = attribute
                            elif not self.__enumMap__[value] == attribute :
                                __raiseBadImplementation__(valueAsString, enum=self)
                            self.__enumEqList__.append(f'{value}({self.__associateReturnsTo__}:{valueAsString})')

            def __eq__(self, other) :
                return str(self) == str(other)

            def __ne__(self, other) :
                return str(self) != str(other)

            def __str__(self) :
                return c.NOTHING.join([ReflectionHelper.getName(OuterEnum), c.COLON_SPACE, StringHelper.prettyPython(self.__enumEqList__, quote=c.NOTHING)])

            def __repr__(self) :
                return __str__()

            @staticmethod
            def map(enumItemOrEnumItemValue) :
                if instanceLog :
                    log.log(OuterEnum,f'''enumItemOrEnumItemValue: {enumItemOrEnumItemValue}''')
                if ObjectHelper.isNone(enumItemOrEnumItemValue) :
                    return enumItemOrEnumItemValue
                else :
                    mappedEnum = OuterEnum.__enumMap__.get(str(enumItemOrEnumItemValue))
                    return mappedEnum if ObjectHelper.isNotNone(mappedEnum) else __raiseEnumValueNotImplemented__(enumItemOrEnumItemValue, enumClass=OuterEnum, enumEqList=OuterEnum().__enumEqList__)
        ReflectionHelper.overrideSignatures(InnerEnum, OuterEnum)
        return InnerEnum
    return Wrapper
