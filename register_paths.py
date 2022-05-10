from sqlite3 import dbapi2
import bcrypt
import secrets

from response import generate_response, generate_response_redirect
from router import Route
import database as db


def add_paths(router):
    router.add_route(Route('GET', '/login$', loginPage))
    router.add_route(Route('POST', '/login$', login))
    router.add_route(Route('POST', '/register$', register))
    router.add_route(Route('GET', '/register$', registerPage))
    router.add_route(Route('GET', '/login.css$', loginCSS))
    router.add_route(Route('GET', '/$', home))


def home(request, handler):
    if not 'username' in request.cookies:
        redirct_to_login(request, handler)
        return
    username = request.cookies['username']
    login_token = request.cookies['token'].encode('utf-8')
    # db_token = db.get_token_by_username(username)[0][username]
    record = db.get_token_by_username(username)
    db_token = record.get('auth_token')
    if not bcrypt.checkpw(login_token, db_token.encode('utf-8')):
        redirct_to_login(request, handler)
        return
    send_response('Pages/home.html', b'text/html; charset=utf-8', request, handler)


def registerPage(request, handler):
    send_response('Pages/signup.html', b'text/html; charset=utf-8', request, handler)


def loginPage(request, handler):
    send_response('Pages/login.html', b'text/html; charset=utf-8', request, handler)


def register(request, handler):
    salt = bcrypt.gensalt()
    password = request.form_content['password'].decode().encode("utf-8")
    username = request.form_content['username'].decode()
    hashed_password = bcrypt.hashpw(password, salt)
    db.store_user(username, hashed_password)
    handler.request.sendall(b'HTTP/1.1 301 Ok\r\nContent-Length: 0\r\nLocation: /\r\n\r\n')


def login(request, handler):
    username = request.form_content['username'].decode()
    password = request.form_content['password'].decode()
    user = db.get_user_by_username(username)
    if user:
        hashed_password = user["password"]
        password = password.encode("utf-8")
        if bcrypt.checkpw(password, hashed_password):
            token = secrets.token_urlsafe(20)
            response = generate_response_redirect(["token", "username"], [token, username])
            salt = bcrypt.gensalt()
            token = bcrypt.hashpw(token.encode("utf-8"), salt)
            db.store_user_token(username, token.decode())

            handler.request.sendall(response)
        else:
            handler.request.sendall(generate_response_redirect())
            print("no match")
    else:
        handler.request.sendall(generate_response_redirect())
        print("user not found")


def loginCSS(request, handler):
    send_response('Pages/login.css', b'text/css; charset=utf-8', request, handler)


def redirct_to_login(request, handler):
    handler.request.sendall('HTTP/1.1 301 OK\r\nContent-Length: 0\r\nLocation: /login\r\n'.encode())


def send_response(filename, mime_type, request, handler):
    with open(filename, 'rb') as content:
        body = content.read()
        response = generate_response(body, mime_type)
        handler.request.sendall(response)
