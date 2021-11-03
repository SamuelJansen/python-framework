import importlib
importlib.invalidate_caches()
from python_helper import EnvironmentHelper, log, RandomHelper
EnvironmentHelper.update("URL_VARIANT", RandomHelper.integer(minimum=0, maximum=10000))
log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')

from python_helper import TestHelper
# TestHelper.run(__file__)
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'EnumAnnotationTest.Enum_comparing'
#     ]
# )
TestHelper.run(
    __file__,
    runOnly = [
        'GlobalExceptionAnnotationTest.encapsulateItWithGlobalException_withParameters_GlobalException'
    ]
)
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'TestApiTest.pythonRun_securityManager'
#         # 'TestApiTest.testing_Client'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'EnumAnnotationTest.enum_withSuccess',
#         'EnumAnnotationTest.otherEnum_withSuccess',
#         'EnumAnnotationTest.python_framework_status',
#         'EnumAnnotationTest.enumName',
#         'EnumAnnotationTest.enumName_badImplementation',
#         'EnumAnnotationTest.map_whenArgIsNone',
#         'EnumAnnotationTest.Enum_whenHaveMoreThanOneInnerValue',
#         'EnumAnnotationTest.Enum_dot_map',
#         'EnumAnnotationTest.Enum_str',
#         'EnumAnnotationTest.Enum_strInOutput'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SerializerTest.convertFromObjectToObject_whenTargetClassIsList',
#         'SerializerTest.isModelTest',
#         'SerializerTest.isJsonifyable',
#         'SerializerTest.jsonifyIt',
#         'SerializerTest.weirdIdList'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SerializerTest.fromModelToDto',
#         'SerializerTest.fromDtoToModel'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SerializerTest.convertFromJsonToObject_whenThereAreEnums'
#     ]
# )

log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')
