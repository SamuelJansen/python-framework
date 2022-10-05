class HeaderKey:
    CONTENT_TYPE = 'Content-Type'

class HeaderValue:
    APPLICATION_JSON = 'application/json'
    MULTIPART_X_MIXED_REPLACE = 'multipart/x-mixed-replace'
    TEXT_HTML = 'text/html; charset=UTF-8'
    TEXT_PLAIN = 'text/plain'
    FROM_DATA = 'multipart/form-data; boundary=value'
    AUDIO_WAV = 'audio/wav'
    AUDIO_MP3 = 'audio/mp3'
    DEFAULT_CONTENT_TYPE = APPLICATION_JSON


class Verb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'

CONTROLLER_CONTEXT = 'Controller'
CLIENT_CONTEXT = 'Client'
LISTENER_CONTEXT = 'Listener'
EMITTER_CONTEXT = 'Emitter'
SCHEDULER_CONTEXT = 'Scheduler'


REQUEST_HEADERS_KEY = 'requestHeaders'
RESPONSE_HEADERS_KEY = 'responseHeaders'
REQUEST_BODY_KEY = 'requestBody'
RESPONSE_BODY_KEY = 'responseBody'
