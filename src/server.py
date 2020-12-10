from json import dumps
import os
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from auth import auth_register, auth_login, auth_logout, auth_passwordreset_request, \
    auth_passwordreset_reset
from channel import channel_invite, channel_details, channel_messages, channel_leave, \
    channel_join, channel_addowner, channel_removeowner
from channels import channels_create, channels_list, channels_listall
from error import InputError
from message import message_send, message_remove, message_edit, message_sendlater,\
                    message_react, message_unreact, message_pin, message_unpin
from other import users_all, admin_userpermission_change, search, clear, admin_user_remove
from user import user_profile, user_profile_setname, user_profile_setemail,\
                 user_profile_sethandle, user_profile_uploadphoto
from standup import standup_start, standup_active, standup_send


def default_handler(err):
    response = err.get_response()
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response
APP = Flask(__name__)
CORS(APP)
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)


# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data['password']
    login_user = auth_login(email, password)
    u_id = int(login_user['u_id'])
    token = str(login_user['token'])
    return dumps({
        'u_id': u_id,
        'token': token
    })


@APP.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json()
    token = str(data['token'])
    logout_user = auth_logout(token)

    return dumps({
        'is_success': logout_user["is_success"]
    })


@APP.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    email = str(data['email'])
    password = str(data['password'])
    name_first = str(data['name_first'])
    name_last = str(data['name_last'])
    register_user = auth_register(email, password, name_first, name_last)
    token = register_user['token']
    u_id = register_user['u_id']
    return dumps({
        'token': token,
        'u_id': u_id
    })


@APP.route("/auth/passwordreset/request", methods=["POST"])
def passwordreset_request():
    data = request.get_json()
    email = str(data['email'])
    auth_passwordreset_request(email)
    return dumps({})


@APP.route("/auth/passwordreset/reset", methods=["POST"])
def passwordreset_reset():
    data = request.get_json()
    reset_code = str(data['reset_code'])
    new_password = str(data['new_password'])
    auth_passwordreset_reset(reset_code, new_password)
    return dumps({})


@APP.route("/channel/invite", methods=["POST"])
def invite_channel():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    channel_invite(token, channel_id, u_id)
    return dumps({})


@APP.route("/channel/details", methods=["GET"])
def details_channel():
    token = request.args.get("token", type=str)
    channel_id = request.args.get("channel_id", type=int)
    details = channel_details(token, channel_id)
    return dumps({
        'name': details['name'],
        'owner_members': details['owner_members'],
        'all_members': details['all_members']
    })


@APP.route("/channel/messages", methods=["GET"])
def messages_channel():
    token = str(request.args.get("token"))
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))
    messages = channel_messages(token, channel_id, start)
    return dumps({
        'messages': messages['messages'],
        'start': messages['start'],
        'end': messages['end']
    })


@APP.route("/channel/leave", methods=["POST"])
def leave_channel():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    channel_leave(token, channel_id)
    return dumps({})


@APP.route("/channel/join", methods=["POST"])
def join_channel():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    channel_join(token, channel_id)
    return dumps({})


@APP.route("/channel/addowner", methods=["POST"])
def addowner_channel():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    channel_addowner(token, channel_id, u_id)
    return dumps({})


@APP.route("/channel/removeowner", methods=["POST"])
def removeowner_channel():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    channel_removeowner(token, channel_id, u_id)
    return dumps({})


@APP.route("/channels/create", methods=["POST"])
def creat_channel():
    data = request.get_json()
    token = str(data['token'])
    name = str(data['name'])
    is_public = bool(data['is_public'])
    channel = channels_create(token, name, is_public)
    channel_id = channel['channel_id']

    return dumps({
        "channel_id": channel_id
    })


@APP.route("/channels/list", methods=["GET"])
def list_channels():
    token = request.args.get("token", type=str)
    list1 = channels_list(token)
    channels = list1["channels"]

    return dumps({
        "channels": channels
    })


@APP.route("/channels/listall", methods=["GET"])
def list_all_channels():
    token = request.args.get("token", type=str)
    listall = channels_listall(token)
    channels = listall["channels"]
    return dumps({
        "channels": channels
    })


@APP.route("/message/send", methods=["POST"])
def send_message():
    data = request.get_json()
    token = str(data["token"])
    channel_id = int(data["channel_id"])
    message = str(data["message"])
    message_id = message_send(token, channel_id, message)
    return dumps({
        "message_id": message_id["message_id"]
    })


@APP.route("/message/remove", methods=["DELETE"])
def remove_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    message_remove(token, message_id)
    return dumps({})


