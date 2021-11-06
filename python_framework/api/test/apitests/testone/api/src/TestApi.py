from python_framework.api.src.service.flask import ResourceManager
import ModelAssociation

app = ResourceManager.initialize(
    __name__,
    ModelAssociation.Model
)
