from python_helper import Constant as c
from python_helper import log, ReflectionHelper, ObjectHelper, StringHelper

ENUM_VALUE_AS_STRING_KEY = 'enumValue'
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
        return c.NOTHING.join(StringHelper.prettyPython(self.__enumItemEqMap__, tabCount=2))

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

ENUM_ITEM_CLASS_DICTIONARY = {
    str : EnumItemStr,
    EnumItemStr : EnumItemStr,
    int : EnumItemInt,
    EnumItemInt : EnumItemInt
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
        def __raiseBadImplementation__(enumValue):
            exception = Exception(f'"{str(enumValue)}" enum value not implemented in {OuterEnum.__name__} Enum')
            log.error(Enum, 'Bad implementation', exception)
            raise exception
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
                        __raiseBadImplementation__(enumValue)
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
                    ReflectionHelper.setAttributeOrMethod(attribute.enumValue, ENUM_AS_STRING_KEY, self)
                if ObjectHelper.isEmpty(OuterEnum.__enumEqList__) :
                    for attribute, value in attributeDataList :
                        if str(attribute.enumValue) not in ENUM_STATIC_METHOD_NAME_LIST :
                            valueAsString = str(attribute.enumValue)
                            self.__enumMap__[valueAsString] = attribute
                            self.__enumEqList__.append(valueAsString)

            def __eq__(self, other) :
                return str(self) == str(other)

            def __ne__(self, other) :
                return str(self) != str(other)

            def __str__(self) :
                return c.NOTHING.join([ReflectionHelper.getName(OuterEnum), StringHelper.prettyPython(self.__enumEqList__)])

            @staticmethod
            def map(enumItemOrEnumItemValue) :
                if instanceLog :
                    log.log(OuterEnum,f'''enumItemOrEnumItemValue: {enumItemOrEnumItemValue}''')
                if enumItemOrEnumItemValue in OuterEnum.__enumMap__ :
                    return enumItemOrEnumItemValue
                else :
                    log.prettyPython(OuterEnum, 'OuterEnum.__enumMap__', OuterEnum.__enumMap__)
                    return OuterEnum.__enumMap__.get(enumItemOrEnumItemValue, __raiseBadImplementation__(enumItemOrEnumItemValue))
        ReflectionHelper.overrideSignatures(InnerEnum, OuterEnum)
        return InnerEnum
    return Wrapper
