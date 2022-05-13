import socketserver
import sys

import register_paths
import feed_paths
import home_path
from request import Request
from router import Router
from buffer_engine import buffer
from profile_paths import add_paths


class MyTCHandler(socketserver.BaseRequestHandler):

    user_token_form = {}

    # import route paths and add here using add_path(self.router)
    def __init__(self, request, client_address, server):
        self.router = Router()
        add_paths(self.router)
        register_paths.add_paths(self.router)
        feed_paths.add_paths(self.router)
        home_path.add_paths(self.router)
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        sys.stdout.flush()
        sys.stderr.flush()
        request = Request(received_data)
        if "Content-Length" in request.headers:
            received_data += buffer(int(request.headers["Content-Length"]) - len(request.body), self)
        request = Request(received_data)
        self.router.handle_request(request, self)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCHandler)
    server.serve_forever()
