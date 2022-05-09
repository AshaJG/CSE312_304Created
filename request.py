# from formParser import get_bodyBoundary


class Request:
    new_line = b'\r\n'
    boundary_line = b'\r\n\r\n'

    def __init__(self, request: bytes):
        [request_line, header_as_bytes, self.body] = split_request(request)
        [self.method, self.path, self.http] = parse_request_line(request_line)
        self.headers = parse_headers(header_as_bytes)
        self.cookies = parse_cookies(self.headers)
        self.boundary = parse_boundary(self.headers)
        self.form_content = parse_form(self.body, self.boundary)
        # self.profile_boundary = get_bodyBoundary(self.headers)


def split_request(request: bytes):
    new_line_boundary = request.find(Request.new_line)
    boundary_line = request.find(Request.boundary_line)

    request_line = request[:new_line_boundary]
    header_as_bytes = request[(new_line_boundary + len(Request.new_line)):boundary_line]
    body = request[(boundary_line + len(Request.boundary_line)):]

    return [request_line, header_as_bytes, body]


def parse_request_line(request_line: bytes):
    return request_line.decode().split(" ")


# Parses the headers into a dictionary
def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.decode().split(Request.new_line.decode())
    for line in lines_as_str:
        splits = line.split(':')
        headers[splits[0].strip()] = splits[1].strip()
    return headers


# If there is a bounadry then it will compute the boundary and return it in bytes
def parse_boundary(headers):
    if "Content-Type" in headers:
        content_type = headers["Content-Type"]
        boundary = content_type.split('boundary=')[1]
        boundary = "--" + boundary
        return boundary.encode()
    return b''


def parse_cookies(headers):
    cookie_dic = {}
    if "Cookie" in headers:
        cookies = headers["Cookie"].split(";")
        for cookie in cookies:
            cookie = cookie.split("=")
            cookie_dic[cookie[0].strip()] = cookie[1].strip()
        return cookie_dic
    return cookie_dic


def parse_form(body, boundary):
    form_dic = {}
    if boundary != b'' and body != b'':
        content = body.split(boundary)
        content.pop(0)
        content.pop(len(content) - 1)
        for idx in range(len(content)):
            idx_equal = content[idx].find(b'=') + 2
            content[idx] = content[idx][idx_equal:]
            body_boundary_line =  content[idx].find(b'\r\n\r\n')
            body_new_line = content[idx].rfind(b'\r\n')
            name_of_body = content[idx][:body_boundary_line]
            name_of_body = name_of_body[:name_of_body.find(b";")]
            name_of_body = name_of_body.strip(b'"').decode()
            form_body = content[idx][body_boundary_line+ len(b'\r\n\r\n'):body_new_line]
            form_dic[name_of_body] = form_body
    return form_dic
