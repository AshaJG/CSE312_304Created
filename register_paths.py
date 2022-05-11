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
    router.add_route(Route('GET', '/$', home))


def home(request, handler):
    # Veify that there is a token for the username
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
    # Renders the home page
    print(db.get_all_feed())
    content = render_template('Pages/home.html', {"loop_data": db.get_all_feed()})
    content = content.replace("{{Auth-Token}}", login_token.decode())
    token = secrets.token_urlsafe(20)
    content = content.replace("{{token}}", token)
    response = generate_response(content.encode(), b'text/html; charset=utf-8', b'200 OK', ["username","token"], [username, login_token.decode()])
    handler.request.sendall(response)
    

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

    
def redirct_to_login(request, handler):
    handler.request.sendall('HTTP/1.1 301 OK\r\nContent-Length: 0\r\nLocation: /login\r\n'.encode())



