from python_helper import TestHelper
# TestHelper.run(__file__)
# TestHelper.run(
#     __file__,
#     runOnly = [
#         'EnumAnnotationTest.enum_withSuccess',
#         'EnumAnnotationTest.otherEnum_withSuccess',
#         'EnumAnnotationTest.python_framework_status'
#     ]
# )
TestHelper.run(
    __file__,
    runOnly = [
        'TestApiTest.appRun_withSuccess'
    ]
)
# SerializerTest.Serializer_isModelTest()
# SerializerTest.Serializer_isJsonifyable()
# SerializerTest.Serializer_jsonifyIt()

# EnumAnnotationTest.enum_withSuccess()

# from python_framework.api.test import app
# app.runFlaskApplication(app.app)
