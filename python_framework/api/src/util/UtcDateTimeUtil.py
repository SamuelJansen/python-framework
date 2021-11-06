import datetime
from python_helper import DateTimeHelper, ObjectHelper

def now():
    return datetime.datetime.utcnow()

def ofTimestamp(t):
    return datetime.datetime.utcfromtimestamp(t)
    
def plusMinutes(givenDateTime, minutes=None, deltaInMinutes=None) :
    if ObjectHelper.isNotNone(minutes) :
        deltaInMinutes = DateTimeHelper.timeDelta(seconds=minutes*60)
    return givenDateTime + deltaInMinutes
