from python_framework.api.src.enumeration.ActuatorHealthStatus import ActuatorHealthStatus

class EnumAsQueryRequestDto:
    def __init__(self,
        status = None
    ):
        self.status = ActuatorHealthStatus.map(status)
