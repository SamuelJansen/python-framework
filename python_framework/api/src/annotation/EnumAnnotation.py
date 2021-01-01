from python_helper import log, ReflectionHelper
from python_framework.api.src.annotation import MethodWrapper
from python_framework.api.src.service.flask import FlaskManager
from python_framework.api.src.helper import Serializer

VALUE_AS_STRING_KEY = 'value'

MAP_METHOD_NAME = 'map'
ENUM_METHOD_NAME_LIST = [
    MAP_METHOD_NAME
]

class EnumClass(object) :
    ...

class EnumItem :
    def __init__(self,**kwargs):
        for key,value in kwargs.items() :
            setattr(self, key, value)

def isEnumItem(possibleEnumItem) :
    itIs = False
    try :
        itIs = isinstance(possibleEnumItem, EnumItem)
    except Exception as exception :
        log.error(isEnumItem, f'not possible to evaluate. Returning {itIs} by default', exception)
    return itIs

def Enum() :
    def Wrapper(OuterEnum, *args, **kwargs):
        def __raiseBadImplementation__(value):
            exception = Exception(f'"{str(value)}" value not implemented in {OuterEnum.__name__} Enum')
            log.error(Enum, 'Bad implementation', exception)
            raise exception
        log.debug(Enum,f'''wrapping {OuterEnum.__name__}''')
        class InnerEnum(OuterEnum, EnumClass):
            def __init__(self,*args,**kwargs):
                originalClassAttributeValueList = ReflectionHelper.getAttributeNameList(OuterEnum)
                log.debug(OuterEnum,f'''originalClassAttributeValueList={originalClassAttributeValueList}''')
                OuterEnum.__init__(self,*args,**kwargs)
                attributeDataList = FlaskManager.getAttributeDataList(self)
                for attribute, value in attributeDataList :
                    if value not in ENUM_METHOD_NAME_LIST and value not in originalClassAttributeValueList :
                        __raiseBadImplementation__(value)
                    setattr(attribute, VALUE_AS_STRING_KEY, str(value))

            @staticmethod
            def map(enumItemOrEnumItemValue) :
                log.debug(OuterEnum,f'''enumItemOrEnumItemValue={enumItemOrEnumItemValue}''')
                if isEnumItem(enumItemOrEnumItemValue) :
                    originalClassAttributeValueList = [str(value) for value in ReflectionHelper.getAttributeNameList(OuterEnum)]
                    if enumItemOrEnumItemValue.value not in originalClassAttributeValueList :
                        __raiseBadImplementation__(enumItemOrEnumItemValue.value)
                    return enumItemOrEnumItemValue
                else :
                    attributeList = [
                        attribute
                        for attribute, value in FlaskManager.getAttributeDataList(OuterEnum())
                        if attribute.value == enumItemOrEnumItemValue
                    ]
                    if 0 == len(attributeList) :
                        return None
                    if 1 == len(attributeList) :
                        return attributeList[0]
                    __raiseBadImplementation__(enumItemOrEnumItemValue)
                try :
                    __raiseBadImplementation__(enumItemOrEnumItemValue.value)
                except :
                    try :
                        __raiseBadImplementation__(enumItemOrEnumItemValue)
                    except :
                        __raiseBadImplementation__('NOT_POSSIBLE_TO_EXTRACT_THE_VALUE')
        MethodWrapper.overrideSignatures(InnerEnum, OuterEnum)
        return InnerEnum
    return Wrapper
