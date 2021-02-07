from python_helper import ReflectionHelper, ObjectHelper

class MyOtherDto:
    def __init__(self, myAttribute) :
        self.myAttribute = myAttribute
    def __eq__(self, other) :
        if ObjectHelper.isNone(other) :
            return self is None
        isEqual = True
        for value, name in ReflectionHelper.getAttributeDataList(other) :
            attributeIsEqual = ReflectionHelper.getAttributeOrMethod(self, name) == ReflectionHelper.getAttributeOrMethod(other, name)
            isEqual = isEqual == attributeIsEqual and True == attributeIsEqual
        return isEqual
    def __repr__(self) :
        return f'MyOtherDto(myAttribute: {self.myAttribute})'
