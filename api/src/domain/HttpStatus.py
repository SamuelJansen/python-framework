###- 1×× Informational
CONTINUE = 100 ###- Continue
SWITCHING_PROTOCOLS = 101 ###- Switching Protocols
PROCESSING = 102 ###- Processing

###- 2×× Success
OK = 200 ###- OK
CREATED = 201 ###- Created
ACCEPTED = 202 ###- Accepted
NON_AUTHORATIVE_INFORMATION = 203 ###- Non-authoritative Information
NO_CONTENT = 204 ###- No Content
RESET_CONTENT = 205 ###- Reset Content
PARTIAL_CONTENT = 206 ###- Partial Content
MULTI_STATUS = 207 ###- Multi-Status
ALREADY_REPORTED = 208 ###- Already Reported
IM_USED = 226 ###- IM Used

###- 3×× Redirection
"""300 ###- Multiple Choices
301 ###- Moved Permanently
302 ###- Found
303 ###- See Other"""
NOT_MODIFIED = 304 ###- Not Modified
"""305 ###- Use Proxy
307 ###- Temporary Redirect
308 ###- Permanent Redirect"""

###- 4×× Client Error
BAD_REQUEST = 400 ###- Bad Request
UNAUTHORIZED = 401 ###- Unauthorized
REQUIRED = 402 ###- Payment Required
FORBIDEN = 403 ###- Forbidden
NOT_FOUND = 404 ###- Not Found
METHOD_NOT_ALLOWED = 405 ###- Method Not Allowed
"""406 ###- Not Acceptable
407 ###- Proxy Authentication Required
408 ###- Request Timeout
409 ###- Conflict
410 ###- Gone
411 ###- Length Required
412 ###- Precondition Failed
413 ###- Payload Too Large
414 ###- Request-URI Too Long
415 ###- Unsupported Media Type
416 ###- Requested Range Not Satisfiable
417 ###- Expectation Failed
418 ###- I'm a teapot
421 ###- Misdirected Request
422 ###- Unprocessable Entity
423 ###- Locked
424 ###- Failed Dependency
426 ###- Upgrade Required
428 ###- Precondition Required
429 ###- Too Many Requests
431 ###- Request Header Fields Too Large
444 ###- Connection Closed Without Response
451 ###- Unavailable For Legal Reasons
499 ###- Client Closed Request"""

###- 5×× Server Error
INTERNAL_SERVER_ERROR = 500 ###- Internal Server Error
NOT_IMPLEMENTED = 501 ###- Not Implemented
"""502 ###- Bad Gateway
503 ###- Service Unavailable
504 ###- Gateway Timeout
505 ###- HTTP Version Not Supported
506 ###- Variant Also Negotiates
507 ###- Insufficient Storage
508 ###- Loop Detected
510 ###- Not Extended
511 ###- Network Authentication Required
599 ###- Network Connect Timeout Error"""
