from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem

@Enum()
class ActuatorHealthStatusEnumeration() :
    UP = EnumItem(name='Api is UP')
    DOWN = EnumItem(name='Api is DOWN')

ActuatorHealthStatus = ActuatorHealthStatusEnumeration()
