import re
import hashlib
import string
import random
import smtplib
from email.mime.text import MIMEText
from error import InputError
from helper import TokenJwt
from db_connector import DbConnector


def auth_login(email: str, password: str) -> dict:
    """
    Given a registered users' email and password and generates a valid token
    for the user to remain authenticated

    :param email: the user's email
    :param password: the user's password
    :return: dictionary with keys "u_id" and "token"
    """
    # check if email invalid
    if not check(email):
        raise InputError(description='error occurred: Email entered is not a valid email')

    # get user details from database
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT u_id, password FROM project.user_data WHERE email = (%s)"
    value = (email,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # check if email do not belong to any user
    if ret is None:
        raise InputError(description='error occurred: Email entered does not belong to a user')

    user_uid = ret[0]
    user_pwd = ret[1]

    # password if correct
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    # if user_pwd != password:
    if user_pwd != hash_password:
        raise InputError(description='error occurred: Password is not correct')

    # generate token
    token_operation = TokenJwt()
    user_token = token_operation.encode_token({'u_id': user_uid})

    # if not login before, store the token
    # add token
    sql = "UPDATE project.user_data set token=(%s) where email=(%s)"
    value = (user_token, email)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
        'u_id': user_uid,
        'token': user_token
    }


def auth_logout(token: str) -> dict:
    """
    Given an active token, invalidates the token to log the user out.
    If a valid token is given, and the user is successfully logged out,
    it returns true, otherwise false.

    :param token: user's token
    :return: a dictionary with key 'is_success' which contains 'True'
            if user is successfully logged out, 'False' otherwise
    """

    db_connect = DbConnector()
    db_connect.cursor()
    sql = 'SELECT token from project.user_data WHERE token =%s'
    value = (token,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        logout_success = False
    else:
        sql = "UPDATE project.user_data set token=(%s) where token=(%s)"
        value = (None, token)
        db_connect.execute(sql, value)
        logout_success = True

    # close database connection
    db_connect.close()

    return {
        'is_success': logout_success,
    }


def auth_register(email: str, password: str, name_first: str, name_last: str) -> dict:
    """
    Given a user's first and last name, email address, and password,
    create a new account for them and return a new token for authentication in their session.

    :param email: user's email
    :param password: user's password
    :param name_first: user's first name
    :param name_last: user's last name
    :return: dictionary with keys "u_id" and "token"
    """
    # check if email invalid
    if not check(email):
        raise InputError(description='error occurred: Email entered is not a valid email')

    # check if email has already been used
    db_connect = DbConnector()
    db_connect.cursor()  # connect to database and get cursor
    sql = "SELECT email from project.user_data WHERE email = %s"
    value = (email,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is not None:
        raise InputError(description='error occurred: Email address is already '
                                     'being used by another user')

    # check the length of password
    if len(password) < 6:
        raise InputError(description='error occurred: Password entered is less '
                                     'than 6 characters long')

    if len(name_first) not in range(1, 51):
        raise InputError(description='error occurred: first name is not '
                                     'between 1 and 50 characters inclusively in length')

    if len(name_last) not in range(1, 51):
        raise InputError(description='error occurred: last name is not '
                                     'between 1 and 50 characters inclusively in length')

    # generate u_id for the new user
    sql = "INSERT INTO project.user_data (email) VALUES (%s)"
    value = (email,)
    db_connect.execute(sql, value)

    sql = "SELECT u_id FROM project.user_data WHERE email=(%s)"
    value = (email,)
    db_connect.execute(sql,value)
    ret = db_connect.fetchone()
    user_uid = ret[0]
    # sql = "SELECT COUNT(*) FROM project.user_data"
    # db_connect.execute(sql)
    # ret = db_connect.fetchone()
    # user_uid = ret[0] + 1
    # print(user_uid)

    # generate a handle for the new user
    # which contains the first letter of the name_first by default
    # cut off the part where exceeds 20

    handle = (name_first[0] + name_last).lower()

    if len(handle) > 20:
        handle = handle[0:20]

    # check if it is unique otherwise
    sql = "SELECT handle from project.user_data WHERE handle=%s"
    value = (handle,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # if it exceeds 20, cutoff the extra part from the original handle and remain user_uid
    # add user_uid at the end of the handle
    if ret is not None:
        if len(handle + str(user_uid)) > 20:
            handle = handle[0:(20 - len(str(user_uid)))] + str(user_uid)
        else:
            handle = handle + str(user_uid)

    # generate the token
    token_operation = TokenJwt()
    token = token_operation.encode_token({'u_id': user_uid})
    # hashing the password
    hash_password = hashlib.sha256(password.encode()).hexdigest()

    # add user in database
    sql = '''
    UPDATE project.user_data
    set password=(%s), name_first=(%s), name_last=(%s), token=(%s), handle=(%s)
    WHERE email=(%s)
    '''
    value = (hash_password, name_first, name_last, token, handle, email)
    db_connect.execute(sql, value)

    if user_uid == 1:
        sql = "INSERT INTO project.flockr_data (owner) VALUES ('{%s}')"
        value = [user_uid]
        db_connect.execute(sql, value)

    db_connect.close()

    return {
        'u_id': user_uid,
        'token': token
    }


def auth_passwordreset_request(email: str) -> dict:
    """
    Given an email address, if the user is a registered user,
    send's them an email containing a specific secret code.

    :param email: user's email
    :return:
    """

    # check if email valid
    if not check(email):
        raise InputError(description='error occurred: Email entered is not a valid email')

    # check if entered email belongs to a registered user
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT email from project.user_data WHERE email = (%s)"
    value = (email,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: Email entered does not belong to a user')

    # generate a random reset_code
    reset_code = generate_code()
    sql = "UPDATE project.user_data set reset_code=(%s) where email=(%s)"
    value = (reset_code, email)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    # send an email contained the reset_code to the user
    # config
    mail_host = 'smtp.qq.com'
    mail_user = '138876722'
    mail_pass = 'rblmdebsmifdbjbf'
    sender = '138876722@qq.com'
    receivers = [email]
    # content
    message = MIMEText(reset_code, 'plain', 'utf-8')
    message['Subject'] = 'Flockr Password Reset'
    message['From'] = sender
    message['To'] = receivers[0]
    # connect and log on server
    smtp = smtplib.SMTP()
    smtp.connect(mail_host, 587) # use 25 if 587 doesn't work
    smtp.login(mail_user, mail_pass)
    # send
    smtp.sendmail(sender, receivers, message.as_string())
    # log out server
    smtp.quit()

    return {}


def auth_passwordreset_reset(reset_code: str, new_password: str) -> dict:
    '''
    Given a reset code for a user,
    set that user's new password to the password provided.

    :param reset_code: generated random code sent to user
    :param new_password: user's new password to be reset
    :return:
    '''
    # check if new password is valid
    if len(new_password) < 6:
        raise InputError(description='error occurred: Password entered is less '
                                     'than 6 characters long')
    # check if reset code match
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT u_id FROM project.user_data WHERE reset_code=(%s)"
    value = (reset_code,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: Reset code entered does not match')

    # use for sql query
    u_id = ret[0]

    # UPDATE new password and remove the reset code from database
    password = hashlib.sha256(new_password.encode()).hexdigest()
    sql = "UPDATE project.user_data set password=(%s), reset_code = (%s) WHERE u_id=(%s)"
    value = (password, None, u_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


##########################
#    helper function     #
##########################

def check(email: str) -> bool:
    """
    check if the input email is valid

    :param email: user's email
    :return: true if email is valid, false otherwise
    """
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if re.search(regex, email):
        return True

    return False


def generate_code():
    '''
    generate a unique reset code for user
    '''
    reset_code_str = ''.join(random.SystemRandom().choice
                             (string.ascii_uppercase + string.digits) for _ in range(16))
    # check if unique
    # is_unique = False
    # if reset_code_str not in RESET_CODE_LIST:
    #     return reset_code_str
    # else:
    #     generate_code()
    return reset_code_str
