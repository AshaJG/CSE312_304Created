from response import generate_response

# sends a response for a file
def send_response(filename, mime_type, request, handler):
    with open(filename, 'rb') as content:
        body = content.read()
        response = generate_response(body, mime_type)
        handler.request.sendall(response)