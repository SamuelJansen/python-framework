from python_framework import Enum, EnumItem

@Enum()
class CallStatusEnumeration :
    INCOMMING = EnumItem()
    WASTED = EnumItem()

CallStatus = CallStatusEnumeration()
