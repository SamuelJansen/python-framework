import json
from python_helper import log, Test, RandomHelper, ReflectionHelper, ObjectHelper
from python_framework.api.src.helper import Serializer
from python_framework.api.src.service import SqlAlchemyProxy as sap
from MyDto import MyDto
from MyOtherDto import MyOtherDto
from MyThirdDto import MyThirdDto
from TestCallDto import TestCallRequestDto
import CallServiceName, CallType, CallStatus

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
DATE_TIME_TEST = 'DateTimeTest'

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

import datetime
from python_helper import Constant as c
from python_helper import ObjectHelper

DEFAULT_DATETIME_PATTERN = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_PATTERN = '%Y-%m-%d'
DEFAULT_TIME_PATTERN = '%H:%M:%S'

DATETIME_FULL_PATTERN = '%Y-%m-%d %H:%M:%S.%f'
TIME_FULL_PATTERN = '%H:%M:%S.%f'

PATTERN_LIST = [
    DEFAULT_DATETIME_PATTERN,
    DEFAULT_DATE_PATTERN,
    DEFAULT_TIME_PATTERN,
    DATETIME_FULL_PATTERN,
    TIME_FULL_PATTERN
]

DATETIME_PATTERN_LIST = [
    DEFAULT_DATETIME_PATTERN,
    DATETIME_FULL_PATTERN
]

DATE_PATTERN_LIST = [
    DEFAULT_DATE_PATTERN
]

TIME_PATTERN_LIST = [
    DEFAULT_TIME_PATTERN,
    TIME_FULL_PATTERN
]

DEFAULT_TIME_BEGIN = '00:00:01'
DEFAULT_TIME_END = '23:59:59'

def toString(givenDatetime, pattern=DEFAULT_DATETIME_PATTERN) :
    return givenDatetime if ObjectHelper.isNone(givenDatetime) or isinstance(givenDatetime, str) else parseToString(givenDatetime, pattern=pattern)

def parseToString(given, pattern=DEFAULT_DATETIME_PATTERN) :
    return str(given)

def parseToDatetimeOrDateOrTimePattern(given, pattern=DEFAULT_DATETIME_PATTERN, timedelta=False) :
    parsed = datetime.datetime.strptime(given, pattern)
    if timedelta and pattern in TIME_PATTERN_LIST :
        # try :
        #     a = datetime.timedelta(hours=parsed.hour, minutes=parsed.minute, seconds=parsed.second, milliseconds=0, microseconds=0)
        #     print(type(a))
        # except Exception as exception :
        #     print(exception)
        #     pass
        return datetime.timedelta(hours=parsed.hour, minutes=parsed.minute, seconds=parsed.second, milliseconds=0, microseconds=0)
    if pattern in DATETIME_PATTERN_LIST :
        return parsed
    elif pattern in DATE_PATTERN_LIST :
        return parsed.date()
    elif pattern in TIME_PATTERN_LIST :
        return parsed.time()

def forcedlyParse(given, pattern=DEFAULT_DATETIME_PATTERN, timedelta=False) :
    parsed = None
    for pattern in [pattern] + PATTERN_LIST :
        try :
            parsed = parseToDatetimeOrDateOrTimePattern(given, pattern=pattern, timedelta=timedelta)
        except Exception as exception :
            pass
    return parsed

def getDatetime(givenDatetime, pattern=DEFAULT_DATETIME_PATTERN) :
    return givenDatetime if ObjectHelper.isNone(givenDatetime) or not isinstance(givenDatetime, str) else parseToDatetimeOrDateOrTimePattern(givenDatetime, pattern=pattern)

def forcedlyGetDatetime(givenDatetime, pattern=DEFAULT_DATETIME_PATTERN) :
    return givenDatetime if ObjectHelper.isNone(givenDatetime) or not isinstance(givenDatetime, str) else forcedlyParse(givenDatetime, pattern=pattern)

