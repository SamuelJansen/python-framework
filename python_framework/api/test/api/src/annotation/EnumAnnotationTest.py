import time
from python_helper import log, Test, SettingHelper, RandomHelper, ObjectHelper
from python_framework import Enum, EnumItem
from python_framework import HttpStatus, ActuatorHealthStatus

LOG_HELPER_SETTINGS = {
    log.LOG : False,
    log.SUCCESS : True,
    log.SETTING : True,
    log.DEBUG : True,
    log.WARNING : True,
    log.WRAPPER : True,
    log.FAILURE : True,
    log.ERROR : True,
    log.TEST : False
}

FULL_LOG_HELPER_SETTINGS = {
    log.LOG : True,
    log.SUCCESS : True,
    log.SETTING : True,
    log.DEBUG : True,
    log.WARNING : True,
    log.WRAPPER : True,
    log.FAILURE : True,
    log.ERROR : True,
    log.TEST : False
}

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def enum_withSuccess() :
    TEST_ITERATION = 1
    ASSERT_ITERATION = 1
    discount = 0
    instanciationTime = 0
    equalTestTime = 0
    start = time.time()
    for _ in range(TEST_ITERATION) :
        # arrange
        discountStart = time.time()
        ITS_NAME = RandomHelper.string(minimum=5, maximum=10)
        A_NAME = RandomHelper.string(minimum=5, maximum=10)
        TEST_NAME = RandomHelper.string(minimum=5, maximum=10)
        ITS_LABEL = RandomHelper.string(minimum=5, maximum=10)
        A_LABEL = RandomHelper.string(minimum=5, maximum=10)
        TEST_LABEL = RandomHelper.string(minimum=5, maximum=10)
        ITS_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
        A_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
        TEST_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
        ITS_VALUE = 'ITS'
        A_VALUE = 'A'
        TEST_VALUE = 'TEST'
        discount += time.time() - discountStart

        # act
        discountStart = time.time()
        @Enum()
        class MyEnumTest :
            ITS = EnumItem(name=ITS_NAME, label=ITS_LABEL, numeric=ITS_NUMERIC)
            A = EnumItem(name=A_NAME, label=A_LABEL, numeric=A_NUMERIC)
            TEST = EnumItem(name=TEST_NAME, label=TEST_LABEL, numeric=TEST_NUMERIC)
        discount += time.time() - discountStart
        instanciationTimeInit = time.time()
        MY_ENUM_TEST = MyEnumTest()
        instanciationTime += time.time() - instanciationTimeInit

        # assert
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert ITS_VALUE == MY_ENUM_TEST.ITS
        discountStart = time.time()
        log.log(enum_withSuccess, f'ITS_VALUE == MY_ENUM_TEST.ITS assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert A_VALUE == MY_ENUM_TEST.A
        discountStart = time.time()
        log.log(enum_withSuccess, f'A_VALUE == MY_ENUM_TEST.A assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert TEST_VALUE == MY_ENUM_TEST.TEST
        discountStart = time.time()
        log.log(enum_withSuccess, f'TEST_VALUE == MY_ENUM_TEST.TEST assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert ITS_NAME == MY_ENUM_TEST.ITS.name
        discountStart = time.time()
        log.log(enum_withSuccess, f'ITS_NAME == MY_ENUM_TEST.ITS.name assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert A_NAME == MY_ENUM_TEST.A.name
        discountStart = time.time()
        log.log(enum_withSuccess, f'A_NAME == MY_ENUM_TEST.A.name assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert TEST_NAME == MY_ENUM_TEST.TEST.name
        discountStart = time.time()
        log.log(enum_withSuccess, f'TEST_NAME == MY_ENUM_TEST.TEST.name assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert ITS_LABEL == MY_ENUM_TEST.ITS.label
        discountStart = time.time()
        log.log(enum_withSuccess, f'ITS_LABEL == MY_ENUM_TEST.ITS.label assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert A_LABEL == MY_ENUM_TEST.A.label
        discountStart = time.time()
        log.log(enum_withSuccess, f'A_LABEL == MY_ENUM_TEST.A.label assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert TEST_LABEL == MY_ENUM_TEST.TEST.label
        discountStart = time.time()
        log.log(enum_withSuccess, f'TEST_LABEL == MY_ENUM_TEST.TEST.label assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert ITS_NUMERIC == MY_ENUM_TEST.ITS.numeric
        discountStart = time.time()
        log.log(enum_withSuccess, f'ITS_NUMERIC == MY_ENUM_TEST.ITS.numeric assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert A_NUMERIC == MY_ENUM_TEST.A.numeric
        discountStart = time.time()
        log.log(enum_withSuccess, f'A_NUMERIC == MY_ENUM_TEST.A.numeric assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert TEST_NUMERIC == MY_ENUM_TEST.TEST.numeric
        discountStart = time.time()
        log.log(enum_withSuccess, f'TEST_NUMERIC == MY_ENUM_TEST.TEST.numeric assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MyEnumTest.map(MY_ENUM_TEST.ITS.enumValue) == MY_ENUM_TEST.ITS
        discountStart = time.time()
        log.log(enum_withSuccess, f'MyEnumTest.map(MY_ENUM_TEST.ITS.enumValue) == MY_ENUM_TEST.ITS assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MyEnumTest.map(MY_ENUM_TEST.A.enumValue) == MY_ENUM_TEST.A
        discountStart = time.time()
        log.log(enum_withSuccess, f'MyEnumTest.map(MY_ENUM_TEST.A.enumValue) == MY_ENUM_TEST.A assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MyEnumTest.map(MY_ENUM_TEST.TEST.enumValue) == MY_ENUM_TEST.TEST
        discountStart = time.time()
        log.log(enum_withSuccess, f'MyEnumTest.map(MY_ENUM_TEST.TEST.enumValue) == MY_ENUM_TEST.TEST assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.ITS.enumValue.enum == MY_ENUM_TEST
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.ITS.enumValue.enum == MY_ENUM_TEST assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.A.enumValue.enum == MY_ENUM_TEST
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.A.enumValue.enum == MY_ENUM_TEST assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.TEST.enumValue.enum == MY_ENUM_TEST
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.TEST.enumValue.enum == MY_ENUM_TEST assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert not MY_ENUM_TEST.ITS.enumValue.enum == MyEnumTest
        discountStart = time.time()
        log.log(enum_withSuccess, f'not MY_ENUM_TEST.ITS.enumValue.enum == MyEnumTest assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert not MY_ENUM_TEST.A.enumValue.enum == MyEnumTest
        discountStart = time.time()
        log.log(enum_withSuccess, f'not MY_ENUM_TEST.A.enumValue.enum == MyEnumTest assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert not MY_ENUM_TEST.TEST.enumValue.enum == MyEnumTest
        discountStart = time.time()
        log.log(enum_withSuccess, f'not MY_ENUM_TEST.TEST.enumValue.enum == MyEnumTest assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        equalTestTimeStart = time.time()
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.ITS.enumValue.enum == MyEnumTest()
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.ITS.enumValue.enum == MyEnumTest() assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.A.enumValue.enum == MyEnumTest()
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.A.enumValue.enum == MyEnumTest() assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        timeAssertInit = time.time()
        for _ in range(ASSERT_ITERATION) :
            assert MY_ENUM_TEST.TEST.enumValue.enum == MyEnumTest()
        discountStart = time.time()
        log.log(enum_withSuccess, f'MY_ENUM_TEST.TEST.enumValue.enum == MyEnumTest() assert duration: {time.time() - timeAssertInit}')
        discount += time.time() - discountStart
        assert MyEnumTest() == MyEnumTest()
        equalTestTime += (time.time() - equalTestTimeStart)

    # log.debug(enum_withSuccess, f'discount time: {discount}')
    # log.debug(enum_withSuccess, f'3 * equal evaluation time : {equalTestTime}')
    # log.debug(enum_withSuccess, f'instanciation time : {instanciationTime}')
    # log.debug(enum_withSuccess, f'test duration: {time.time() - start - equalTestTime - discount}')


# LOG_HELPER_SETTINGS = {
#     log.LOG : True,
#     log.SUCCESS : True,
#     log.SETTING : True,
#     log.DEBUG : True,
#     log.WARNING : True,
#     log.WRAPPER : True,
#     log.FAILURE : True,
#     log.ERROR : True,
#     log.TEST : True
# }
@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def otherEnum_withSuccess() :
    # arrange
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyOtherEnumTest :
        ONE = EnumItem(value=1)
        TWO = EnumItem(value=2)
        THREE = EnumItem(value=3)
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyThirdEnumTest :
        ONE = EnumItem(value=4)
        TWO = EnumItem(value=5)
        THREE = EnumItem(value=6)

    # act
    one = MyOtherEnumTest().ONE
    anotherOne = MyThirdEnumTest().ONE

    # assert
    assert one == 1
    assert anotherOne == 4
    assert MyOtherEnumTest() != MyThirdEnumTest()
    assert MyOtherEnumTest() == MyOtherEnumTest()
    assert MyOtherEnumTest().ONE == MyOtherEnumTest().ONE
    assert MyOtherEnumTest().TWO != MyOtherEnumTest().ONE
    assert 8 == MyOtherEnumTest().TWO + MyThirdEnumTest().THREE

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def python_framework_status() :
    # arrange
    # act
    # assert
    assert 200 == HttpStatus.OK
    assert 'UP' == ActuatorHealthStatus.UP

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def enumName() :
    # arrange
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyOtherEnumTest :
        ONE = EnumItem(value=1, otherValue='1')
        TWO = EnumItem(value=2, otherValue='1')
        THREE = EnumItem(value=3, otherValue='1')
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyThirdEnumTest :
        ONE = EnumItem(value=4, otherValue='1')
        TWO = EnumItem(value=5, otherValue='1')
        THREE = EnumItem(value=6, otherValue='1')
    ITS_NAME = RandomHelper.string(minimum=5, maximum=10)
    A_NAME = RandomHelper.string(minimum=5, maximum=10)
    TEST_NAME = RandomHelper.string(minimum=5, maximum=10)
    ITS_LABEL = RandomHelper.string(minimum=5, maximum=10)
    A_LABEL = RandomHelper.string(minimum=5, maximum=10)
    TEST_LABEL = RandomHelper.string(minimum=5, maximum=10)
    ITS_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
    A_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
    TEST_NUMERIC = RandomHelper.integer(minimum=5, maximum=1000)
    ITS_VALUE = 'ITS'
    A_VALUE = 'A'
    TEST_VALUE = 'TEST'
    @Enum()
    class MyEnumTest :
        ITS = EnumItem(name=ITS_NAME, label=ITS_LABEL, numeric=ITS_NUMERIC)
        A = EnumItem(name=A_NAME, label=A_LABEL, numeric=A_NUMERIC)
        TEST = EnumItem(name=TEST_NAME, label=TEST_LABEL, numeric=TEST_NUMERIC)
    MY_ENUM_TEST = MyEnumTest()

    # act
    enumType = MY_ENUM_TEST

    # assert
    assert 'OK' == HttpStatus.OK.enumName
    assert 'ONE' == MyOtherEnumTest().ONE.enumName
    assert 'ONE' == MyOtherEnumTest.ONE.enumName
    assert 1 == MyOtherEnumTest.ONE
    assert MyEnumTest.map(MY_ENUM_TEST.ITS.enumValue) == MY_ENUM_TEST.ITS
    assert MyEnumTest.map(MY_ENUM_TEST.ITS) == MY_ENUM_TEST.ITS
    assert MyOtherEnumTest.map(MyOtherEnumTest.ONE.enumValue) == MyOtherEnumTest.ONE
    assert MyOtherEnumTest.map(MyOtherEnumTest.ONE) == MyOtherEnumTest.ONE
    assert MyOtherEnumTest.map('ONE') == MyOtherEnumTest.ONE.enumValue
    assert MyOtherEnumTest.map('ONE') == MyOtherEnumTest.ONE
    assert MY_ENUM_TEST.map('TEST') == MyEnumTest.TEST.enumValue
    assert MY_ENUM_TEST.map('TEST') == MyEnumTest.TEST
    assert MyEnumTest == type(enumType)

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def enumName_badImplementation() :
    # arrange
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyOtherEnumTest :
        ONE = EnumItem(value='ONE', otherValue=1)
        TWO = EnumItem(value='TWO', otherValue=2)
    MY_OTHER_ENUM_TEST = MyOtherEnumTest()
    firstTestExteption = None
    secondTestExteption = None
    thirdTestExteption = None
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyThirdEnumTest :
        ONE = EnumItem(value='ONE', otherValue=1)

    # act
    try :
        @Enum(associateReturnsTo='value', instanceLog=False)
        class MyEnumTest :
            ONE = EnumItem(value='ONE', otherValue=1)
            TWO = EnumItem(value='ONE', otherValue=2)
        MyEnumTest()
    except Exception as e :
        firstTestExteption = e
    try:
        MY_OTHER_ENUM_TEST.map('another')
    except Exception as e :
        secondTestExteption = e
    try :
        '1' == MyThirdEnumTest.ONE
    except Exception as e :
        thirdTestExteption = e

    # assert
    # print(str(firstTestExteption))
    # print(str(secondTestExteption))
    assert '''Not possible to implement "ONE" enum value in MyEnumTest: ['ONE(value:ONE)'] enum''' == str(firstTestExteption)
    assert '''Not possible to retrieve "another" of type: <class 'str'> enum value from MyOtherEnumTest: ['ONE(value:ONE)', 'TWO(value:TWO)'] enum. Enum.__enumMap__ = {'ONE': 'ONE', 'TWO': 'TWO'}''' == str(secondTestExteption)
    assert "'EnumItem' object has no attribute 'enumValue'" == str(thirdTestExteption)

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def map_whenArgIsNone() :
    # arrange
    @Enum(associateReturnsTo='value', instanceLog=False)
    class MyOtherEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=2)
    MY_OTHER_ENUM_TEST = MyOtherEnumTest()
    @Enum(associateReturnsTo='otherValue', instanceLog=False)
    class MyThirdEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
    MY_THIRD_ENUM_TEST = MyThirdEnumTest()
    @Enum(instanceLog=False)
    class SimpleEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=1)
        THREE = EnumItem(value='three', otherValue=1)
    SIMPLE_ENUM_TEST = SimpleEnumTest()

    # act
    shouldBe_two_asString = MY_OTHER_ENUM_TEST.map('two')
    shouldBe_one_asInteger = MY_THIRD_ENUM_TEST.map(1)
    shouldBe_THREE_asString = SIMPLE_ENUM_TEST.map('THREE')

    # assert
    assert 'two' == shouldBe_two_asString
    assert 1 == shouldBe_one_asInteger
    assert 'THREE' == shouldBe_THREE_asString
    assert MY_OTHER_ENUM_TEST.map(None) is None
    assert MY_THIRD_ENUM_TEST.map(None) is None
    assert SIMPLE_ENUM_TEST.map(None) is None

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **LOG_HELPER_SETTINGS
    }
)
def Enum_whenHaveMoreThanOneInnerValue() :
    # arrange
    @Enum(instanceLog=False)
    class MyEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=2)
    @Enum(instanceLog=False)
    class MyOtherEnumTest :
        ONE = EnumItem(value=1, otherValue='one')
        TWO = EnumItem(value=2, otherValue='two')
    MY_ENUM_TEST = MyEnumTest()
    MY_OTHER_ENUM_TEST = MyOtherEnumTest()
    @Enum()
    class WeekDayEnumeration :
        MONDAY = EnumItem(index=0, short='mon')
        TUESDAY = EnumItem(index=1, short='tue')
        WEDNESDAY = EnumItem(index=2, short='wed')
        THURSDAY = EnumItem(index=3, short='thu')
        FRIDAY = EnumItem(index=4, short='fri')
        SATURDAY = EnumItem(index=5, short='sat')
        SUNDAY = EnumItem(index=6, short='sun')
    WeekDay = WeekDayEnumeration()

    # act
    value = MY_ENUM_TEST.ONE.value
    otherValue = MY_ENUM_TEST.TWO.otherValue
    other_value = MY_OTHER_ENUM_TEST.ONE.value
    other_otherValue = MY_OTHER_ENUM_TEST.TWO.otherValue
    fridayIndex = WeekDay.FRIDAY.index
    fridayShort = WeekDay.FRIDAY.short
    # from python_helper import ReflectionHelper
    # ReflectionHelper.getItNaked(MY_ENUM_TEST)
    # ReflectionHelper.getItNaked(MY_OTHER_ENUM_TEST)
    # ReflectionHelper.getItNaked(WeekDay)

    # assert
    assert 'one' == value
    assert 2 == otherValue
    assert 1 == other_value
    assert 'two' == other_otherValue
    assert 4 == fridayIndex
    assert 'fri' == fridayShort

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def Enum_dot_map() :
    # arrange
    @Enum(instanceLog=False)
    class SimpleEnum :
        ABC = EnumItem()
        DEF = EnumItem()
    SIMPLE_ENUM = SimpleEnum()
    @Enum(instanceLog=False)
    class MyEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=2)
    MY_ENUM_TEST = MyEnumTest()
    @Enum(associateReturnsTo='otherValue', instanceLog=False)
    class MyThirdEnumTest :
        THREE = EnumItem(value='three', otherValue=3)
        FOUR = EnumItem(value='four', otherValue=4)
    MY_THIRD_ENUM_TEST = MyThirdEnumTest()

    # act
    shouldBe_DEF = SIMPLE_ENUM.map('DEF')
    shouldBe_DEF_asWell = SIMPLE_ENUM.map(SIMPLE_ENUM.map('DEF'))
    shouldBe_None = SIMPLE_ENUM.map(None)

    # assert
    assert shouldBe_None is None
    assert shouldBe_DEF == SIMPLE_ENUM.DEF
    assert shouldBe_DEF is not {}
    assert not SIMPLE_ENUM.map('DEF') == SIMPLE_ENUM.map('ABC')
    assert not MY_ENUM_TEST.map('ONE') == MY_ENUM_TEST.map('TWO')
    assert shouldBe_DEF_asWell == SIMPLE_ENUM.DEF
    assert shouldBe_DEF_asWell is not {}
    assert ObjectHelper.isNotEmpty(shouldBe_DEF_asWell)

    assert MY_ENUM_TEST.map('ONE') == MY_ENUM_TEST.ONE
    assert not MY_ENUM_TEST.map('ONE') == MY_ENUM_TEST.TWO
    assert MY_ENUM_TEST.map('ONE') is not {}
    assert ObjectHelper.isNotEmpty(MY_ENUM_TEST.map('TWO'))

    assert MY_THIRD_ENUM_TEST.map(3) == MY_THIRD_ENUM_TEST.THREE
    assert not MY_THIRD_ENUM_TEST.map(4) == MY_THIRD_ENUM_TEST.THREE
    assert MY_THIRD_ENUM_TEST.map(4) is not {}
    assert ObjectHelper.isNotEmpty(MY_THIRD_ENUM_TEST.map(3))
    assert MY_THIRD_ENUM_TEST.map('THREE') == MY_THIRD_ENUM_TEST.THREE
    assert not MY_THIRD_ENUM_TEST.map('FOUR') == MY_THIRD_ENUM_TEST.THREE
    assert MY_THIRD_ENUM_TEST.map('FOUR') is not {}
    assert ObjectHelper.isNotEmpty(MY_THIRD_ENUM_TEST.map('THREE'))

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def Enum_str() :
    # arrange
    @Enum(instanceLog=False)
    class SimpleEnum :
        ABC = EnumItem()
        DEF = EnumItem()
    SIMPLE_ENUM = SimpleEnum()
    @Enum(instanceLog=False)
    class MyEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=2)
    MY_ENUM_TEST = MyEnumTest()
    @Enum(associateReturnsTo='otherValue', instanceLog=False)
    class MyThirdEnumTest :
        THREE = EnumItem(value='three', otherValue=3)
        FOUR = EnumItem(value='four', otherValue=4)
    MY_THIRD_ENUM_TEST = MyThirdEnumTest()

    # act
    shouldBe_DEF = SIMPLE_ENUM.map('DEF')
    shouldBe_DEF_asWell = SIMPLE_ENUM.map(SIMPLE_ENUM.map('DEF'))
    shouldBe_None = SIMPLE_ENUM.map(None)

    # act and assert
    assert 'DEF' == str(SIMPLE_ENUM.map('DEF'))
    assert 'DEF' == str(SIMPLE_ENUM.DEF)
    assert 'ABC' == str(SIMPLE_ENUM.map(SIMPLE_ENUM.map('ABC')))
    assert 'ABC' == str(SIMPLE_ENUM.map(SIMPLE_ENUM.ABC))
    assert 'None' == str(SIMPLE_ENUM.map(SIMPLE_ENUM.map(None)))
    assert shouldBe_DEF == shouldBe_DEF_asWell
    assert not shouldBe_DEF == shouldBe_None
    assert not shouldBe_None == shouldBe_DEF_asWell

    assert 'ONE' == str(MY_ENUM_TEST.ONE)
    assert 'TWO' == str(MY_ENUM_TEST.TWO)

    assert 3 == MY_THIRD_ENUM_TEST.THREE
    assert 4 == MY_THIRD_ENUM_TEST.FOUR
    assert 3 == MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.THREE)
    assert 4 == MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.FOUR))
    assert 3 == MY_THIRD_ENUM_TEST.map(3)
    assert 4 == MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map(4))
    assert 3 == MY_THIRD_ENUM_TEST.map('THREE')
    assert 4 == MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map('FOUR'))

    assert str(3) == str(MY_THIRD_ENUM_TEST.THREE)
    assert str(4) == str(MY_THIRD_ENUM_TEST.FOUR)
    assert str(3) == str(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.THREE))
    assert str(4) == str(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.FOUR)))
    assert str(3) == str(MY_THIRD_ENUM_TEST.map(3))
    assert str(4) == str(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map(4)))
    assert str(3) == str(MY_THIRD_ENUM_TEST.map('THREE'))
    assert str(4) == str(MY_THIRD_ENUM_TEST.map(MY_THIRD_ENUM_TEST.map('FOUR')))

@Test(environmentVariables={
        SettingHelper.ACTIVE_ENVIRONMENT : SettingHelper.LOCAL_ENVIRONMENT,
        **FULL_LOG_HELPER_SETTINGS
    }
)
def Enum_strInOutput() :
    # arrange
    @Enum(instanceLog=False)
    class SimpleEnum :
        ABC = EnumItem()
        DEF = EnumItem()
    SIMPLE_ENUM = SimpleEnum()
    @Enum(instanceLog=False)
    class MyEnumTest :
        ONE = EnumItem(value='one', otherValue=1)
        TWO = EnumItem(value='two', otherValue=2)
    MY_ENUM_TEST = MyEnumTest()
    @Enum(associateReturnsTo='otherValue', instanceLog=False)
    class MyThirdEnumTest :
        THREE = EnumItem(value='three', otherValue=3)
        FOUR = EnumItem(value='four', otherValue=4)
    MY_THIRD_ENUM_TEST = MyThirdEnumTest()

    # act and assert
    assert f'''{[SIMPLE_ENUM.map('DEF')]}''' == "['DEF']"
    assert str(type(SIMPLE_ENUM.map('DEF'))) == '''<class 'python_framework.api.src.annotation.EnumAnnotation.EnumItemStr'>'''
    assert f'''{[SIMPLE_ENUM.map(SIMPLE_ENUM.DEF)]}''' == "['DEF']"
    assert str(type(SIMPLE_ENUM.map(SIMPLE_ENUM.DEF))) == '''<class 'python_framework.api.src.annotation.EnumAnnotation.EnumItemStr'>'''
    a = [SIMPLE_ENUM.map('DEF')]
    b = [SIMPLE_ENUM.map(SIMPLE_ENUM.DEF)]
    assert f'''{a}''' == "['DEF']"
    assert str(type(a[0])) == '''<class 'python_framework.api.src.annotation.EnumAnnotation.EnumItemStr'>'''
    assert f'''{b}''' == "['DEF']"
    assert str(type(b[0])) == '''<class 'python_framework.api.src.annotation.EnumAnnotation.EnumItemStr'>'''

    print(MY_THIRD_ENUM_TEST)
    print(type(MY_THIRD_ENUM_TEST))
