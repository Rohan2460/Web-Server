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
                headers["content_length"] = int(value.strip())

        request.headers = headers

        if request.method == "POST":
            body = body_part
            content_length = headers.get("content_length", 0)

            while len(body) < content_length:
                part = conn.recv(content_length - len(body)) 
                if not part:
                    break
                body += part

            request.body = body

        return request


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
