import json
from python_helper import log, Test, RandomHelper, ReflectionHelper, ObjectHelper
from python_framework import Serializer
from python_framework import SqlAlchemyProxy as sap
from MyDto import MyDto
from MyOtherDto import MyOtherDto
from MyThirdDto import MyThirdDto

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
def isModelTest() :
    assert False == Serializer.isModel(generatorFunction())
    assert False == Serializer.isModel(MyClass())
    assert True == Serializer.isModel(MyEntityClass())

@Test()
def isJsonifyable() :
    assert False == Serializer.isJsonifyable(generatorFunction())
    assert True == Serializer.isJsonifyable(MyClass())
    assert True == Serializer.isJsonifyable(MyEntityClass())

@Test()
def convertFromObjectToObject_whenTargetClassIsList() :
    # arrange
    a = RandomHelper.string()
    b = RandomHelper.string()
    c = RandomHelper.string()
    otherA = MyOtherDto(RandomHelper.string())
    otherB = MyOtherDto(RandomHelper.string())
    otherC = MyOtherDto(RandomHelper.string())
    myFirst = MyDto(RandomHelper.string(), otherA, [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), None), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())])
    mySecond = MyDto(RandomHelper.string(), otherB, [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), None), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())])
    myThird = MyDto(RandomHelper.string(), otherC, [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), [MyThirdDto(MyDto(RandomHelper.string(), MyOtherDto(RandomHelper.string()), None), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())]), RandomHelper.integer())])
    thirdOne = RandomHelper.integer()
    thirdTwo = RandomHelper.integer()
    thirdThree = RandomHelper.integer()
    myThirdOne = [MyThirdDto(myFirst, thirdOne)]
    myThirdTwo = [MyThirdDto(mySecond, thirdTwo)]
    myThirdThree = [MyThirdDto(myThird, thirdThree)]
    expected = [MyDto(a, otherA, myThirdOne), MyDto(b, otherB, myThirdTwo), MyDto(c, otherC, myThirdThree)]
    null = 'null'
    inspectEquals = False

    # act
    toAssert = Serializer.convertFromObjectToObject(expected, [[MyDto]])
    another = Serializer.convertFromObjectToObject([MyDto(a, otherA, [MyThirdDto(myFirst, thirdOne)]), MyDto(b, otherB, myThirdTwo), MyDto(c, otherC, myThirdThree)], [[MyDto]])
    another[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my = MyDto(
        MyDto(RandomHelper.string(), None, None),
        expected[0].myThirdList[0].my.myOther,
        expected[0].myThirdList[0].my.myThirdList
    )

    # assert
    assert expected == toAssert, f'{expected} == {toAssert}: {expected == toAssert}'
    assert ObjectHelper.equals(expected, toAssert)
    assert ObjectHelper.isNotNone(expected[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my)
    assert expected[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my == toAssert[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my
    assert ObjectHelper.equals(expected[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my, toAssert[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my)
    assert ObjectHelper.isNone(expected[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList)
    assert ObjectHelper.equals(expected[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList, toAssert[0].myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList[0].my.myThirdList)
    assert ObjectHelper.equals(json.loads(Serializer.jsonifyIt(expected)), json.loads(Serializer.jsonifyIt(toAssert))), f'ObjectHelper.equals({json.loads(Serializer.jsonifyIt(expected))},\n\n{json.loads(Serializer.jsonifyIt(toAssert))})'
    assert False == (expected == another), f'False == ({expected} == {another}): False == {(expected == another)}'
    assert False == ObjectHelper.equals(expected, another, muteLogs=not inspectEquals)
    assert False == ObjectHelper.equals(another, expected, muteLogs=not inspectEquals)
    assert False == ObjectHelper.equals(another, toAssert, muteLogs=not inspectEquals)
    assert False == ObjectHelper.equals(toAssert, another, muteLogs=not inspectEquals)
    assert str(expected) == str(toAssert), f'str({str(expected)}) == str({str(toAssert)}): {str(expected) == str(toAssert)}'

@Test()
def jsonifyIt() :
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
