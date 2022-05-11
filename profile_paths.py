import database
from profileHelpers import send_file, makeChange
from response import generate_Response200, generate_Redirect
from router import Route
from template_engine import render_template


def add_paths(router):
    router.add_route(Route('GET', "/profile.css", profile_style))
    router.add_route(Route('GET', "/profile", profile))
    router.add_route(Route('GET', "/image/.", images))
    router.add_route(Route('POST', "/image-upload", post_profilePic))
    router.add_route(Route('GET', "/editProfile", edit_profile))


def profile(request, handler):
    username_signed = request.cookies.get('username')
    user = database.find_profileInfo(username_signed)

    if user is None:
        # print("condition 1", flush=True)
        record_con_token = database.get_token_by_username(username_signed)
        record_username = record_con_token.get('username')
        record_token = record_con_token.get('auth_token')

        default_random_info = "Write some info here"
        default_name = "put name here"
        default_pic_img = "defaultImage.jpeg"
        original_dict = {'auth_token': record_token, 'profile_username': record_username, 'profile_name': default_name,
                         'profile_pic': 'defaultImage',
                         'random_info': default_random_info}

        database.create_profileEdit(original_dict)

        content = render_template("Pages/profile.html",
                                  {"username_sent": record_username, "name": "name here",
                                   "image_sent": "defaultImage.jpeg",
                                   "random_info": default_random_info})

        response = generate_Response200(content.encode(), "text/html; charset=utf-8", "200OK")
        handler.request.sendall(response)
    else:
        profile_user = user.get('profile_name')

        # for the username
        if type(profile_user) != str:
            profile_userString = profile_user.decode('utf-8')
        else:
            profile_userString = profile_user

        # for the random info
        profile_randomInfo = user.get('random_info')
        if type(profile_randomInfo) != str:
            profile_randomInfoString = profile_randomInfo.decode('utf-8')
        else:
            profile_randomInfoString = profile_randomInfo
        # print("p_r", profile_randomInfo, type(profile_randomInfo), flush=True)

        profile_pic = user.get('profile_pic')

        content2 = render_template("Pages/profile.html",
                                   {"username_sent": username_signed, "name": profile_userString,
                                    "image_sent": profile_pic,
                                    "random_info": profile_randomInfoString})

        response = generate_Response200(content2.encode(), "text/html; charset=utf-8", "200OK")
        handler.request.sendall(response)


def profile_style(request, handler):
    send_file("./Pages/profile.css", "text/css; charset=utf-8", request, handler)


def edit_profile(request, handler):
    send_file("Pages/editProfile.html", "text/html; charset=utf-8", request, handler)


def post_profilePic(request, handler):
    makeChange(request, handler)
    all_profiles = database.list_profile()
    # print("all profiles", all_profiles, flush=True)
    redirect_url = "/profile"
    response_redirect = generate_Redirect(redirect_url)
    handler.request.sendall(response_redirect)


def images(request, handler):
    image_path = request.path
    if "!" in image_path:
        slice_image_path = image_path[7:]
        basic_name = slice_image_path[:len(slice_image_path) - 1]
        basic_name = basic_name.lower()
        basic_name = basic_name.replace("/", "")
        send_file("sample_page/image/" + basic_name + ".jpg", "image/jpeg", request, handler)
    elif image_path[-1].isdigit():
        slice_image_path = image_path[7:]
        slice_image_path = slice_image_path.replace("/", "")
        # print("image_path", image_path, "slice image path", slice_image_path, flush=True)
        send_file(slice_image_path, "image/jpeg", request, handler)
    else:
        slice_image_path = image_path[7:]
        # print("what's the slice", slice_image_path, flush=True)
        # slice_image_path = slice_image_path.lower()
        slice_image_path = slice_image_path.replace("/", "")
        send_file("Pages/" + slice_image_path, "image/jpeg", request, handler)