def forcedlyGetDate(givenDate, pattern=DEFAULT_DATE_PATTERN) :
    return givenDate if ObjectHelper.isNone(givenDate) or not isinstance(givenDate, str) else forcedlyParse(givenDate, pattern=pattern)

def forcedlyGetTime(givenTime, pattern=DEFAULT_TIME_PATTERN) :
    return givenTime if ObjectHelper.isNone(givenTime) or not isinstance(givenTime, str) else forcedlyParse(givenTime, pattern=pattern)

def forcedlyGetInterval(givenTime, pattern=DEFAULT_DATETIME_PATTERN) :
    return givenTime if ObjectHelper.isNone(givenTime) or not isinstance(givenTime, str) else forcedlyParse(givenTime, pattern=pattern, timedelta=True)

class DateTimeTest(MODEL) :
    __tablename__ = DATE_TIME_TEST
    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    beginAtDatetime = sap.Column(sap.DateTime)
    endAtDatetime = sap.Column(sap.DateTime)
    beginAtDate = sap.Column(sap.Date)
    endAtDate = sap.Column(sap.Date)
    beginAtTime = sap.Column(sap.Time)
    endAtTime = sap.Column(sap.Time)
    intervalTime = sap.Column(sap.Interval)

    def __init__(self,
        id = None,
        beginAtDatetime = None,
        endAtDatetime = None,
        beginAtDate = None,
        endAtDate = None,
        beginAtTime = None,
        endAtTime = None,
        intervalTime = None,
        timedelta = None
    ):
        self.id = id
        self.beginAtDatetime = forcedlyGetDatetime(beginAtDatetime)
        self.endAtDatetime = forcedlyGetDatetime(endAtDatetime)
        self.beginAtDate = forcedlyGetDate(beginAtDate)
        self.endAtDate = forcedlyGetDate(endAtDate)
        self.beginAtTime = forcedlyGetTime(beginAtTime)
        self.endAtTime = forcedlyGetTime(endAtTime)
        self.intervalTime = forcedlyGetInterval(intervalTime)
        self.timedelta = forcedlyGetInterval(timedelta)

class DateTimeTestResponseDto :
    def __init__(self,
        id = None,
        beginAtDatetime = None,
        endAtDatetime = None,
        beginAtDate = None,
        endAtDate = None,
        beginAtTime = None,
        endAtTime = None,
        intervalTime = None,
        timedelta = None
    ) :
        self.id = id
        self.beginAtDatetime = toString(beginAtDatetime, pattern=DEFAULT_DATETIME_PATTERN)
        self.endAtDatetime = toString(endAtDatetime, pattern=DEFAULT_DATETIME_PATTERN)
        self.beginAtDate = toString(beginAtDate, pattern=DEFAULT_DATE_PATTERN)
        self.endAtDate = toString(endAtDate, pattern=DEFAULT_DATE_PATTERN)
        self.beginAtTime = toString(beginAtTime, pattern=DEFAULT_TIME_PATTERN)
        self.endAtTime = toString(endAtTime, pattern=DEFAULT_TIME_PATTERN)
        self.intervalTime = toString(intervalTime, pattern=DEFAULT_DATETIME_PATTERN)
        self.timedelta = toString(timedelta, pattern=DEFAULT_TIME_PATTERN)

