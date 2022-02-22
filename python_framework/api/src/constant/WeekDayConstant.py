from python_helper import Constant as c
from python_helper import StringHelper

from python_framework.api.src.enumeration.WeekDay import WeekDay


ALL_WEEK = '*'

WEEK_DAY_LIST = [
    WeekDay.MONDAY
    , WeekDay.TUESDAY
    , WeekDay.WEDNESDAY
    , WeekDay.THURSDAY
    , WeekDay.FRIDAY
]

WEEKEND_DAY_LIST = [
    WeekDay.SUNDAY
    , WeekDay.SATURDAY
]

WEEK_LIST = [
    *WEEK_DAY_LIST,
    *WEEKEND_DAY_LIST
]

WEEK_DAY_CHRON = StringHelper.join(
    [weekDay.short for weekDay in WEEK_DAY_LIST],
    character = c.COMA
)

WEEKEND_DAY_CHRON = StringHelper.join(
    [weekDay.short for weekDay in WEEKEND_DAY_LIST],
    character = c.COMA
)

WEEK_CHRON = StringHelper.join(
    [weekDay.short for weekDay in WEEK_LIST],
    character = c.COMA
)
