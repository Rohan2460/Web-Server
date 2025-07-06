from pprint import pprint
import re
import socket
from .models import *
from web_server.socket_handler import SocketServer


class HttpServer:
    urls = {}
    conn = None

    def __init__(self, urls):
        self.urls = urls

    def dispatch(self, req):
        status_code = 200
        try:
            res = self.urls[req.url](req)
            self.conn.send(res.response)
        except KeyError:
            self.conn.send(self.html_response(req, "Not found").response)
            status_code = 404
        finally:
            self.log_request(req.method, status_code, req.url, req.address)

    def parse_request(self, conn: socket.socket, addr) -> HttpRequest:
        self.conn = conn
        raw_request = b''
        headers = {}
        request = HttpRequest()
        request.address = addr

        while b'\r\n\r\n' not in raw_request:
            part = conn.recv(256)
            if not part:
                break
            raw_request += part 

        header_part, _, body_part = raw_request.partition(b"\r\n\r\n")
        header_str = header_part.decode()

        lines = header_str.split("\r\n")
        request_line = lines[0]
        method, url, _ = request_line.split(" ")
        request.method = HttpMethod[method]
        request.url = url

        for line in lines[1:]:
            line = line.lower()

            if line.startswith("content-length"):
                key, value = line.split(":")
                headers["content-length"] = int(value.strip())
            else:
                key, value = line.split(": ")
                headers[key.lower()] = value.strip()
        
        request.headers = headers

        if request.method == "POST":
            content_length = headers.get("content-length", 0)
            request.body = self.parse_body(conn, content_length, body_part)

            content_type = headers.get("content-type", 0)
            if content_type == "application/x-www-form-urlencoded":
                request.form_data = self.parse_form(request.body)

            elif content_type.startswith("multipart/form-data"):
                request.files = self.parse_files(request.body, content_type)

        return request
    
    def parse_body(self, conn, content_length, body):
        while len(body) < content_length:
            part = conn.recv(content_length - len(body)) 
            if not part:
                break
            body += part

        return body
    
    def parse_form(self, body):
        form_data = {}
        body = body.decode()
        for data in body.split("&"):
            key, value = data.split("=")
            form_data[key] = value

        return form_data
    
    def parse_files(self, body, content_type):
        files = {}
        body = body.decode()
        ctype, boundary = content_type.split("; boundary=")
        body = body.split("--" + boundary)
        body.pop()
        
        for file in body:
            if not file:
                continue
            
            file = file.strip("\r\n")
            header, data = file.split("\r\n\r\n")

            filename = re.search(r'filename="([^"]+)"', header).group(1)
            name_id = re.search(r'name="([^"]+)"', header).group(1)

            files[name_id] = UploadedFile(filename, data.encode())

        return files

    def send_file(self, req, file):
        with open(file, "r") as fp:
            res = fp.read()
            return self.html_response(req, res)

    def html_response(self, req: HttpRequest, text:str = ""):
        return HttpResponse(HttpStatus.OK, ContentTypes.HTML, text, req.method)

    def log_request(self, method, status, url, addr):
        print(f"[{status}] {addr[0]} {method.value} {url}")

    def listen(self, ip = '0.0.0.0', port = 8080):
        server = SocketServer(self, (ip, port))
        server.listen()