@Test()
def fromModelToDto() :
    # arrange
    mockedDatetimeAsString = '2021-03-11 08:30:00'
    mockedDateAsString = mockedDatetimeAsString.split()[0]
    mockedTimeAsString = mockedDatetimeAsString.split()[1]
    instance = DateTimeTest(
        beginAtDatetime = forcedlyGetDatetime(mockedDatetimeAsString),
        endAtDatetime = forcedlyGetDatetime(mockedDatetimeAsString),
        beginAtDate = forcedlyGetDate(mockedDateAsString),
        endAtDate = forcedlyGetDate(mockedDateAsString),
        beginAtTime = forcedlyGetTime(mockedTimeAsString),
        endAtTime = forcedlyGetTime(mockedTimeAsString),
        intervalTime = forcedlyGetInterval(mockedDatetimeAsString),
        timedelta = forcedlyGetInterval(mockedTimeAsString)
    )
    # log.prettyPython(fromModelToDto, 'instance', Serializer.getObjectAsDictionary(instance), logLevel=log.DEBUG)
    instanceList = [
        instance,
        instance
    ]

    # act
    toAssert = Serializer.convertFromObjectToObject(instance, DateTimeTestResponseDto)
    listToAssert = Serializer.convertFromObjectToObject(instanceList, [[DateTimeTestResponseDto]])
    # log.prettyPython(fromModelToDto, 'toAssert', Serializer.getObjectAsDictionary(toAssert), logLevel=log.DEBUG)
    # log.prettyPython(fromModelToDto, 'listToAssert', Serializer.getObjectAsDictionary(listToAssert), logLevel=log.DEBUG)

    # assert
    assert ObjectHelper.isNotEmpty(toAssert)
    assert str == type(toAssert.beginAtDatetime)
    assert str == type(toAssert.endAtDatetime)
    assert str == type(toAssert.beginAtDate)
    assert str == type(toAssert.endAtDate)
    assert str == type(toAssert.beginAtTime)
    assert str == type(toAssert.endAtTime)
    assert str == type(toAssert.intervalTime)
    assert str == type(toAssert.timedelta)
    assert ObjectHelper.equals(
        {
            'beginAtDate': '2021-03-11',
            'beginAtDatetime': '2021-03-11 08:30:00',
            'beginAtTime': '08:30:00',
            'endAtDate': '2021-03-11',
            'endAtDatetime': '2021-03-11 08:30:00',
            'endAtTime': '08:30:00',
            'id': None,
            'intervalTime': '2021-03-11 08:30:00',
            'timedelta': '08:30:00'
        },
        Serializer.getObjectAsDictionary(toAssert),
        ignoreKeyList = [
            'timedelta'
        ]
    )
    assert ObjectHelper.isNotEmpty(listToAssert)
    assert ObjectHelper.equals(
        [
            {
                'beginAtDate': '2021-03-11',
                'beginAtDatetime': '2021-03-11 08:30:00',
                'beginAtTime': '08:30:00',
                'endAtDate': '2021-03-11',
                'endAtDatetime': '2021-03-11 08:30:00',
                'endAtTime': '08:30:00',
                'id': None,
                'intervalTime': '2021-03-11 08:30:00',
                'timedelta': '08:30:00'
            },
            {
                'beginAtDate': '2021-03-11',
                'beginAtDatetime': '2021-03-11 08:30:00',
                'beginAtTime': '08:30:00',
                'endAtDate': '2021-03-11',
                'endAtDatetime': '2021-03-11 08:30:00',
                'endAtTime': '08:30:00',
                'id': None,
                'intervalTime': '2021-03-11 08:30:00',
                'timedelta': '08:30:00'
            }
        ],
        Serializer.getObjectAsDictionary(listToAssert),
        ignoreKeyList = [
            'timedelta'
        ]
    )

