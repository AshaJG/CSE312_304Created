import os


from router import Route
import database as db
from response import generate_response_redirect
from response import generate_response
from file_engine import send_response

def add_paths(router):
    router.add_route(Route('POST', '/feed_content', feed))
    router.add_route(Route("GET", "/image/.", images))


def images(request, handler):
    data = request.path.split('/')
    # Search through images to find request on
    if os.path.exists("Pages/image/" + data[2]):
        send_response('Pages/image/' + data[2], b'image/jpeg', request, handler)
        return
    # Image request not found 404 Error
    response = generate_response('404\nCannot Find Page'.encode(),b'text/plain; charset=utf-8',b'404 Error')
    handler.request.sendall(response)



def feed(request, handler):
    auth_token = request.cookies["token"]
    feed_auth_token = request.form_content["auth_token"]
    if auth_token.encode() != feed_auth_token:
        print("token did not match")
        response = generate_response_redirect()
        handler.request.sendall(response)
        return
    feed_rand_token = request.form_content["token"]
    image = request.form_content["upload"]
    image_file_name = save_image(image)
    comment = request.form_content["comment"]
    db.store_feed_content(image_file_name, comment)
    response = generate_response_redirect()
    handler.request.sendall(response)



def save_image(image: bytes):
    image_file_name = ""
    if image != b'':
        image_id = db.get_next_image_id()
        image_file_name = "image" + str(image_id) + ".jpg"
        image_file = open("./Pages/image/" + image_file_name, "wb")
        image_file.write(image)
        image_file.close()
    return image_file_name
  