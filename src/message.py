import time
from data import CHANNEL_DATA, MESSAGES_DATA, MESSAGE_IDS, FLOCKR_DATA
from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid
import threading
from hangman import check_hangman


def message_send(token, channel_id, message):
    token_operation = TokenJwt()

    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # check if the length of the message > 1000
    if len(message) > 1000:
        raise InputError(description='error occurred: Message is more than 1000')

    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # get member list
    member_list = ret[0]

    # check user is already in the channel
    if u_id not in member_list:
        raise AccessError(description='error occurred: the authorised user has not joined the channel')

    message = check_hangman(message, channel_id)

    # Store message in database
    sql = '''
    INSERT INTO project.message_data (channel_id, message, time_created, u_id, is_pinned, react_uid) 
    VALUES (%s, %s, %s, %s, %s, %s);
    '''
    value = (channel_id, message, int(time.time()), u_id, False, [])
    db_connect.execute(sql, value)

    sql = "SELECT MAX(message_id) FROM project.message_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()

    # get message_id
    message_id = ret[0]
    db_connect.close()
    return {
        'message_id': message_id
    }


def message_remove(token, message_id):
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # check if the message_id is valid
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT channel_id FROM project.message_data WHERE  message_id=(%s)"
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description="error occurred: message doesn't exist")

    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    sql = '''
    SELECT owner, u_id
    FROM project.channel_data c
            INNER JOIN project.message_data m ON c.channel_id = m.channel_id
    WHERE message_id=(%s);
    '''
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    owner_list = ret[0]
    send_uid = ret[1]
    # check user has permission
    if u_id not in owner_list and u_id != send_uid:
        raise AccessError(description='error occurred: the authorised user is not owner')

    # has permission to remove
    sql = "DELETE FROM project.message_data WHERE message_id=(%s)"
    value = (message_id,)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


def message_edit(token, message_id, message):
    # If the new message is an empty string, the message is deleted
    if len(message) == 0:
        return message_remove(token, message_id)
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    SELECT owner, u_id
    FROM project.channel_data c
            INNER JOIN project.message_data m ON c.channel_id = m.channel_id
    WHERE message_id=(%s)
    '''
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    owner_list = ret[0]
    send_uid = ret[1]
    # check permission
    if send_uid != u_id and u_id not in owner_list:
        raise AccessError(description='error occurred: the authorised user is not owner')

    # edit message
    sql = "UPDATE project.message_data SET message=(%s) WHERE message_id=(%s)"
    value = (message, message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


def message_sendlater(token, channel_id, message, time_sent):
    time_sent = int(time_sent)

    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s);"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # check if the channel_id is valid
    if ret is None:
        raise InputError(description='error occurred: channel is not valid')

    member_list = ret[0]

    # check if the length of the message > 1000
    if len(message) > 1000:
        raise InputError(description='error occurred: Message is more than 1000')

    # get user's u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)
    if u_id not in member_list:
        raise AccessError(description='error occurred: the authorised user has not joined the channel')

    current_time = int(time.time())
    # check the time is valid or not
    if time_sent < current_time:
        raise InputError(description='error occurred: Time sent is a time in the past')

    # get the total sleep time
    sleep_time = time_sent - current_time

    sql = '''
    INSERT INTO project.message_data (message) VALUES (%s)
    '''
    value = (None,)
    db_connect.execute(sql, value)

    sql = "SELECT MAX(message_id) FROM project.message_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()
    message_id = ret[0]

    t = threading.Timer(sleep_time, store_message_data, args=[message_id, channel_id, message, time_sent, u_id])
    t.start()

    db_connect.close()

    return {
        'message_id': message_id
    }


def message_react(token, message_id, react_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # get the u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)
    # check whether the message id is valid

    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    SELECT member 
    FROM project.channel_data c
            INNER JOIN project.message_data m ON c.channel_id=m.channel_id
    WHERE m.message_id = (%s)
    '''
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    if ret is None:
        raise InputError(description='react_id is not a valid React ID.')

    member_list = ret[0]

    if u_id not in member_list:
        raise InputError("message_id is not a valid message within a channel that the authorised user has joined")

    sql = "SELECT react_uid FROM project.message_data WHERE message_id=(%s);"
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: message_id is not valid')
    # check the react id
    if react_id != 1:
        raise InputError(description='react_id is not a valid React ID.')

    # get the react id list
    react_list = ret[0]

    # check if react
    if u_id in react_list:
        raise InputError(description='error occurred: user already reacted')

    # react
    react_list.append(u_id)
    sql = "UPDATE project.message_data SET react_uid=(%s) WHERE message_id=(%s);"
    value = (react_list, message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


def message_unreact(token, message_id, react_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # get the u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
        SELECT member 
        FROM project.channel_data c
                INNER JOIN project.message_data m ON c.channel_id=m.channel_id
        WHERE m.message_id = (%s)
        '''
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    if ret is None:
        raise InputError(description='error occurred: message_id is not valid')

    member_list = ret[0]

    if u_id not in member_list:
        raise InputError(description='error occurred: message_id is not a valid '
                                     'message within a channel that the authorised user has joined')

    # check whether the message id is valid
    sql = "SELECT react_uid FROM project.message_data WHERE message_id=(%s)"
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: message_id is not valid')

    react_list = ret[0]
    # check the react id
    if react_id != 1:
        raise InputError(description='error occurred: react_id is not valid')

    # check react list
    if u_id not in react_list:
        raise InputError(description='error occurred: user has not react')

    react_list.remove(u_id)
    sql = "UPDATE project.message_data SET react_uid=(%s) WHERE message_id=(%s)"
    value = (react_list, message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


def message_pin(token, message_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # get the u_id from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT is_pinned, channel_id FROM project.message_data WHERE message_id=(%s)"
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check whether the message id is valid
    if ret is None:
        raise InputError(description='error occurred: message_id is not valid')
    pin_flag = ret[0]
    channel_id = ret[1]

    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # get member list
    member_list = ret[0]

    sql = "SELECT owner FROM project.flockr_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()

    # get flockr owner list
    flockr_owner = ret[0]
    # check authorised user
    if u_id not in member_list and u_id not in flockr_owner:
        raise AccessError(description='error occurred: the authorised user is not a channel member or owner')

    if pin_flag is True:
        raise InputError(description='Message is already pinned')

    sql = "UPDATE project.message_data SET is_pinned=(%s) WHERE message_id=(%s)"
    value = (True, message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


def message_unpin(token, message_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occured: token is not valid')

    # get uid from token
    token_operation = TokenJwt()
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT is_pinned, channel_id FROM project.message_data WHERE message_id=(%s)"
    value = (message_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # check whether the message id is valid
    if ret is None:
        raise InputError(description='error occurred: message_id is not valid')

    pin_flag = ret[0]
    channel_id = ret[1]

    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    member_list = ret[0]

    sql = "SELECT owner FROM project.flockr_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()

    flockr_owner = ret[0]

    if u_id not in member_list and u_id not in flockr_owner:
        raise AccessError(description='The authorised user is not a channel member or owner')

    if pin_flag is False:
        raise InputError(description='Message is already unpinned')

    sql = "UPDATE project.message_data SET is_pinned=(%s) WHERE message_id=(%s)"
    value = (False, message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


############################
#     helper functions     #
############################
def store_message_data(message_id, channel_id, message, time_sent, u_id):
    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    UPDATE project.message_data SET channel_id=(%s), message=(%s), time_created=(%s), u_id=(%s), is_pinned=(%s), react_uid=(%s)
    WHERE message_id=(%s)
    '''
    value = (channel_id, message, time_sent, u_id, False, [], message_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()
