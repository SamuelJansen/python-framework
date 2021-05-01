from python_helper import DateTimeHelper
from python_helper import ObjectHelper

def getValueOrDefault(value, default) :
    return value if ObjectHelper.isNotNone(value) else default

def overrideDateData(model) :
    now = DateTimeHelper.dateTimeNow()
    model.createdAt = getValueOrDefault(model.createdAt, now)
    model.updatedAt = now
