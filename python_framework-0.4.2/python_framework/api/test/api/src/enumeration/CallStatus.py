from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem

@Enum()
class CallStatusEnumeration :
    INCOMMING = EnumItem()
    WASTED = EnumItem()

CallStatus = CallStatusEnumeration()