@APP.route("/message/edit", methods=["PUT"])
def edit_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    message = str(data["message"])
    message_edit(token, message_id, message)
    return dumps({})


@APP.route("/message/sendlater", methods=["POST"])
def sendlater_message():
    data = request.get_json()
    token = str(data["token"])
    channel_id = int(data["channel_id"])
    message = str(data["message"])
    time_sent = int(data["time_sent"])
    message_id = message_sendlater(token, channel_id, message, time_sent)
    return dumps({
        "message_id": message_id["message_id"]
    })


@APP.route("/message/react", methods=["POST"])
def react_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    react_id = int(data["react_id"])
    message_react(token, message_id, react_id)
    return dumps({})


@APP.route("/message/unreact", methods=["POST"])
def unreact_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    react_id = int(data["react_id"])
    message_unreact(token, message_id, react_id)
    return dumps({})


@APP.route("/message/pin", methods=["POST"])
def pin_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    message_pin(token, message_id)
    return dumps({})


@APP.route("/message/unpin", methods=["POST"])
def unpin_message():
    data = request.get_json()
    token = str(data["token"])
    message_id = int(data["message_id"])
    message_unpin(token, message_id)
    return dumps({})



@APP.route("/user/profile", methods=["GET"])
def profile_user():
    token = request.args.get("token", type=str)
    u_id = request.args.get("u_id", type=int)
    profile = user_profile(token, u_id)
    return dumps({"user": profile["user"]})


@APP.route("/user/profile/setname", methods=["PUT"])
def profile_setname():
    data = request.get_json()
    token = str(data["token"])
    name_first = str(data["name_first"])
    name_last = str(data["name_last"])
    user_profile_setname(token, name_first, name_last)
    return dumps({})


@APP.route("/user/profile/setemail", methods=["PUT"])
def profile_setemail():
    data = request.get_json()
    token = str(data["token"])
    email = str(data["email"])
    user_profile_setemail(token, email)
    return dumps({})


@APP.route("/user/profile/sethandle", methods=["PUT"])
def profile_sethandle():
    data = request.get_json()
    token = str(data["token"])
    handle_str = str(data["handle_str"])
    user_profile_sethandle(token, handle_str)
    return dumps({})


@APP.route("/users/all", methods=["GET"])
def all_users():
    token = request.args.get("token", type=str)
    user_details = users_all(token)
    return dumps({"users": user_details["users"]})


@APP.route("/admin/userpermission/change", methods=["POST"])
def user_permission_change():
    data = request.get_json()
    token = str(data["token"])
    u_id = int(data["u_id"])
    permission_id = data["permission_id"]
    admin_userpermission_change(token, u_id, permission_id)
    return dumps({})


@APP.route("/admin/user/remove", methods=["DELETE"])
def user_delete():
    data = request.get_json()
    token = str(data["token"])
    u_id = int(data["u_id"])
    admin_user_remove(token, u_id)
    return dumps({})


@APP.route("/search", methods=["GET"])
def search_msg():
    token = request.args.get("token", type=str)
    query_str = request.args.get("query_str", type=str)
    msg = search(token, query_str)
    return dumps({"messages": msg["messages"]})


@APP.route("/clear", methods=["DELETE"])
def clear_all():
    clear()
    return dumps({})


@APP.route("/user/profile/uploadphoto", methods=["POST"])
def uploadphoto():
    data = request.get_json()
    token = str(data["token"])
    img_url = data['img_url']
    x_start = int(data['x_start'])
    y_start = int(data['y_start'])
    x_end = int(data['x_end'])
    y_end = int(data['y_end'])
    user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    return dumps({})


@APP.route("/image/<string:path>")
def send_js(path):
    return send_from_directory('', 'image/'+path)


@APP.route("/standup/start", methods=["POST"])
def stand_start():
    data = request.get_json()
    token = str(data["token"])
    channel_id = int(data["channel_id"])
    length = int(data["length"])
    finish_time = standup_start(token, channel_id, length)
    return dumps(finish_time)


@APP.route("/standup/active", methods=["GET"])
def stand_active():
    token = request.args.get("token", type=str)
    channel_id = request.args.get("channel_id", type=int)
    active = standup_active(token, channel_id)
    return dumps(active)


@APP.route("/standup/send", methods=["POST"])
def stand_send():
    data = request.get_json()
    token = str(data["token"])
    channel_id = int(data["channel_id"])
    message = str(data["message"])
    standup_send(token, channel_id, message)
    return dumps({})





if __name__ == "__main__":
    APP.run(port=0)  # Do not edit this port
