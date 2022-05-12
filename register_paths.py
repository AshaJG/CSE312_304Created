from sqlite3 import dbapi2
import bcrypt
import secrets

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
    username = request.form_content['username'].decode()
    hashed_password = bcrypt.hashpw(password, salt)
    db.store_user(username, hashed_password)
    handler.request.sendall(b'HTTP/1.1 301 Ok\r\nContent-Length: 0\r\nLocation: /\r\n\r\n')

# Logins in user when the correct password and username are inputed
# Creates a new Auth-token for everytime they log in
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

# Renders the login CSS
def loginCSS(request, handler):
    send_response('Pages/login.css', b'text/css; charset=utf-8', request, handler)

def homejs(request, handler):
    send_response('Pages/home.js', b'text/js; charset=utf-8', request, handler)

    




