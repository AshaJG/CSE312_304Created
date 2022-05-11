import os

import database
from response import generate_Response200
from feed_paths import save_image


def send_file(filename, mime_type, request, handler):
    with open(filename, "rb") as content:
        body = content.read()
        response = generate_Response200(body, mime_type, '200 OK')
        handler.request.sendall(response)


def makeChange(request, handler):
    username_sent = request.cookies.get('username')
    recordDB = database.find_profileInfo(username_sent)
    # recordDB = database.get_token_by_username(username_sent)

    if recordDB is not None:
        token_pulled = recordDB.get('auth_token')
        # check who needs to update
        [update_usernameBoolean, update_picBoolean, update_randomBoolean] = update_what(request, handler)
        # print("the boolean results ", update_usernameBoolean, update_randomBoolean, update_picBoolean, flush=True)
        # make the change
        [name_now, random_info_now, profile_picNow] = give_anUpdate(request, token_pulled, update_usernameBoolean,
                                                                    update_randomBoolean, update_picBoolean)

        # print("what r the changes", name_now, random_info_now, profile_picNow, flush=True)

        return [name_now, random_info_now, profile_picNow]


def give_anUpdate(request, token_sent, update_usernameBoolean, update_randomBoolean, update_picBoolean):
    # print("in here update")
    username_sent = request.cookies.get('username')
    profile_record = database.find_profileInfo(str(username_sent))
    # print("p record", profile_record, flush=True)
    profile_username = profile_record.get('profile_username')
    profile_token = profile_record.get('auth_token')

    name_now = update_name(request, profile_record, update_usernameBoolean)

    # sanitization
    if type(name_now) != str:
        name_nowSanitized = escape_html((name_now.decode()))
    else:
        name_nowSanitized = escape_html(name_now)
    random_info_now = update_randomInfo(request, profile_record, update_randomBoolean)
    if type(random_info_now) != str:
        random_info_Sanitized = escape_html((random_info_now.decode()))
    else:
        random_info_Sanitized = escape_html(random_info_now)

    profile_picNow = update_profilePic(request, profile_record, update_picBoolean)
    # print("line 157", name_now, random_info_now)

    updated_dict = {'auth_token': token_sent, 'profile_username': profile_username, 'profile_name': name_nowSanitized,
                    'profile_pic': profile_picNow,
                    'random_info': random_info_Sanitized}
    database.update_profileEdit(updated_dict)

    return [name_nowSanitized, random_info_Sanitized, profile_picNow]


def update_name(request, profile_record, update_usernameBoolean):
    # print("in update_user", update_usernameBoolean, flush=True)
    username_now = ""
    username_form = request.form_content.get('uname')
    # print("username_form")
    username_DB = profile_record.get('profile_name')
    # print("username_db")
    if update_usernameBoolean:
        username_now = username_form
    else:
        username_now = username_DB
    # print("username_now", username_now)
    return username_now


def update_profilePic(request, profile_record, update_picBoolean):
    # print("in update_pic", update_picBoolean, flush=True)
    profile_pic_now = ""
    pic_bytes = request.form_content.get('upload')
    picture_file_form = save_image(pic_bytes)
    profile_picDB = profile_record.get('profile_pic')
    if update_picBoolean:
        profile_pic_now = picture_file_form
    else:
        profile_pic_now = profile_picDB
    return profile_pic_now


def update_randomInfo(request, profile_record, update_randomBoolean):
    # print("in update_randomInfo", update_randomBoolean, flush=True)
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
    name_update = False
    picture_update = False
    random_info_update = False
    name_submitted = request.form_content.get('uname')
    picture_submitted = request.form_content.get('upload')
    random_info_submitted = request.form_content.get('random')

    # print("in update what ", username_submitted, picture_submitted, random_info_submitted, flush=True)
    if name_submitted is not None and name_submitted != b'':
        name_update = True
    if picture_submitted is not None and picture_submitted != b'':
        picture_update = True
    if random_info_submitted is not None and random_info_submitted != b'':
        random_info_update = True
    return [name_update, picture_update, random_info_update]


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
