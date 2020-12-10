from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid


def channel_invite(token: str, channel_id: int, u_id: int) -> dict:
    """
    Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately

    :param token: token of user who try to invite user
    :param channel_id: the id of channel which the user will be invited in
    :param u_id: uid of user who has been invited to join the channel
    :return: if it can successfully invite somebody to this channel,
             it will return an empty dictionary
    """

    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # check if channel id is valid
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT channel_id FROM project.channel_data WHERE channel_id = (%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: channel_id does not refer to a valid channel')

    # check if uid is valid
    sql = "SELECT u_id FROM project.user_data WHERE u_id = (%s)"
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    if ret is None:
        raise InputError(description='error occurred: u_id does not refer to a valid user')

    # check if the authorised user( is a member of the channel)
    authorised_uid = token_operation.get_uid(token)
    sql = "SELECT member, owner  FROM project.channel_data  WHERE channel_id =(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    member_list = ret[0]
    owner_list = ret[1]
    if authorised_uid not in member_list:
        raise AccessError(description='error occurred: the authorised user '
                                      'is not a member of the channel')

    # get flockr owner list
    sql = "SELECT owner FROM project.flockr_data;"
    db_connect.execute(sql)
    ret = db_connect.fetchone()
    flockr_list = ret[0]

    # if no error, add the user to the channel
    if u_id not in member_list:
        sql = "UPDATE project.channel_data SET member=(%s), owner=(%s) WHERE channel_id=(%s);"
        # if invite flockr, flockr will be owner
        if u_id in flockr_list:
            member_list.append(u_id)
            owner_list.append(u_id)
            value = (member_list, owner_list, channel_id)
        else:
            member_list.append(u_id)
            value = (member_list, owner_list, channel_id)
        db_connect.execute(sql, value)

    db_connect.close()

    return {
    }


def channel_details(token: str, channel_id: int) -> dict:
    """
    Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel

    :param token: user's token
    :param channel_id: channel's id
    :return: a dictionary with keys 'name', 'owner_members' and 'all_members'
    """
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # get the user's u_id from token
    u_id = token_operation.get_uid(token)

    # get info for the channel
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT * FROM project.channel_data  WHERE channel_id = (%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()
    # check if channel id invalid
    if len(ret) == 0:
        raise InputError(description='error occurred: the channel ID is not a valid channel')

    channel_name = ret[0][1]
    member_list = ret[0][2]
    owner_list = ret[0][3]
    # check if the authorised user is member of this channel
    if u_id not in member_list:
        raise AccessError(description='error occurred: the authorised user '
                                      'is not a member of channel with this channel_id')

    # get channel member basic information
    db_connect.cursor()
    sql = '''
    DROP TABLE IF EXISTS project.detail_data;
    CREATE TABLE project.detail_data
    (
        id   serial NOT NULL,
        u_id int
    );
    INSERT INTO project.detail_data(u_id)
    select unnest((
        SELECT member
        FROM project.channel_data
        WHERE channel_id = (%s)));
    SELECT u.u_id, name_last, name_first, profile_img_url
    FROM project.user_data u
    INNER JOIN project.detail_data d ON u.u_id = d.u_id
    ORDER BY d.id;
    '''
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()
    all_members = []
    # get member details
    for detail in ret:
        all_members.append({
            'u_id': detail[0],
            'name_last': detail[1],
            'name_first': detail[2],
            'profile_img_url': detail[3]
        })

    # get owner details
    owner_members = []
    for member in all_members:
        if member['u_id'] in owner_list:
            owner_members.append(member)

    # close database connection
    db_connect.close()

    details = {
        'name': channel_name,
        'owner_members': owner_members,
        'all_members': all_members
    }

    return details


def channel_messages(token: str, channel_id: int, start: int):
    """
    Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50"
    :param token: the authorised user's token
    :param channel_id: the channel ID
    :param start: the start number
    :return: dictionary of messages as required
    """
    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # start = int(start)
    # channel_id = int(channel_id)
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check channel_id is valid
    if ret is None:
        raise InputError(description='error occurred: channel id is not valid')
    member_list = ret[0]
    # get user's u_id from token
    u_id = token_operation.get_uid(token)
    # check u_id is a member for the channel
    if u_id not in member_list:
        raise AccessError(description='Authorised user is not a member of channel')

    # check start valid
    sql = "SELECT COUNT(*) FROM project.message_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    total_message = ret[0]
    # start is greater than the total number of messages
    if start > total_message:
        raise InputError(description='error occurred: start is greater than '
                                     'the total number of messages')

    # determine end
    retuen_end = -1
    if total_message > start + 50:
        end = start + 50
        retuen_end = end
    else:
        end = total_message

    # store all the required messages
    msg = []
    sql = "SELECT * FROM project.message_data WHERE channel_id=(%s) ORDER BY time_created DESC"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()
    for detail in ret:
        react_uid = detail[6]
        if u_id in react_uid:
            react_cond = True
        else:
            react_cond = False
        msg.append({
            'message_id': detail[0],
            'channel_id': detail[1],
            'time_created': detail[3],
            'u_id': detail[4],
            'message': detail[2],
            'is_pinned': detail[5],
            'reacts': [{
                'is_this_user_reacted': react_cond,
                'react_id': 1,
                'u_ids': react_uid
            }]
        })

    # close database connection
    db_connect.close()

    return {
        'messages': msg,
        'start': start,
        'end': retuen_end
    }


def channel_leave(token: str, channel_id: int):
    """
    Given a channel ID, the user removed as a member of this channel

    :param token: user's token
    :param channel_id: channel's id
    :return: if user leave the channel successfully, it will return an empty dictionary
    """

    # check token if valid
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member, owner FROM project.channel_data  WHERE channel_id = (%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check if the channel is valid
    if ret is None:
        raise InputError(description='error occurred: the channel ID is not a valid channel')
    member_list = ret[0]
    owner_list = ret[1]
    # check if the user is valid
    if u_id not in member_list:
        raise AccessError(description='error occurred: the authorised user '
                                      'is not a member of channel with this channel_id')

    # remove user from member_list
    member_list.remove(u_id)

    # if owner, remove from owner_list
    if u_id in owner_list:
        owner_list.remove(u_id)

    # UPDATE database
    db_connect.cursor()
    sql = "UPDATE project.channel_data SET member=(%s),owner=(%s) WHERE channel_id=(%s)"
    value = (member_list, owner_list, channel_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


def channel_join(token: str, channel_id: int) -> dict:
    """

    :param token:
    :param channel_id:
    :return:
    """

    # check token is valid
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occured: token is not valid')
    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    if not isinstance(channel_id, int):
        raise InputError(description='error occurred: channel ID is not valid')
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT is_public FROM project.channel_data  WHERE channel_id = (%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check channel is valid
    if ret is None:
        raise InputError(description='error occurred: channel ID is not valid')

    if ret[0] is False and not user_is_flockr_owner(u_id):
        raise AccessError(
            description='error occurred: channel ID refers to a private channel')

    sql = "SELECT member, owner FROM project.channel_data  WHERE channel_id = (%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    member_list = ret[0]
    owner_list = ret[1]

    # update database
    sql = "UPDATE project.channel_data SET member=(%s), owner=(%s) WHERE channel_id=(%s)"
    member_list.append(u_id)
    # if user is flockr then become onwer
    if user_is_flockr_owner(u_id):
        owner_list.append(u_id)

    value = (member_list, owner_list, channel_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


def channel_addowner(token: str, channel_id: int, u_id: int) -> dict:
    """
    Make user with user id u_id an owner of this channel

    :param token: user's token
    :param channel_id: channel's id
    :param u_id: user's id
    :return: an empty dictionary
    """

    # check
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # get authorised user's u_id from token
    authorised_uid = token_operation.get_uid(token)

    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT member, owner FROM project.channel_data WHERE channel_id=(%s)"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()
    # check channel is valid
    if ret is None:
        raise InputError(description='error occurred: Channel ID is not valid')

    member_list = ret[0]
    owner_list = ret[1]

    # user is already owner
    if u_id in owner_list:
        raise InputError(description='error occurred: user is already an owner of the channel')

    # check authorised_uid is valid
    if authorised_uid not in owner_list:
        raise AccessError(
            description='error occurred: the authorised user is not an owner of the flockr, '
                        'or an owner of this channel')

    # update database
    sql = "UPDATE project.channel_data SET member=(%s), owner=(%s) WHERE channel_id=(%s)"
    owner_list.append(u_id)
    if u_id not in member_list:
        member_list.append(u_id)
    value = (member_list, owner_list, channel_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


def channel_removeowner(token: str, channel_id: int, u_id: int) -> dict:
    """
    Remove user with user id u_id an owner of this channel

    :param token: user's token
    :param channel_id: channel's id
    :param u_id: user's id
    :return: an empty dictionary
    """

    # check token is valid
    token_operation = TokenJwt()
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    # get authorised user's u_id from token
    authorised_uid = token_operation.get_uid(token)

    # get owner_list
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT owner FROM project.channel_data WHERE channel_id=(%s);"
    value = (channel_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    # check channel is valid
    if ret is None:
        raise InputError(description='error occurred: Channel ID is not valid')

    # get owner_list
    owner_list = ret[0]

    # user not owner
    if u_id not in owner_list:
        raise InputError(description='error occurred: user is not an owner of the channel')

    # if not an owner
    if authorised_uid not in owner_list:
        raise AccessError(
            description='error occurred: the authorised user is not an owner of the flockr, '
                        'or an owner of this channel')

    # remove
    sql = "UPDATE project.channel_data SET owner=(%s) WHERE channel_id=(%s)"
    owner_list.remove(u_id)
    value = (owner_list, channel_id)
    db_connect.execute(sql, value)

    # close database connection
    db_connect.close()

    return {
    }


###############################
#       helper  functions     #
###############################
def user_is_flockr_owner(u_id):
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT owner FROM project.flockr_data"
    db_connect.execute(sql)
    owner_list = db_connect.fetchone()[0]
    if u_id in owner_list:
        return True
    return False
