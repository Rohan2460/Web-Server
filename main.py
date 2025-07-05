from web_server.http_handler import HttpServer

def index(req):
    return server.html_response(req, "<h1>Hello</h1>")

urls = {
    "/" : index,
}

server = HttpServer(urls)
server.listen()
