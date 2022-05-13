def escape_HTML(content: bytes):
    content = content.replace(b'&', b'&amp;')
    content = content.replace(b'>', b'&gt;')
    content = content.replace(b'<', b'&lt;')
    return content.decode()