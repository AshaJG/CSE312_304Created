import os


from router import Route
import database as db
from response import generate_response_redirect
from response import generate_response
from file_engine import send_response
from token_check_engine import check_token

def add_paths(router):
    router.add_route(Route('POST', '/feed_content', feed))
    router.add_route(Route("GET", "/image/.", images))


# Gets the image for image requested
def images(request, handler):
    data = request.path.split('/')
    # Search through images to find request on
    if os.path.exists("Pages/image/" + data[2]):
        send_response('Pages/image/' + data[2], b'image/jpeg', request, handler)
        return
    # Image request not found 404 Error
    response = generate_response('404\nCannot Find Page'.encode(),b'text/plain; charset=utf-8',b'404 Error')
    handler.request.sendall(response)


# Checks for auth-token and random token before allow user to upload to feed page
def feed(request, handler):
    username = request.cookies['username']
    if check_token(request.cookies["token"].encode(), request.form_content["auth_token"]):
        response = generate_response_redirect()
        handler.request.sendall(response)
        return
    if check_token(request.form_content["token"], handler.user_token_form[username].encode()):
        response = generate_response_redirect()
        handler.request.sendall(response)
        return
    post_id = "post_id_" + str(db.get_next_post_id())
    image = request.form_content["upload"]
    user_profile_picture = db.find_profileInfo(username)
    if not user_profile_picture:
        user_profile_picture = ""
    else:
        user_profile_picture = user_profile_picture['profile_pic']
    db.store_feed_content(username,save_image(image), request.form_content["comment"], post_id, user_profile_picture)
    response = generate_response_redirect()
    handler.request.sendall(response)


# Saves the image into the local server files
def save_image(image: bytes):
    image_file_name = ""
    if image != b'':
        image_id = db.get_next_image_id()
        image_file_name = "image" + str(image_id) + ".jpg"
        image_file = open("./Pages/image/" + image_file_name, "wb")
        image_file.write(image)
        image_file.close()
    return image_file_name
  