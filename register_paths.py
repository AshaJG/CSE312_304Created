import bcrypt
import secrets
import re

from response import generate_response, generate_response_redirect
from file_engine import send_response
from template_engine import *
from router import Route
import database as db


def add_paths(router):
    router.add_route(Route('GET', '/login$', loginPage))
    router.add_route(Route('POST', '/login$', login))
    router.add_route(Route('POST', '/register$', register))
    router.add_route(Route('GET', '/register$', registerPage))
    router.add_route(Route('GET', '/login.css$', loginCSS))
    router.add_route(Route('GET', '/home.js', homejs))
    router.add_route(Route('GET', '/signup.js', registerjs))


# Renders the Register Page
def registerPage(request, handler):
    send_response('Pages/signup.html', b'text/html; charset=utf-8', request, handler)


# Renders the Login Page
def loginPage(request, handler):
    send_response('Pages/login.html', b'text/html; charset=utf-8', request, handler)


# Store user in the database when they sign up
def register(request, handler):
    salt = bcrypt.gensalt()
    password = request.form_content['password'].decode().encode("utf-8")
    username = request.form_content['username'].decode().replace(" ", "")
    if '/' in username or "\\" in username:
        handler.request.sendall(b'HTTP/1.1 301 Ok\r\nContent-Length: 0\r\nLocation: /registerUsernameError\r\n\r\n')
        return
    hashed_password = bcrypt.hashpw(password, salt)
    db.store_user(username, hashed_password)
    handler.request.sendall(b'HTTP/1.1 301 Ok\r\nContent-Length: 0\r\nLocation: /\r\n\r\n')


# Logins in user when the correct password and username are inputed
# Creates a new Auth-token for everytime they log in
def login(request, handler):
    username = request.form_content['username'].decode().replace(" ", "")
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
    else:
        handler.request.sendall(generate_response_redirect())


# Renders the login CSS
def loginCSS(request, handler):
    send_response('Pages/login.css', b'text/css; charset=utf-8', request, handler)

def homejs(request, handler):
    send_response('Pages/home.js', b'text/javascript; charset=utf-8', request, handler)

def registerjs(request, handler):
    send_response('Pages/signup.js', b'text/javascript; charset=utf-8', request, handler)