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
            raw_request += conn.recv(256)

        raw_request = raw_request.decode()
        index1 = raw_request.index(" ")
        index_body_start = raw_request.index("\r\n\r\n")

        request.method = HttpMethod[raw_request[:index1]]
        request.url = raw_request[index1 + 1: raw_request.index(" ", index1 + 1)]

        for line in raw_request.split("\n"):
            if line.startswith("Content-Length"):
                index = line.index("Content-Length") + len("Content-Length: ") 
                headers["content_length"] = int(line[index:])

        if request.method == "POST":
            extra_size = len(raw_request) - len(raw_request[:index_body_start])
            remaining_size =  headers["content_length"] - extra_size
            data = raw_request[:index_body_start].encode() + conn.recv(remaining_size)
            request.body = data

        request.headers = headers
        return request


    def send_file(self, conn):
        with open("index.html", "r") as fp:
            res = fp.read()
            header = "HTTP/1.1 200 OK\n" \
            "Content-Type: text/html; charset=utf-8\n" \
            "Content-Length: {}\n\n".format(len(res))

            res = header + res
            conn.send(res.encode())


    def html_response(self, req: HttpRequest, text:str = ""):
        return HttpResponse(HttpStatus.OK, ContentTypes.HTML, text, req.method)

    def log_request(self, method, status, url, addr):
        print(f"[{status}] {addr[0]} {method.value} {url}")
    

    def listen(self, ip = '0.0.0.0', port = 8080):
        server = SocketServer(self, (ip, port))
        server.listen()
