class ClientTestRequestParamDto:
    def __init__(self,
        someParam = None
    ):
        self.someParam = someParam

class ClientTestRequestHeaderDto:
    def __init__(self,
        someHeader = None
    ):
        self.someHeader = someHeader


class ClientTestRequestDto:
    def __init__(self,
        someBody = None,
        someOtherBody = None
    ):
        self.someBody = someBody
        self.someOtherBody = someOtherBody


class ClientTestResponseDto:
    def __init__(self,
        someBody = None,
        someOtherBody = None
    ):
        self.someBody = someBody
        self.someOtherBody = someOtherBody
