from python_framework.api.src.service.flask import ResourceManager
from python_framework.api.test.api.src.model import ModelAssociation

api, app, jwt = ResourceManager.initialize(
    __name__,
    ModelAssociation.Model,
    baseUrl = '',
    jwtSecret = 'put_some_os_enviroment_key_here',
    databaseEnvironmentVariable = 'DATABASE_URL'
)
