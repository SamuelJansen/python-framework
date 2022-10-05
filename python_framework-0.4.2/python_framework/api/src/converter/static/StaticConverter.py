from python_helper import DateTimeHelper, ObjectHelper
from python_framework.api.src.util import Serializer

def getValueOrDefault(value, default) :
    return value if ObjectHelper.isNotNone(value) else default

def overrideDateData(model) :
    now = DateTimeHelper.dateTimeNow()
    model.createdAt = getValueOrDefault(model.createdAt, now)
    model.updatedAt = now

def overrideUserData(model, loggedUser) :
    model.createdBy = getValueOrDefault(model.createdBy, loggedUser)
    model.updatedBy = loggedUser

def overrideData(model, loggedUser) :
    overrideDateData(model)
    overrideUserData(model, loggedUser)

def to(dto, toClass) :
    if not (ObjectHelper.isNone(dto) or ObjectHelper.isNone(toClass))  :
        return Serializer.convertFromObjectToObject(dto, toClass)
    return dto

def toList(dtoList, toClass) :
    if not (ObjectHelper.isNone(dtoList) or ObjectHelper.isNone(toClass)) :
        return Serializer.convertFromObjectToObject(dtoList, toClass)
    return dtoList
