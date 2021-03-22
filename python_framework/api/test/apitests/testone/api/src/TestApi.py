from python_framework.api.src.service.flask import ResourceManager
import ModelAssociation

api, app, jwt = ResourceManager.initialize(
    __name__,
    ModelAssociation.Model
)
