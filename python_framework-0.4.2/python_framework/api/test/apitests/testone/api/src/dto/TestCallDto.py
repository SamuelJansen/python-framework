import CallServiceName, CallType, CallStatus

class TestCallRequestDto:
    def __init__(self,
        hoster = None,
        beginAtDate = None,
        endAtDate = None,
        beginAtTime = None,
        endAtTime = None,
        note = None,
        service = None,
        type = None,
        status = None,
        url = None
    ):
        self.hoster = hoster
        self.beginAtDate = str(beginAtDate)
        self.endAtDate = str(endAtDate)
        self.beginAtTime = str(beginAtTime)
        self.endAtTime = str(endAtTime)
        self.note = note
        self.service = CallServiceName.CallServiceName.map(service)
        self.type = CallType.CallType.map(type)
        self.status = CallStatus.CallStatus.map(status)
        self.url = url

class TestCallResponseDto:
    def __init__(self,
        id = None,
        hoster = None,
        beginAtDate = None,
        endAtDate = None,
        beginAtTime = None,
        endAtTime = None,
        note = None,
        service = None,
        type = None,
        status = None,
        url = None
    ):
        self.id = id
        self.hoster = hoster
        self.beginAtDate = str(beginAtDate)
        self.endAtDate = str(endAtDate)
        self.beginAtTime = str(beginAtTime)
        self.endAtTime = str(endAtTime)
        self.note = note
        self.service = CallServiceName.CallServiceName.map(service)
        self.type = CallType.CallType.map(type)
        self.status = CallStatus.CallStatus.map(status)
        self.url = url
