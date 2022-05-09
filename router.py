import re

from request import Request
from response import generate_response


class Router:

    def __init__(self):
        self.routes = []
        self.route_404 = Route('', '', Error)

    def add_route(self, route):
        self.routes.append(route)

    def handle_request(self, request: Request, handler):
        for route in self.routes:
            if route.is_request_match(request):
                route.handle_request(request, handler)
                return
        self.route_404.handle_request(request, handler)


class Route:

    def __init__(self, method, path, action):
        self.method = method
        self.path = path
        self.action = action

    def is_request_match(self, request: Request):
        if request.method != self.method:
            return False
        search_result = re.search(('^' + self.path), request.path)
        if search_result:
            return True
        else:
            return False

    def handle_request(self, request: Request, handler):
        self.action(request, handler)


def Error(request, handler, message: bytes = b'404\nPage Not Found'):
    response = generate_response(message, b'text/plain; charset=utf-8', b'404 NOT FOUND')
    handler.request.sendall(response)
