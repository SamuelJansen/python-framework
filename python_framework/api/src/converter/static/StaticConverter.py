from python_helper import ObjectHelper

def getValueOrDefault(value, default) :
    value if ObjectHelper.isNotNone(value) else default
