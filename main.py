from web_server.http_handler import HttpServer

def index(req):
    # return server.html_response(req, "<h1>Hello</h1>")
    if req.method == "POST":
        print(req.files["data"].data)

    return server.send_file(req, "testing/index.html")

urls = {
    "/" : index,
}

server = HttpServer(urls)
server.listen()
