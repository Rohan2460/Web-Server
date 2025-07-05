from enum import Enum


class HttpMethod(str, Enum):
    GET  = "GET"
    POST = "POST"


class HttpStatus(Enum):
    OK   = 200
    Internal_Server_Error  = 500
    Not_Found = 404


class ContentTypes(str, Enum):
    HTML = "text/html"
    PLAIN = "text/plain"


class HttpRequest:
    method = HttpMethod
    url = ""
    headers = {}
    body = ""
    address = None


class HttpResponse:
    response = ""
    status_code = HttpStatus
    content_type = ContentTypes
    body = b""
    request_method = HttpMethod
    
    #TODO: replace with property funtion
    def __init__(self, status: HttpStatus = None, content_type: ContentTypes = None, body: str = "", request_method: HttpMethod = None):
        self.request_method = request_method
        self.content_type = content_type
        self.status_code = status
        self.body = body
        template = "HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\n\r\n{body}"

        self.response = template.format(
            status = f"{self.status_code.value} {status.name.replace("_", " ")}", 
            ctype = self.content_type.value,
            body = self.body).encode()
        
    def __str__(self):
        return self.response

    