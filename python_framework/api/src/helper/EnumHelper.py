from python_helper import log
from python_framework.api.src.service.flask import FlaskManager

def isEnumItem(possibleEnumItem) :
    itIs = False
    try :
        itIs = isinstance(possibleEnumItem, EnumItem)
    except Exception as exception :
        log.error(isEnumItem, f'not possible to evaluate. Returning {itIs} by default', exception)
    return itIs

def mapToEnum(value=None, enumClass=None) :
    def __raiseBadImplementation__(value):
        exception = Exception(f'"{str(value)}" value not implemented in {enumClass.__name__} Enum')
        log.error(mapToEnum, 'Bad implementation', exception)
        raise exception
    if not enumClass :
        exception = Exception('Enum not informed')
        log.error(mapToEnum, 'Enum cannot be null', exception)
        raise exception
    if value :
        possibleEnumList = [
            enumItem
            for enumItem, enumValue in FlaskManager.getAttributeDataList(enumClass())
            if enumItem.value == value and enumValue == value
        ]
        log.debug(mapToEnum, f'possibleEnumList={possibleEnumList}')
        return possibleEnumList[0] if 1 == len(possibleEnumList) else __raiseBadImplementation__(value)
