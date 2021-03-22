from python_helper import Test
from python_framework.api.src.service.flask import FlaskManager

@Test()
def KW_RESOURCE_LIST_isInCorrectOrder() :
    # arrange
    resourceNameCorrectOrder = [
        FlaskManager.KW_CONTROLLER_RESOURCE,
        FlaskManager.KW_SERVICE_RESOURCE,
        FlaskManager.KW_CLIENT_RESOURCE,
        FlaskManager.KW_REPOSITORY_RESOURCE,
        FlaskManager.KW_VALIDATOR_RESOURCE,
        FlaskManager.KW_MAPPER_RESOURCE,
        FlaskManager.KW_HELPER_RESOURCE,
        FlaskManager.KW_CONVERTER_RESOURCE
    ]

    # act

    # assert
    assert len(resourceNameCorrectOrder) == len(FlaskManager.KW_RESOURCE_LIST)
    for index, resourceName in enumerate(resourceNameCorrectOrder) :
        assert resourceName == FlaskManager.KW_RESOURCE_LIST[index]
