from profileHelpers import send_file, send_to_database
from response import generate_Response200, generate_Redirect
from router import Route


def add_paths(router):
    router.add_route(Route('GET', "/profile.css", profile_style))
    router.add_route(Route('GET', "/profile", profile))
    router.add_route(Route('POST', "/image-upload", post_profilePic))
    router.add_route(Route('GET', "/editProfile", edit_profile))
    # router.add_route(Route('GET', "/$", home))


# def home(request, handler):
#     response = generate_Response200("connected".encode(), "text/html; charset=utf-8", "200OK")
#     handler.request.sendall(response)


def profile(request, handler):
    send_file("Pages/profile.html", "text/html; charset=utf-8", request, handler)


def profile_style(request, handler):
    send_file("./Pages/profile.css", "text/css; charset=utf-8", request, handler)


def edit_profile(request, handler):
    send_file("Pages/editProfile.html", "text/html; charset=utf-8", request, handler)


def post_profilePic(request, handler):
    # as soon as the edit username , the random info and pic comes , save to db
    # change the DB to find by token and update the DB info instead
    # send_to_database()
    # then do a redirect
    redirect_url = "/profile"
    response_redirect = generate_Redirect(redirect_url)
    handler.request.sendall(response_redirect)
