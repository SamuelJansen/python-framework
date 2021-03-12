from python_framework import Enum, EnumItem

@Enum()
class CallTypeEnumeration :
    UNIQUE = EnumItem()
    DAILY = EnumItem()

CallType = CallTypeEnumeration()
