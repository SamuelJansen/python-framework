from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem

@Enum(associateReturnsTo='name')
class CallServiceNameEnumeration :
    TEAMS = EnumItem(name='teams')
    ZOOM = EnumItem(name='zoom')
    MEET = EnumItem(name='meet')

CallServiceName = CallServiceNameEnumeration()
