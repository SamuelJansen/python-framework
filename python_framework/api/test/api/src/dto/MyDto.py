from python_helper import ReflectionHelper, ObjectHelper

class MyDto:
    def __init__(self, myAttribute, myOther, myThirdList) :
        self.myAttribute = myAttribute
        self.myOther = myOther
        self.myThirdList = myThirdList
    def __eq__(self, other) :
        if ObjectHelper.isNone(other) :
            return self is None
        isEqual = True
        for value, name in ReflectionHelper.getAttributeDataList(other) :
            attributeIsEqual = ReflectionHelper.getAttributeOrMethod(self, name) == ReflectionHelper.getAttributeOrMethod(other, name)
            isEqual = isEqual == attributeIsEqual and True == attributeIsEqual
        return isEqual
    def __repr__(self) :
        return f'MyDto(myAttribute: {self.myAttribute}, myOther: {self.myOther}, myThirdList: {self.myThirdList})'
