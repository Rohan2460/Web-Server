import socket


class SocketServer:
    addr = ()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_server = None

    def __init__(self, http_instance, addr: tuple):
        self.web_server = http_instance 
        self.addr = addr
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.bind(self.addr)
        self.server.listen()

    def listen(self):
        quit = False
        try:
            while(True):
                # try:
                    conn, addr = self.server.accept()
                    req = self.web_server.parse_request(conn, addr)
                    self.web_server.dispatch(req)

                # except Exception as e:
                #     print(e)
                #     quit = True
                    
                # finally:
                    conn.close()
                    if quit: break

        except KeyboardInterrupt:
            print("\nExiting...")

        finally:
            self.server.close()
