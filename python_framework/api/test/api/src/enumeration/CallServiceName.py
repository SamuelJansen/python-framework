from python_framework import Enum, EnumItem

@Enum(associateReturnsTo='name')
class CallServiceNameEnumeration :
    TEAMS = EnumItem(name='teams')
    ZOOM = EnumItem(name='zoom')
    MEET = EnumItem(name='meet')

CallServiceName = CallServiceNameEnumeration()