@Test()
def fromDtoToModel() :
    # arrange
    mockedDatetimeAsString = '2021-03-11 08:30:00'
    mockedDateAsString = mockedDatetimeAsString.split()[0]
    mockedTimeAsString = mockedDatetimeAsString.split()[1]
    instance = DateTimeTestResponseDto(
        beginAtDatetime = mockedDatetimeAsString,
        endAtDatetime = mockedDatetimeAsString,
        beginAtDate = mockedDateAsString,
        endAtDate = mockedDateAsString,
        beginAtTime = mockedTimeAsString,
        endAtTime = mockedTimeAsString,
        intervalTime = mockedDatetimeAsString,
        timedelta = mockedTimeAsString
    )
    # log.prettyPython(fromModelToDto, 'instance', Serializer.getObjectAsDictionary(instance), logLevel=log.DEBUG)
    instanceList = [
        instance,
        instance
    ]

    # act
    toAssert = Serializer.convertFromObjectToObject(instance, DateTimeTest)
    listToAssert = Serializer.convertFromObjectToObject(instanceList, [[DateTimeTest]])
    # log.prettyPython(fromDtoToModel, 'toAssert', Serializer.getObjectAsDictionary(toAssert), logLevel=log.DEBUG)
    # log.prettyPython(fromModelToDto, 'listToAssert', Serializer.getObjectAsDictionary(listToAssert), logLevel=log.DEBUG)

    # assert
    assert ObjectHelper.isNotEmpty(toAssert)
    assert datetime.datetime == type(toAssert.beginAtDatetime)
    assert datetime.datetime == type(toAssert.endAtDatetime)
    assert datetime.date == type(toAssert.beginAtDate)
    assert datetime.date == type(toAssert.endAtDate)
    assert datetime.time == type(toAssert.beginAtTime)
    assert datetime.time == type(toAssert.endAtTime)
    assert datetime.datetime == type(toAssert.intervalTime)
    assert datetime.timedelta == type(toAssert.timedelta)
    assert ObjectHelper.equals(
        {
            'beginAtDate': '2021-03-11',
            'beginAtDatetime': '2021-03-11 08:30:00',
            'beginAtTime': '08:30:00',
            'endAtDate': '2021-03-11',
            'endAtDatetime': '2021-03-11 08:30:00',
            'endAtTime': '08:30:00',
            'id': None,
            'intervalTime': '2021-03-11 08:30:00',
            'timedelta': '08:30:00'
        },
        Serializer.getObjectAsDictionary(toAssert),
        ignoreKeyList = [
            'timedelta'
        ]
    )
    assert ObjectHelper.isNotEmpty(listToAssert)
    assert ObjectHelper.equals(
        [
            {
                'beginAtDate': '2021-03-11',
                'beginAtDatetime': '2021-03-11 08:30:00',
                'beginAtTime': '08:30:00',
                'endAtDate': '2021-03-11',
                'endAtDatetime': '2021-03-11 08:30:00',
                'endAtTime': '08:30:00',
                'id': None,
                'intervalTime': '2021-03-11 08:30:00',
                'timedelta': '08:30:00'
            },
            {
                'beginAtDate': '2021-03-11',
                'beginAtDatetime': '2021-03-11 08:30:00',
                'beginAtTime': '08:30:00',
                'endAtDate': '2021-03-11',
                'endAtDatetime': '2021-03-11 08:30:00',
                'endAtTime': '08:30:00',
                'id': None,
                'intervalTime': '2021-03-11 08:30:00',
                'timedelta': '08:30:00'
            }
        ],
        Serializer.getObjectAsDictionary(listToAssert),
        ignoreKeyList = [
            'timedelta'
        ]
    )

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

