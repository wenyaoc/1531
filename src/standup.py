import time
import threading
from data import USER_DATA
from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid



def standup_start(token, channel_id, length):
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # check channel_id is not valid
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT channel_id FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occured: Channel ID is not a valid channel')

    curr_time = int(time.time())
    exist_active = standup_active(token, channel_id)["is_active"]
    if exist_active is True:
        raise InputError(description='error occurred:\
                         An active standup is currently running in this channel')

    finish_time = curr_time + length

    # get id from token
    u_id = token_operation.get_uid(token)

    sql = "INSERT INTO project.active_data (standup_uid, channel_id, time_finish) VALUES (%s,%s,%s)"
    value = (u_id, channel_id, int(finish_time))
    db_connect.execute(sql, value)
    # time_dict = {
    #     'standup_uid': u_id,
    #     'channel_id': channel_id,
    #     'time_finish': int(finish_time),
    #     'message': ""
    # }
    # ACTIVE_DATA.append(time_dict)
    time1 = threading.Timer(length, send_standup_message, [channel_id])
    time1.start()
    return {'time_finish': int(finish_time)}


def standup_active(token, channel_id):
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # check channel_id is valid
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT channel_id FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: Channel ID is not a valid channel')

    # delete finished standup
    curr_time = int(time.time())
    # check if standup is active
    sql = "SELECT time_finish FROM project.active_data WHERE channel_id=(%s);"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is not None:
        time_finish = ret[0]
        if int(time_finish) > curr_time:
            db_connect.close()
            return {'is_active': True, 'time_finish': time_finish}

    # close database connection
    db_connect.close()

    return {'is_active': False, 'time_finish': None}


def standup_send(token, channel_id, message):
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # check channel id is valid
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s);"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: channel is not valid')

    # get member list
    member_list = ret[0]

    # check if the message longer than 1000
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters')
    exist_active = standup_active(token, channel_id)["is_active"]
    if not exist_active:
        raise InputError(description='error occurred: no standup is running in this channel')

    u_id = token_operation.get_uid(token)
    # check user is valid
    if u_id not in member_list:
        raise AccessError(description='error occurred: user is not a member of this channel')

    # get handle
    sql = "SELECT handle FROM project.user_data WHERE u_id=(%s)"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    handle = ret[0]

    # get msg from active buffer
    sql = "SELECT message FROM project.active_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    if ret[0] is not None:
        message_stand = ret[0]
        message_stand += "\n" + handle + ": " + message
    else:
        message_stand = handle + ": " + message

    # add to active data
    sql = "UPDATE project.active_data SET message=(%s) WHERE channel_id=(%s);"
    value = (message_stand, channel_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {}


############################
#     helper functions     #
############################
'''
def delete_finished_standup(channel_id):
    #global ACTIVE_DATA
    for channel in ACTIVE_DATA:
        if channel['channel_id'] < channel_id:
            ACTIVE_DATA.remove(channel)
'''


# def get_handle(u_id):
#     for user in USER_DATA:
#         if user["u_id"] == u_id:
#             return user["handle"]


def send_standup_message(channel_id):
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT standup_uid, time_finish, message FROM project.active_data where channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    if ret is not None:
        message = ret[2]
        if message is not None:

            standup_uid = ret[0]
            time_finish = ret[1]
        
            # send message
            sql = '''
            INSERT INTO project.message_data (channel_id, message, time_created, u_id, is_pinned, react_uid) 
            VALUES (%s, %s, %s, %s, %s, %s);
            '''
            value = (channel_id, message, time_finish, standup_uid, False, [])
            db_connect.execute(sql, value)

    # remove active
    sql = "DELETE FROM project.active_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    # for channel in ACTIVE_DATA:
    #     if channel['channel_id'] == channel_id:
    #         if channel['message'] != "":
    #             message_id = get_new_messageid()
    #             message_dict = {
    #                 'message_id': message_id,
    #                 'u_id': channel['standup_uid'],
    #                 'message': channel["message"],
    #                 'time_created': channel['time_finish'],
    #                 'is_pinned': False,
    #                 'reacts': [{'is_this_user_reacted': None, 'react_id': 1, 'u_ids': []}]
    #             }
    #             MESSAGES_DATA[channel_id].append(message_dict)
    #             MESSAGE_IDS[channel_id].append(message_id)
    #             channel['message'] = ""
    #         ACTIVE_DATA.remove(channel)
