import datetime
from python_helper import DateTimeHelper

def now():
    return datetime.datetime.utcnow()

def timestamp():
    return datetime.datetime.timestamp()

def ofTimestamp(t):
    return datetime.datetime.fromtimestamp(t)

def plusMinutes(givenDateTime, minutes=None, deltaInMinutes=None) :
    if ObjectHelper.isNotNone(minutes) :
        deltaInMinutes = timeDelta(seconds=minutes*60)
    return givenDateTime + deltaInMinutes