@Test()
def convertFromJsonToObject_whenThereAreEnums() :
    # arrange
    jsonToConvert = [
      {
        "beginAtDate": "2021-03-11",
        "beginAtTime": "08:00:00",
        "endAtDate": "2021-03-11",
        "endAtTime": "09:00:00",
        "hoster": "Tati",
        "service": "teams",
        "url": "https://teams.microsoft.com/dl/launcher/launcher.html?url=%2F_%23%2Fl%2Fmeetup-join%2F19%3Ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2%2F0%3Fcontext%3D%257b%2522Tid%2522%253a%2522b8329613-0680-4673-a03f-9a18a0b0e93b%2522%252c%2522Oid%2522%253a%2522fcb6e799-c1f0-4556-be74-3302ea89c13d%2522%257d%26anon%3Dtrue&type=meetup-join&deeplinkId=98d55d14-abc6-4abf-a4a8-5af45024d137&directDl=true&msLaunch=true&enableMobilePage=true&suppressPrompt=true"
      },
      {
        "beginAtDate": "2021-03-11",
        "beginAtTime": "14:00:00",
        "endAtDate": "2021-03-11",
        "endAtTime": "15:00:00",
        "hoster": "Cristiano / Tati",
        "note": "Alinhamento Desmarcação",
        "service": "teams",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_YzQ3YTY1ZWUtYzg4Ny00NDg1LTkwNGEtYTBhYmNhM2RjOWZi%40thread.v2/0?context=%7b%22Tid%22%3a%22647631af-8bf8-4048-a98f-b1fbee134a6d%22%2c%22Oid%22%3a%22be78d394-2f08-4059-bee9-97b849e03cdb%22%7d"
      },
      {
        "beginAtDate": "2021-03-16",
        "beginAtTime": "10:00:00",
        "endAtDate": "2021-03-16",
        "endAtTime": "11:00:00",
        "hoster": "Riachuelo",
        "note": "Daily Riachuelo - Terça",
        "type": "DAILY",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      },
      {
        "beginAtDate": "2021-03-10",
        "beginAtTime": "10:00:00",
        "endAtDate": "2021-03-10",
        "endAtTime": "11:00:00",
        "hoster": "Riachuelo",
        "note": "Daily Riachuelo - Quarda",
        "type": "DAILY",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      },
      {
        "beginAtDate": "2021-03-12",
        "beginAtTime": "10:00:00",
        "endAtDate": "2021-03-12",
        "endAtTime": "11:00:00",
        "hoster": "Riachuelo",
        "note": "Daily Riachuelo - Sexta",
        "type": "DAILY",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      },
      {
        "beginAtDate": "2021-03-15",
        "beginAtTime": "15:00:00",
        "endAtDate": "2021-03-15",
        "endAtTime": "16:00:00",
        "hoster": "Riachuelo",
        "note": "Daily Riachuelo - Segunda",
        "type": "DAILY",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_ZDZmMGUzY2UtZWQzZS00NDQ3LWEwZDMtMzc0MzQwYjYxNWQ1%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      },
      {
        "beginAtDate": "2021-03-11",
        "beginAtTime": "17:30:00",
        "endAtDate": "2021-03-11",
        "endAtTime": "18:30:00",
        "hoster": "Riachuelo",
        "note": "Daily Riachuelo - Quinta",
        "type": "DAILY",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      },
      {
        "beginAtDate": "2021-03-18",
        "beginAtTime": "11:00:00",
        "endAtDate": "2021-03-18",
        "endAtTime": "12:00:00",
        "hoster": "Hoffmann",
        "note": "CWI - Trimestral",
        "service": "meet",
        "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
      }
    ]

    # act
    toAssert = Serializer.convertFromJsonToObject(jsonToConvert, [[TestCallRequestDto]])

    # assert
    # print(Serializer.prettify(Serializer.getObjectAsDictionary(toAssert)))
    assert 'meet' == CallServiceName.CallServiceName.map('meet')
    assert 'zoom' == CallServiceName.CallServiceName.map('zoom')
    assert 'teams' == CallServiceName.CallServiceName.map('teams')
    assert 'UNIQUE' == CallType.CallType.map('UNIQUE')
    assert 'DAILY' == CallType.CallType.map('DAILY')
    assert 'INCOMMING' == CallStatus.CallStatus.map('INCOMMING')
    assert 'WASTED' == CallStatus.CallStatus.map('WASTED')
    assert ObjectHelper.equals(
        [
            {
                "beginAtDate": "2021-03-11",
                "beginAtTime": "08:00:00",
                "endAtDate": "2021-03-11",
                "endAtTime": "09:00:00",
                "hoster": "Tati",
                "note": None,
                "service": "teams",
                "status": None,
                "type": None,
                "url": "https://teams.microsoft.com/dl/launcher/launcher.html?url=%2F_%23%2Fl%2Fmeetup-join%2F19%3Ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2%2F0%3Fcontext%3D%257b%2522Tid%2522%253a%2522b8329613-0680-4673-a03f-9a18a0b0e93b%2522%252c%2522Oid%2522%253a%2522fcb6e799-c1f0-4556-be74-3302ea89c13d%2522%257d%26anon%3Dtrue&type=meetup-join&deeplinkId=98d55d14-abc6-4abf-a4a8-5af45024d137&directDl=true&msLaunch=true&enableMobilePage=true&suppressPrompt=true"
            },
            {
                "beginAtDate": "2021-03-11",
                "beginAtTime": "14:00:00",
                "endAtDate": "2021-03-11",
                "endAtTime": "15:00:00",
                "hoster": "Cristiano / Tati",
                "note": "Alinhamento Desmarcação",
                "service": "teams",
                "status": None,
                "type": None,
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_YzQ3YTY1ZWUtYzg4Ny00NDg1LTkwNGEtYTBhYmNhM2RjOWZi%40thread.v2/0?context=%7b%22Tid%22%3a%22647631af-8bf8-4048-a98f-b1fbee134a6d%22%2c%22Oid%22%3a%22be78d394-2f08-4059-bee9-97b849e03cdb%22%7d"
            },
            {
                "beginAtDate": "2021-03-16",
                "beginAtTime": "10:00:00",
                "endAtDate": "2021-03-16",
                "endAtTime": "11:00:00",
                "hoster": "Riachuelo",
                "note": "Daily Riachuelo - Terça",
                "service": None,
                "status": None,
                "type": "DAILY",
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            },
            {
                "beginAtDate": "2021-03-10",
                "beginAtTime": "10:00:00",
                "endAtDate": "2021-03-10",
                "endAtTime": "11:00:00",
                "hoster": "Riachuelo",
                "note": "Daily Riachuelo - Quarda",
                "service": None,
                "status": None,
                "type": "DAILY",
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            },
            {
                "beginAtDate": "2021-03-12",
                "beginAtTime": "10:00:00",
                "endAtDate": "2021-03-12",
                "endAtTime": "11:00:00",
                "hoster": "Riachuelo",
                "note": "Daily Riachuelo - Sexta",
                "service": None,
                "status": None,
                "type": "DAILY",
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_MmQ5ZjliYmQtZDZhYi00MjkwLWE2NGMtOWIxMmUzYzZhYjFh%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            },
            {
                "beginAtDate": "2021-03-15",
                "beginAtTime": "15:00:00",
                "endAtDate": "2021-03-15",
                "endAtTime": "16:00:00",
                "hoster": "Riachuelo",
                "note": "Daily Riachuelo - Segunda",
                "service": None,
                "status": None,
                "type": "DAILY",
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_ZDZmMGUzY2UtZWQzZS00NDQ3LWEwZDMtMzc0MzQwYjYxNWQ1%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            },
            {
                "beginAtDate": "2021-03-11",
                "beginAtTime": "17:30:00",
                "endAtDate": "2021-03-11",
                "endAtTime": "18:30:00",
                "hoster": "Riachuelo",
                "note": "Daily Riachuelo - Quinta",
                "service": None,
                "status": None,
                "type": "DAILY",
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            },
            {
                "beginAtDate": "2021-03-18",
                "beginAtTime": "11:00:00",
                "endAtDate": "2021-03-18",
                "endAtTime": "12:00:00",
                "hoster": "Hoffmann",
                "note": "CWI - Trimestral",
                "service": "meet",
                "status": None,
                "type": None,
                "url": "https://teams.microsoft.com/l/meetup-join/19%3ameeting_Y2Q1MWI1MWMtOWE0YS00OWJkLTkxNGMtYWMxNDczNTgxYTlj%40thread.v2/0?context=%7b%22Tid%22%3a%22b8329613-0680-4673-a03f-9a18a0b0e93b%22%2c%22Oid%22%3a%22fcb6e799-c1f0-4556-be74-3302ea89c13d%22%7d"
            }
        ],
        Serializer.getObjectAsDictionary(toAssert)
    )
