from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem

@Enum(associateReturnsTo='key')
class HttpStatusEnumeration() :
    CHRONOS = EnumItem(key='cron')
    INTERVAL = EnumItem(key='interval')

SchedulerType = HttpStatusEnumeration()
