from python_helper import log, Test
from python_framework import Serializer
from python_framework import SqlAlchemyProxy as sap

def generatorFunction() :
    while True :
        yield 'something'
        break

class MyClass :
    def __init__(self, myAttribute=None):
        self.myAttribute = myAttribute
        self.myNeutralAttribute = 'someString'

class MyAttributeClass :
    def __init__(self, myClass=None):
        self.myClass = myClass
        self.myNeutralClassAttribute = 'someOtherString'

MY_DICTIONARY = {
    'myString' : 'myValue',
    'myInteger' : 0,
    'myFloat' : 0.099
}

MODEL = sap.getNewModel()

class MyEntityClass(MODEL) :
    __tablename__ = 'MyEntityClass'
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)

SELF_REFERENCE_FATHER_NAME = 'Father'
SELF_REFERENCE_CHILD_NAME = 'Child'
BROTHER_NAME = 'Brother'

class Father(MODEL) :
    __tablename__ = SELF_REFERENCE_FATHER_NAME
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    childList = sap.getOneToMany(__tablename__, SELF_REFERENCE_CHILD_NAME, MODEL)
    brotherList = sap.getOneToMany(__tablename__, BROTHER_NAME, MODEL)

class Brother(MODEL):
    __tablename__ = BROTHER_NAME
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    father, fatherId = sap.getManyToOne(__tablename__, SELF_REFERENCE_FATHER_NAME, MODEL)
    child = sap.getOneToOneParent(__tablename__, SELF_REFERENCE_CHILD_NAME, MODEL)

class Child(MODEL) :
    __tablename__ = SELF_REFERENCE_CHILD_NAME
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    father, fatherId = sap.getManyToOne(__tablename__, SELF_REFERENCE_FATHER_NAME, MODEL)
    brother, brotherId = sap.getOneToOneChild(__tablename__, BROTHER_NAME, MODEL)

@Test()
def Serializer_isModelTest() :
    assert False == Serializer.isModel(generatorFunction())
    assert False == Serializer.isModel(MyClass())
    assert True == Serializer.isModel(MyEntityClass())

@Test()
def Serializer_isJsonifyable() :
    assert False == Serializer.isJsonifyable(generatorFunction())
    assert True == Serializer.isJsonifyable(MyClass())
    assert True == Serializer.isJsonifyable(MyEntityClass())

@Test()
def Serializer_jsonifyIt() :
    assert '{"myString": "myValue", "myInteger": 0, "myFloat": 0.099}' == Serializer.jsonifyIt(MY_DICTIONARY)

    myGenerator = generatorFunction()
    assert myGenerator == Serializer.jsonifyIt(myGenerator)
    assert '{"myAttribute": null, "myNeutralAttribute": "someString"}' == Serializer.jsonifyIt(MyClass())
    assert '{"id": null}' == Serializer.jsonifyIt(MyEntityClass())

    father = Father()
    child = Child()
    brother = Brother()
    otherFather = Father()
    otherBrother = Brother()
    otherChild = Child()

    father.id = 1
    child.id = 2
    brother.id = 3
    otherFather.id = 4
    otherBrother.id = 5
    otherChild.id = 6

    father.childList = [child, otherChild]
    father.brotherList = [otherBrother]

    child.father = father
    child.fatherId = father.id
    child.brother = brother
    child.brotherId = brother.id

    brother.father = otherFather
    brother.fatherId = otherFather.id
    brother.child = child

    otherFather.childList = []
    otherFather.brotherList = [brother]

    otherBrother.father = father
    otherBrother.fatherId = father.id
    otherBrother.child = otherChild

    otherChild.father = father
    otherChild.fatherId = father.id
    otherChild.brother = otherBrother
    otherChild.brotherId = otherBrother.id

    assert '{"brother": {"child": null, "father": {"brotherList": [], "childList": [], "id": 4}, "fatherId": 4, "id": 3}, "brotherId": 3, "father": {"brotherList": [{"child": {"brother": null, "brotherId": 5, "father": null, "fatherId": 1, "id": 6}, "father": null, "fatherId": 1, "id": 5}], "childList": [{"brother": {"child": null, "father": null, "fatherId": 1, "id": 5}, "brotherId": 5, "father": null, "fatherId": 1, "id": 6}], "id": 1}, "fatherId": 1, "id": 2}' == Serializer.jsonifyIt(child)
    assert '{"brotherList": [{"child": {"brother": null, "brotherId": 5, "father": null, "fatherId": 1, "id": 6}, "father": null, "fatherId": 1, "id": 5}], "childList": [{"brother": {"child": null, "father": {"brotherList": [], "childList": [], "id": 4}, "fatherId": 4, "id": 3}, "brotherId": 3, "father": null, "fatherId": 1, "id": 2}, {"brother": {"child": null, "father": null, "fatherId": 1, "id": 5}, "brotherId": 5, "father": null, "fatherId": 1, "id": 6}], "id": 1}' == Serializer.jsonifyIt(father)

    myClass = MyClass()
    myAttributeClass =  MyAttributeClass(myClass=myClass)
    myClass.myAttribute = myAttributeClass
    assert '{"myAttribute": {"myClass": null, "myNeutralClassAttribute": "someOtherString"}, "myNeutralAttribute": "someString"}' == Serializer.jsonifyIt(myClass)
    assert '{"myClass": {"myAttribute": null, "myNeutralAttribute": "someString"}, "myNeutralClassAttribute": "someOtherString"}' == Serializer.jsonifyIt(myClass.myAttribute)
