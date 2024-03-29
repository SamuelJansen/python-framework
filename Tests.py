import importlib
importlib.invalidate_caches()
from python_helper import EnvironmentHelper, log, RandomHelper
EnvironmentHelper.update("URL_VARIANT", RandomHelper.integer(minimum=0, maximum=10000))
log.debug(log.debug, f'variant: {EnvironmentHelper.get("URL_VARIANT")}')

from python_helper import TestHelper
TestHelper.run(
    __file__,
    ignoreModules = [
        'TestApiTest'
    ]
)
# TestHelper.run(__file__)
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SerializerTest.getClassRole',
#         'SerializerTest.importResource',
#         'SerializerTest.convertFromObjectToObject',
#         'SerializerTest.convertFromObjectToObject_whenTargetClassIsList',
#         'SerializerTest.isModelTest',
#         'SerializerTest.isJsonifyable',
#         'SerializerTest.jsonifyIt',
#         'SerializerTest.fromDtoToModel',
#         'SerializerTest.fromModelToDto',
#         'SerializerTest.convertFromJsonToObject_whenThereAreEnums',
#         'SerializerTest.convertFromObjectToObject_weirdIdList',
#         'SerializerTest.convertFromJsonToObject_nativeClassAtributeList',
#         'SerializerTest.convertFromJsonToObject_listSpecialCase_whenNotFound',
#         'SerializerTest.convertFromJsonToObject_listSpecialCase_whenFoundButInvalid',
#         'SerializerTest.convertFromJsonToObject_listSpecialCase_whenFoundAndValid',
#         'SerializerTest.convertFromJsonToObject_listSpecialCase_whenFoundAndValidKeepingDataType'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SessionManagerTest.sessionManager_worksProperly',
#         'ApiKeyManagerTest.apiKeyManager_worksProperly',
#         'SecurityManagerTest.securityManager_worksProperly'
#     ]
# )
# TestHelper.run(
#     __file__,
#     # times=10,
#     runOnly = [
#         'TestApiTest.appRun_whenEnvironmentIsPrd_withSuccess',
#         # 'TestApiTest.appRun_whenEnvironmentIsLocalFromDevConfig_withSuccess',
#         # 'TestApiTest.appRun_whenEnvironmentIsLocalFromLocalConfig_withSuccess',
#         # 'TestApiTest.pythonRun_securityManager',
#         # # 'TestApiTest.pythonRun_apiKeyManager',
#         # # 'TestApiTest.pythonRun_sessionManager',
#         # 'TestApiTest.testing_headersAndParams',
#         # # ,
#         # 'TestApiTest.testing_Client'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'EnumAnnotationTest.Enum_comparing'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'GlobalExceptionAnnotationTest.encapsulateItWithGlobalException_withParameters_GlobalException'
#     ]
# )
# TestHelper.run(
#     __file__,
#     # logStatus = True,
#     # wrapperStatus = True,
#     runOnly = [
#         # 'EnumAnnotationTest.enum_withSuccess',
#         # 'EnumAnnotationTest.otherEnum_withSuccess',
#         # 'EnumAnnotationTest.python_framework_status',
#         # 'EnumAnnotationTest.enumName',
#         # 'EnumAnnotationTest.enumName_badImplementation',
#         # 'EnumAnnotationTest.map_whenArgIsNone',
#         # 'EnumAnnotationTest.Enum_whenHaveMoreThanOneInnerValue',
#         # 'EnumAnnotationTest.Enum_dot_map',
#         # 'EnumAnnotationTest.Enum_str',
#         # 'EnumAnnotationTest.Enum_strInOutput',
#         # 'EnumAnnotationTest.Enum_getItemsAsString'
#     ]
# )
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'SerializerTest.convertFromObjectToObject_whenTargetClassIsList',
#         'SerializerTest.isModelTest',
#         'SerializerTest.isJsonifyable',
#         'SerializerTest.jsonifyIt',
#         'SerializerTest.fromDtoToModel',
#         'SerializerTest.fromModelToDto',
#         'SerializerTest.convertFromJsonToObject_whenThereAreEnums',
#         'SerializerTest.convertFromObjectToObject_weirdIdList',
#         'SerializerTest.convertFromJsonToObject_nativeClassAtributeList'
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
