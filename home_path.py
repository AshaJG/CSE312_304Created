import secrets
import bcrypt



from router import Route
from response import generate_response
from template_engine import render_template
from file_engine import send_response
import database as db



def add_paths(router):
    router.add_route(Route('GET', '/$', home))
    router.add_route(Route('GET', '/home.css', homeCSS))

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
    content = render_template('Pages/home.html', {"loop_data": db.get_all_feed()})
    content = content.replace("{{Auth-Token}}", login_token.decode())
    token = secrets.token_urlsafe(20)
    content = content.replace("{{token}}", token)
    handler.user_token_form[username] = token
    response = generate_response(content.encode(), b'text/html; charset=utf-8', b'200 OK', ["username","token"], [username, login_token.decode()])
    handler.request.sendall(response)


def homeCSS(request, handler):
    send_response('Pages/home.css', b'text/css; charset=utf-8', request, handler)


def redirct_to_login(request, handler):
    handler.request.sendall('HTTP/1.1 301 OK\r\nContent-Length: 0\r\nLocation: /login\r\n'.encode())