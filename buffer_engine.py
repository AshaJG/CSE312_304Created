def buffer(content_length, handler):
    content = b''
    while len(content) != content_length:
        if content_length >= len(content)+1024:
            content += handler.request.recv(1024)
        else:
            content += handler.request.recv(content_length-len(content))
    return content