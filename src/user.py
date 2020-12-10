import re
import os
import urllib.request
import flask
from PIL import Image
from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid



def user_profile(token, u_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT email, name_first, name_last, handle, \
           profile_img_url FROM project.user_data WHERE u_id=(%s);"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # check uid is valid
    if ret is None:
        raise InputError(description='error occurred: User with u_id is not a valid user')

    user_dict = {}  # for return
    email = ret[0]
    name_first = ret[1]
    name_last = ret[2]
    handle_str = ret[3]
    profile_img_url = ret[4]

    user_dict['u_id'] = u_id
    user_dict['email'] = email
    user_dict['name_first'] = name_first
    user_dict['name_last'] = name_last
    user_dict['handle_str'] = handle_str
    user_dict['profile_img_url'] = profile_img_url

    # close database connection
    db_connect.close()

    return {'user': user_dict}


def user_profile_setname(token, name_first, name_last):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    if len(name_first) > 50 or len(name_first) < 1:  # check length of name_first
        raise InputError(
            description='error occurred: first name is not between \
                1 and 50 characters inclusively in length')
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError(
            description='error occurred: last name is not between \
                1 and 50 characters inclusively in length')
    # get user's u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "UPDATE project.user_data SET name_first=(%s), \
           name_last=(%s) WHERE u_id=(%s)"
    value = (name_first, name_last, u_id)
    db_connect.execute(sql, value)
    db_connect.close()

    return {
    }


def user_profile_setemail(token, email):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    exist_change = False
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if re.search(regex, email):  # check Email entered is valid
        exist_change = True
    if exist_change is False:
        raise InputError(
            description='error occurred: email entered is not valid')

    # check email address is independent
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT email FROM project.user_data WHERE email=(%s);"
    value = (email,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is not None:
        raise InputError(description='error occurred: email is already used by another user')

    # get user's u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)

    sql = "UPDATE project.user_data SET email=(%s) WHERE u_id=(%s)"
    value = (email, u_id)
    db_connect.execute(sql, value)

    db_connect.close()

    return {
    }


def user_profile_sethandle(token, handle_str):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    if len(handle_str) > 20 or len(handle_str) < 3:  # check handle is valid
        raise InputError(
            description='error occurred: handle must be between 3 and 20 characters')

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT handle FROM project.user_data WHERE handle=(%s)"
    value = (handle_str,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is not None:
        raise InputError(
            description='error occurred: handle is already used by another user')

    # get user's u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)
    sql = "UPDATE project.user_data SET handle=(%s) WHERE u_id=(%s);"
    value = (handle_str, u_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    try:
        urllib.request.urlopen(img_url)
    except urllib.error.HTTPError:
        raise InputError(description='error occurred: \
                         img_url returns an HTTP status other than 200.')

    # check img is jpg
    if not img_url.lower().endswith('.jpg'):
        raise InputError(description='error occurred: Image uploaded is not a JPG')

    if not os.path.exists('./image'):
        os.makedirs('./image')
    # get user's u_id from token
    u_id = token_operation.get_uid(token)
    image_address = './image/' + str(u_id) + '.jpg'
    urllib.request.urlretrieve(img_url, image_address)
    image_object = Image.open(image_address)
    width, height = image_object.size

    if (int(x_start) < 0 or int(x_start) > width or int(x_end) < 0 or int(x_end) > width or
            int(y_start) < 0 or int(y_start) > height or int(y_end) < 0 or int(y_end) > height):
        os.remove(image_address)
        raise InputError(
            description="x_start, y_start, x_end, y_end are not \
                         within the dimensions of the image at the URL")

    if int(x_start) >= int(x_end) or int(y_start) >= int(y_end):
        os.remove(image_address)
        raise InputError(description="start value can't exceed end value")

    cropped = image_object.crop((x_start, y_start, x_end, y_end))
    cropped.save(image_address)
    base_url = flask.request.host_url

    image_url = base_url + 'image/' + str(u_id) + '.jpg'

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "UPDATE project.user_data SET profile_img_url=(%s) WHERE u_id=(%s)"
    value = (image_url, u_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}
