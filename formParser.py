edit_sequence = ""
comment_after = ""
actual_picture = b''
final_token = ""
username = ""


# content_length = Request.headers.get('Content-Length')

# function gets the boundary in the multi-part form
def get_bodyBoundary(headers):
    global edit_sequence
    boundary = "boundary="
    contentType_value = headers.get("Content-Type")
    # print("Content - Type", contentType_value, flush=True)
    if contentType_value is not None:
        body_sequence = contentType_value
        find_sequence = contentType_value.find(boundary)
        common_sequence = body_sequence[(find_sequence + len(boundary)):]
        stripped_sequence = common_sequence.strip()
        edit_sequence = "--" + stripped_sequence
        print("edit_sequence", edit_sequence, flush=True)
    else:
        edit_sequence = None
    # print("boundary", boundary, flush=True)
    return edit_sequence


# function separate the body into username, random info and picture
def separate_body(body: bytes):
    boundary = edit_sequence.encode()
    print("boundary in separate_body", boundary, flush=True)
    # sequence = boundary.encode()
    # content = body
    # print("body in separate_body", body, flush=True)
    split_body = body.split(boundary)
    # print("split body", split_body, flush=True)
    remove_empty_string = split_body.pop(0)
    username = get_username(split_body[0])
    comment = get_comment(split_body[1])
    picture = get_picture(split_body[2])
    # send_to_database()
    print("the username parsed : ", username, flush=True)
    print("the comment parsed : ", comment, flush=True)
    print("the pic parsed : ", picture, flush=True)
    return [username, comment, picture, ]
    # return [comment, picture, token]


def get_username(split_body):
    global username
    content = split_body
    stripped = content.strip()
    user_start = content.find(b'\r\n\r\n')
    user_name = stripped[user_start:]
    user_end = user_name.find(b'\r\n')
    user_actual = [(user_end + len(b'r\n'))]
    sanitized_user = escape_html(str(user_actual))
    username_edit = sanitized_user.encode()
    return username_edit


# this function literally slices out the comment out of the body and also perform sanitization
def get_comment(split_body):
    global comment_after
    content = split_body
    strip_content = content.strip()
    comment_start = content.find(b'\r\n\r\n')
    actual_comment = strip_content[comment_start:]
    space = actual_comment.find(b'\r\n')
    final_comment = actual_comment[(space + len(b'\r\n')):]
    sanitized_comment = escape_html(str(final_comment))
    comment_after = sanitized_comment.encode()
    # print("actual_comment", comment_after, flush=True)
    return comment_after


# this function parses out the picture and store it as an array of bytes i think..
def get_picture(split_body):
    global actual_picture
    content = split_body
    picture_start = content.find(b'\r\n\r\n')
    actual_picture = content[(picture_start + len(b'\r\n\r\n')):]
    # print("actual_picture", actual_picture, flush=True)
    return actual_picture


# implemented for security in html injections
def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
