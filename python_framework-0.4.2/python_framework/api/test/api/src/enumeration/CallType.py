from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem

@Enum()
class CallTypeEnumeration :
    UNIQUE = EnumItem()
    DAILY = EnumItem()

CallType = CallTypeEnumeration()
