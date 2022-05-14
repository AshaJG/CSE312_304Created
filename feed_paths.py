import os
import sys
import bcrypt



from router import Route
import database as db
from response import generate_Response200, generate_response_redirect
from response import generate_response
from file_engine import send_response
from template_engine import render_template
from token_check_engine import check_token

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

#goes to the dm menu
def dmMenu(request, handler):
    if not 'username' in request.cookies:
        redirct_to_login(request, handler)
        return
    username = request.cookies['username']
    login_token = request.cookies['token'].encode('utf-8')
    record = db.get_token_by_username(username)
    db_token = record.get('auth_token')
    if not bcrypt.checkpw(login_token, db_token.encode('utf-8')):
        redirct_to_login(request, handler)
        return
    user = request.cookies["username"]
    users = {}
    users = db.find_all_dms(user)
    if users == "none":
        users = [{"user": ""}]
    #for person
    body = render_template('Pages/dmMenu.html', {"loop_data":users})
    response = generate_response(body.encode(), b'text/html; charset=utf-8', b'200 OK')
    handler.request.sendall(response)

def newdm(request, handler):
    todm = request.form_content["username"].decode()
    user = request.cookies["username"]
    exsits = db.get_user_by_username(todm)
    if(exsits == None):
        response = generate_response_redirect(location="/dmMenu")
        handler.request.sendall(response)
    else:
        record = db.add_dm(user, todm)
        if(record == "already exsists"):
            path = "/userdm/"+todm
            response = generate_response_redirect(location=path)
            handler.request.sendall(response)
        response = generate_response_redirect(location="/dmMenu")
        handler.request.sendall(response)

def indm(request, handler):
    if not 'username' in request.cookies:
        redirct_to_login(request, handler)
        return
    username = request.cookies['username']
    login_token = request.cookies['token'].encode('utf-8')
    record = db.get_token_by_username(username)
    db_token = record.get('auth_token')
    if not bcrypt.checkpw(login_token, db_token.encode('utf-8')):
        redirct_to_login(request, handler)
        return
    requestpath = request.path
    whole = requestpath.split('/')
    reciever = whole[2]
    sender = request.cookies["username"]
    messages = db.get_dm(sender, reciever)
    body = render_template('Pages/dm.html', {"person":reciever,"loop_data": messages})
    response = generate_response(body.encode(), content_type=b'text/html; charset=utf-8')
    handler.request.sendall(response)

def senddm(request, handler):
    sys.stdout.flush()
    reciever = request.form_content["rec"].decode()
    content = request.form_content["dmcomment"].decode()
    take2 = content.replace("&", "&amp;")
    take3 = take2.replace("<", "&lt;")
    content = take3.replace("<", "&gt;")
    sender = request.cookies["username"]
    message = {'user': sender, 'message': content}
    record = db.add_dm_message(sender, reciever, message)
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



def redirct_to_login(request, handler):
    handler.request.sendall('HTTP/1.1 301 OK\r\nContent-Length: 0\r\nLocation: /login\r\n'.encode())
  