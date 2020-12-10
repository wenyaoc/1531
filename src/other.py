import copy
# from data import USER_DATA, CHANNEL_DATA, MESSAGES_DATA, \
#      FLOCKR_DATA, MESSAGE_IDS, ACTIVE_DATA
from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid


# LEN_USER = len(USER_DATA)
# LEN_CHANNEL = len(CHANNEL_DATA)
# LEN_ACTIVE = len(ACTIVE_DATA)
# LEN_FLOCKR_OWNER = len(FLOCKR_DATA['owner'])
# LEN_FLOCKR_MEM = len(FLOCKR_DATA['member'])
# MESSAGES_COPY = copy.deepcopy(MESSAGES_DATA)
# MESSAGE_ID_COPY = copy.deepcopy(MESSAGE_IDS)


# class CurrData:
#     def __init__(self, USER_DATA, CHANNEL_DATA, FLOCKR_DATA):
#         self.curr_user = len(USER_DATA)
#         self.curr_channel = len(CHANNEL_DATA)
#         self.curr_messages = len(MESSAGES_DATA)
#         self.curr_flockr_owner = len(FLOCKR_DATA['owner'])
#         self.curr_flockr_mem = len(FLOCKR_DATA['member'])


def clear() -> None:
    """

    :return:
    """
    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    truncate table 
    project.user_data, project.channel_data, project.message_data, project.flockr_data, project.active_data
    restart identity;
    '''
    db_connect.execute(sql)
    db_connect.close()


def users_all(token) -> dict:
    """

    :param token:
    :return:
    """
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    users = {'users': []}
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT u_id, email, name_first, name_last,\
            handle, profile_img_url FROM project.user_data;"
    db_connect.execute(sql)
    ret = db_connect.fetchall()
    for user in ret:
        users['users'].append({
            'u_id': user[0],
            'email': user[1],
            'name_first': user[2],
            'name_last': user[3],
            'handle_str': user[4],
            'profile_img_url': user[5]
        })

    # close database connection
    db_connect.close()

    return users


def admin_userpermission_change(token, u_id, permission_id):
    # get owner's u_id from token
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT u_id FROM project.user_data WHERE u_id=(%s)"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check u_id is valid
    if ret is None:
        raise InputError(description='error occurred: u_id does not refer to a valid user')

    # if permission_id != 1 and permission_id != 2
    if permission_id not in (1, 2):
        raise InputError(description='error occurred: permission_id does not '
                                     'refer to a value permission')

    sql = "SELECT owner FROM project.flockr_data;"
    db_connect.execute(sql)
    ret = db_connect.fetchone()
    owner_list = ret[0]
    # get id from token
    owner_id = token_operation.get_uid(token)
    # check the authorised user is a flockr
    if owner_id not in owner_list:
        raise AccessError(description='error occurred: The authorised user '
                                      'is not an admin or owner')

    # if permission_id is 1 make sure User in owner list
    if permission_id == 1 and u_id not in owner_list:
        owner_list.append(u_id)
        sql = "UPDATE project.flockr_data SET owner=(%s)"
        value = (owner_list,)
        db_connect.execute(sql, value)
    elif permission_id == 2 and u_id in owner_list:
        owner_list.remove(u_id)
        sql = "UPDATE project.flockr_data SET owner=(%s)"
        value = (owner_list,)
        db_connect.execute(sql, value)
    # update all channel members to channel owner
    sql = "SELECT owner FROM project.channel_data WHERE (%s) = ANY(member)"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()

    for owner in ret:
        if u_id not in owner[0]:
            owner[0].append(u_id)
        sql = "UPDATE project.channel_data SET owner=(%s) WHERE (%s) = ANY(member)"
        value = (owner[0], u_id)
        db_connect.execute(sql, value)

    # close database connection
    db_connect.close()


def search(token, query_str):
    search_list = []
    # get user's u_id from token
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # get u_idz
    u_id = token_operation.get_uid(token)

    # search
    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    SELECT message_id, m.channel_id, u_id, message, time_created
    FROM project.message_data m
            JOIN project.channel_data c
                ON (%s) = ANY (c.member)
    WHERE message LIKE (%s)
        AND c.channel_id = m.channel_id
    ORDER BY time_created DESC;
    '''
    value = (u_id, '%' + query_str + '%')
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()

    for msg in ret:
        search_list.append({
            'message_id': msg[0],
            'channel_id': msg[1],
            'u_id': msg[2],
            'message': msg[3],
            'time_created': msg[4]
        })

    # close database connection
    db_connect.close()
    return {
        'messages': search_list
    }


def admin_user_remove(token, u_id):
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT u_id FROM project.user_data WHERE u_id=(%s)"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='u_id does not refer to a valid user'
                                     'AccessError whenThe authorised user '
                                     'is not an owner of the flockr')

    token_operation = TokenJwt()
    authorised_uid = token_operation.get_uid(token)
    sql = "SELECT owner FROM project.flockr_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()
    owner_list = []
    if ret is not None:
        owner_list = ret[0]
    if authorised_uid not in owner_list:
        raise AccessError(description='The authorised user is not '
                                      'an owner of the flockr')

    # # remove
    sql = '''
    DELETE FROM project.user_data WHERE u_id=(%s);
    DELETE FROM project.message_data WHERE u_id=(%s);
    '''
    value = (u_id, u_id)
    db_connect.execute(sql, value)

    # remove from channel
    sql = '''
    SELECT member, owner
    FROM project.channel_data c
    WHERE (%s) = ANY(member)
    '''
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()

    for temp_ret in ret:
        list_member = temp_ret[0]
        list_owner = temp_ret[1]
        list_member.remove(u_id)
        try:
            list_owner.remove(u_id)
        except ValueError:
            pass
        sql = '''
            UPDATE project.channel_data SET member=(%s), owner=(%s);
            '''
        value = (list_member, list_owner)
        db_connect.execute(sql, value)

    try:
        owner_list.remove(u_id)
    except:
        pass
    sql = "UPDATE project.flockr_data SET owner=(%s)"
    value = (owner_list,)
    db_connect.execute(sql, value)

    db_connect.close()

    return {}
