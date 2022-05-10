import database
import profileHelpers
from profileHelpers import send_file
from response import generate_Response200, generate_Redirect, generate_response
from router import Route
from template_engine import render_template

last_user = []


def add_paths(router):
    router.add_route(Route('GET', "/profile.css", profile_style))
    router.add_route(Route('GET', "/profile", profile))
    router.add_route(Route('GET', "/image/.", images))
    router.add_route(Route('POST', "/image-upload", post_profilePic))
    router.add_route(Route('GET', "/editProfile", edit_profile))


def profile(request, handler):
    global last_user
    username_signed = request.cookies.get('username')
    username_formed = request.form_content.get('uname')
    print("username_signed", username_signed, flush=True)
    print("username formed", username_formed, flush=True)
    if len(last_user) == 0:
        print("condition 1", flush=True)
        record_con_token = database.get_token_by_username(username_signed)
        record_username = record_con_token.get('username')
        record_token = record_con_token.get('auth_token')

        default_random_info = "Write some info here"
        default_pic_img = "defaultImage.jpeg"
        original_dict = {'auth_token': record_token, 'profile_username': record_username, 'profile_pic': 'defaultImage',
                         'random_info': default_random_info}
        database.create_profileEdit(original_dict)
        content = render_template("Pages/profile.html",
                                  {"username_sent": record_username, "image_sent": "defaultImage.jpeg",
                                   "random_info": default_random_info})

        response = generate_Response200(content.encode(), "text/html; charset=utf-8", "200OK")
        handler.request.sendall(response)
    else:
        print("condition 2", flush=True)
        # find their profile info
        user = last_user[0]
        print("the user", user, flush=True)
        record_with_token = database.get_token_by_username(user)

        token_returned = record_with_token.get('auth_token')

        profile_record = database.find_profileInfo(token_returned)

        profile_user = profile_record.get('profile_username')
        profile_userString = profile_user.decode('utf-8')

        profile_random_info = profile_record.get('random_info')
        profile_random_infoString = profile_random_info.decode('utf-8')

        profile_pic = profile_record.get('profile_pic')

        content2 = render_template("Pages/profile.html",
                                   {"username_sent": profile_userString, "image_sent": profile_pic,
                                    "random_info": profile_random_infoString})

        response = generate_Response200(content2.encode(), "text/html; charset=utf-8", "200OK")
        handler.request.sendall(response)


def profile_style(request, handler):
    send_file("./Pages/profile.css", "text/css; charset=utf-8", request, handler)


def edit_profile(request, handler):
    send_file("Pages/editProfile.html", "text/html; charset=utf-8", request, handler)


def post_profilePic(request, handler):
    makeChange(request, handler)

    all_profiles = database.list_profile()
    print("all profiles", all_profiles, flush=True)
    redirect_url = "/profile"
    response_redirect = generate_Redirect(redirect_url)
    handler.request.sendall(response_redirect)


def images(request, handler):
    image_path = request.path
    if "!" in image_path:
        print("this one")
        slice_image_path = image_path[7:]
        print("slice image path", slice_image_path)
        basic_name = slice_image_path[:len(slice_image_path) - 1]
        basic_name = basic_name.lower()
        basic_name = basic_name.replace("/", "")
        send_file("sample_page/image/" + basic_name + ".jpg", "image/jpeg", request, handler)
    elif image_path[-1].isdigit():
        print("this one here")
        slice_image_path = image_path[7:]
        slice_image_path = slice_image_path.replace("/", "")
        # print("image_path", image_path, "slice image path", slice_image_path, flush=True)
        send_file(slice_image_path, "image/jpeg", request, handler)
    else:
        print("this one there")
        slice_image_path = image_path[7:]
        # print("what's the slice", slice_image_path, flush=True)
        # slice_image_path = slice_image_path.lower()
        slice_image_path = slice_image_path.replace("/", "")
        send_file("Pages/" + slice_image_path, "image/jpeg", request, handler)


def makeChange(request, handler):
    username_sent = request.cookies.get('username')
    recordDB = database.get_token_by_username(username_sent)

    if recordDB is not None:
        token_pulled = recordDB.get('auth_token')
        # check who needs to update
        [update_usernameBoolean, update_picBoolean, update_randomBoolean] = update_what(request, handler)
        print("the boolean results ", update_usernameBoolean, update_randomBoolean, update_picBoolean, flush=True)
        # make the change
        [username_now, random_info_now, profile_picNow] = give_anUpdate(request, token_pulled, update_usernameBoolean,
                                                                        update_randomBoolean, update_picBoolean)
        print("what r the changes", username_now, random_info_now, profile_picNow, flush=True)

        return [username_now, random_info_now, profile_picNow]


def give_anUpdate(request, token_sent, update_usernameBoolean, update_randomBoolean, update_picBoolean):
    profile_record = database.find_profileInfo(str(token_sent))
    username_now = update_username(request, profile_record, update_usernameBoolean)
    random_info_now = update_randomInfo(request, profile_record, update_randomBoolean)
    profile_picNow = update_profilePic(request, profile_record, update_picBoolean)
    updated_dict = {'auth_token': token_sent, 'profile_username': username_now,
                    'profile_pic': profile_picNow,
                    'random_info': random_info_now}
    database.update_profileEdit(updated_dict)

    # store the user token
    database.store_user_token(username_now, token_sent)
    return [username_now, random_info_now, profile_picNow]


def update_username(request, profile_record, update_usernameBoolean):
    # print("in update_user", update_usernameBoolean, flush=True)
    username_now = ""
    username_form = request.form_content.get('uname')
    username_DB = profile_record.get('profile_username')
    if update_usernameBoolean:
        username_now = username_form
    else:
        username_now = username_DB
    return username_now


def update_profilePic(request, profile_record, update_picBoolean):
    print("in update_pic", update_picBoolean, flush=True)
    profile_pic_now = ""
    pic_bytes = request.form_content.get('upload')
    picture_file_form = profileHelpers.write_incoming_picture(pic_bytes)
    profile_picDB = profile_record.get('profile_pic')
    if update_picBoolean:
        profile_pic_now = picture_file_form
    else:
        profile_pic_now = profile_picDB
    return profile_pic_now


def update_randomInfo(request, profile_record, update_randomBoolean):
    print("in update_randomInfo", update_randomBoolean, flush=True)
    profile_randomInfo = ""
    profile_randomForm = request.form_content.get('random')
    if update_randomBoolean:
        profile_randomInfo = profile_randomForm
        # print("if", profile_randomInfo, flush=True)
    else:
        profile_randomInfo = profile_record.get('random_info')
        # print("else", profile_randomInfo, flush=True)
    return profile_randomInfo


def update_what(request, handler):
    global last_user
    username_update = False
    picture_update = False
    random_info_update = False
    username_submitted = request.form_content.get('uname')
    picture_submitted = request.form_content.get('upload')
    random_info_submitted = request.form_content.get('random')
    last_user = [username_submitted, picture_submitted, random_info_submitted]
    # print("in update what ", username_submitted, picture_submitted, random_info_submitted, flush=True)
    if username_submitted is not None and username_submitted != b'':
        username_update = True
    if picture_submitted is not None and picture_submitted != b'':
        picture_update = True
    if random_info_submitted is not None and random_info_submitted != b'':
        random_info_update = True
    return [username_update, picture_update, random_info_update]
