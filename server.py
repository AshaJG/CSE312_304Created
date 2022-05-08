import socketserver
import sys

import formParser
from request import Request
from router import Router
# from register_paths import add_paths as path_register
# from buffer_engine import buffer
from static_paths import add_paths


class MyTCHandler(socketserver.BaseRequestHandler):

    # import route paths and add here using add_path(self.router)
    def __init__(self, request, client_address, server):
        self.router = Router()
        add_paths(self.router)
        # path_register(self.router)
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(1048)
        if len(received_data) == 0:
            return
        print("------received data---------------")
        print(received_data, flush=True)
        print("----------ending------------------\n\n")
        sys.stdout.flush()
        sys.stderr.flush()
        request = Request(received_data)

        # implementing the buffer
        content_length = request.headers.get('Content-Length')
        buffer = request.body
        if content_length is not None:
            content_length_int = int(content_length)
            buffer_count = len(request.body)
            amt_left = content_length_int - buffer_count

            while buffer_count < content_length_int:
                # print("content_length_int in loop", content_length_int, "buffer_count in loop", buffer_count,flush=True)
                received_data = self.request.recv(4096)
                buffer += received_data
                buffer_count = len(buffer)
                amt_left = content_length_int - buffer_count
                # print("amount left in the loop", amt_left, "buffer_count in loop", buffer_count,flush=True)
            else:
                remaining = content_length_int - buffer_count
                # print("last amt remaining", remaining, flush=True)
                received_data_left = self.request.recv(remaining)
                buffer += received_data_left
            request.body = buffer
            formParser.separate_body(buffer)
            # print("the length", len(buffer), flush=True)
            # print("the buffer", buffer, flush=True)
            # print ("the request body length", len(request.body), flush=True)


        # if "Content-Length" in request.headers:
        #     print("in here the content length", request.headers["Content-Length"], flush=True)
        #     received_data += buffer(int(request.headers["Content-Length"])-len(request.body), self)
        #     # print("the received data", received_data, len(received_data),flush=True)
        # request = Request(received_data)

        self.router.handle_request(request, self)


if __name__ == "__main__":
    HOST, PORT =  "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCHandler)
    server.serve_forever()