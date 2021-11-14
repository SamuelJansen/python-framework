class TestRequestParamDto:
    def __init__(self,
        first = None,
        second = None
    ):
        self.first = first
        self.second = second


class TestRequestHeaderDto:
    def __init__(self,
        firstHeader = None,
        secondHeader = None
    ):
        self.firstHeader = firstHeader
        self.secondHeader = secondHeader


class TestResponseDto:
    def __init__(self,
        status = None,
        first = None,
        second = None,
        firstHeader = None,
        secondHeader = None
    ):
        self.status = status
        self.first = first
        self.second = second
        self.firstHeader = firstHeader
        self.secondHeader = secondHeader
