from python_framework.api.src.annotation.EnumAnnotation import Enum, EnumItem


@Enum(associateReturnsTo='number')
class WeekDayEnumeration :
    MONDAY = EnumItem(number=0, short='mon')
    TUESDAY = EnumItem(number=1, short='tue')
    WEDNESDAY = EnumItem(number=2, short='wed')
    THURSDAY = EnumItem(number=3, short='thu')
    FRIDAY = EnumItem(number=4, short='fri')
    SATURDAY = EnumItem(number=5, short='sat')
    SUNDAY = EnumItem(number=6, short='sun')

WeekDay = WeekDayEnumeration()
