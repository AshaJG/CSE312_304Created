import os

import database
import formParser
from response import generate_Response200


def send_file(filename, mime_type, request, handler):
    with open(filename, "rb") as content:
        body = content.read()
        response = generate_Response200(body, mime_type, '200 OK')
        handler.request.sendall(response)


# responsible for generating the picture file
def write_incoming_picture():
    picture = formParser.actual_picture
    pic_no = database.get_next_id()
    image_fn = f'image{pic_no}'
    flag = os.path.exists(image_fn)
    if flag:
        pic_no = database.get_next_id()
        image_fn = f'image{pic_no}'
        filename = open(image_fn, "wb")
        filename.write(picture)
        filename.close()
    else:
        filename = open(image_fn, "wb")
        filename.write(picture)
        filename.close()

    return image_fn


# EDIT THIS FUNCTION WHEN LOGIN AND REGISTER COMES IN TO UPDATE USER INFO
def send_to_database():
    comment_dict = {}
    post_dict = {}
    comment = formParser.comment_after
    comment_key: str = comment.decode('utf-8')
    pic_filename = write_incoming_picture()
    # post_dict[comment_key] = pic_filename
    post_dict = {"comment": comment_key, "pic_filename": pic_filename}
    # print("image file in send to db and dict sent", pic_filename, post_dict, flush=True)
    database.create_post(post_dict)


