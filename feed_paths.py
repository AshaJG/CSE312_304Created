import os
from re import template
from reprlib import recursive_repr
import sys
from urllib import response


from router import Route
import database as db
from response import generate_Response200, generate_response_redirect
from response import generate_response
from file_engine import send_response
from template_engine import render_template

def add_paths(router):
    router.add_route(Route('POST', '/feed_content', feed))
    router.add_route(Route("GET", "/image/.", images))
    router.add_route(Route('GET', '/dmMenu', dmMenu))
    router.add_route(Route('POST', '/newdm', newdm))
    router.add_route(Route('GET', '/userdm/.', indm))
    router.add_route(Route('POST', '/senddm', senddm))


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

#goes to the dm menu
def dmMenu(request, handler):
    user = request.cookies["username"]
    print("finding all dms for " + user)
    users = {}
    users = db.find_all_dms(user)
    print("found all dms")
    sys.stdout.flush()
    print(users)
    sys.stdout.flush()
    if users == "none":
        users = [{"user": ""}]
    #for person
    body = render_template('Pages/dmMenu.html', {"loop_data":users})
    print("out of gen template")
    sys.stdout.flush()
    #print(body)
    sys.stdout.flush()
    response = generate_response(body.encode(), b'text/html; charset=utf-8', b'200 OK')
    handler.request.sendall(response)

def newdm(request, handler):
    todm = request.form_content["username"].decode()
    print("to dm")
    sys.stdout.flush()
    user = request.cookies["username"]
    print(todm)
    sys.stdout.flush()
    exsits = db.get_user_by_username(todm)
    print(exsits)
    sys.stdout.flush()
    if(exsits == None):
        print("no user exsists")
        response = generate_response_redirect(location="/dmMenu")
        handler.request.sendall(response)
    else:
        print("user exsists, adding dm")
        sys.stdout.flush()
        record = db.add_dm(user, todm)
        print(record)
        if(record == "already exsists"):
            path = "/userdm/"+todm
            response = generate_response_redirect(location=path)
            handler.request.sendall(response)
        sys.stdout.flush()
        response = generate_response_redirect(location="/dmMenu")
        handler.request.sendall(response)

def indm(request, handler):
    print("in my special in dm fucntin")
    sys.stdout.flush()
    requestpath = request.path
    whole = requestpath.split('/')
    reciever = whole[2]
    print(reciever)
    sys.stdout.flush()
    sender = request.cookies["username"]
    messages = db.get_dm(sender, reciever)
    print(messages)
    sys.stdout.flush()
    body = render_template('Pages/dm.html', {"person":reciever,"loop_data": messages})
    response = generate_response(body.encode(), content_type=b'text/html; charset=utf-8')
    handler.request.sendall(response)

def senddm(request, handler):
    print("sending dm")
    sys.stdout.flush()
    reciever = request.form_content["rec"].decode()
    content = request.form_content["dmcomment"].decode()
    take2 = content.replace("&", "&amp;")
    take3 = take2.replace("<", "&lt;")
    content = take3.replace("<", "&gt;")
    sender = request.cookies["username"]
    message = {'user': sender, 'message': content}
    record = db.add_dm_message(sender, reciever, message)
    print(record)
    sys.stdout.flush()
    path = '/userdm/'+reciever
    response = generate_response_redirect(location=path)
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
  