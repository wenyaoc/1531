from db_connector import DbConnector
from error import InputError, AccessError
from helper import TokenJwt, check_valid


def channels_list(token: str) -> dict:
    """
    Provide a list of all channels (and their associated details)
    that the authorised user is part of

    :param token: user's token
    :return: dictionary of list of dictionary with keys 'channel_id' and 'name'
            which includes the channels that the user is a part of
    """
    dictionary = {'channels': [], }

    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    # get user's u_id from token
    u_id = token_operation.get_uid(token)

    # get info in database
    db_connect = DbConnector()
    db_connect.cursor()
    sql = '''
    SELECT channel_id, name 
    FROM project.channel_data c 
            INNER JOIN project.user_data u ON u.u_id = ANY (c.member) 
    WHERE u.u_id = (%s);
    '''
    value = (u_id,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchall()

    for channel in ret:
        dictionary["channels"].append({
            'channel_id': channel[0],
            'name': channel[1]
        })

    db_connect.close()

    return dictionary


def channels_listall(token: str) -> dict:
    """
    Provide a list of all channels (and their associated details)

    :param token: user's token
    :return: dictionary of list of dictionary with keys 'channel_id' and 'name'
            which includes all the channels
    """
    #token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')

    dictionary = {'channels': [], }

    # get info for all list
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT channel_id, name FROM project.channel_data"
    db_connect.execute(sql)
    ret = db_connect.fetchall()

    for channel in ret:
        dictionary['channels'].append({
            'channel_id': channel[0],
            'name': channel[1]
        })

    # close database connection
    db_connect.close()

    return dictionary


def channels_create(token: str, name: str, is_public: bool) -> dict:
    """
    Creates a new channel with that name that is either a public or private channel

    :param token: user's token
    :param name: channel's name
    :param is_public: boolean expression of whether the channel is public or private
    :return: the dictionary with key 'channel_id'
    """

    token_operation = TokenJwt()
    # check if the token is valid
    if check_valid(token) is False:
        raise AccessError(description='error occurred: token is not valid')
    if len(name) > 20:
        raise InputError(description='error occurred: Name is more than 20 characters long')

    u_id = token_operation.get_uid(token)
    #
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "INSERT INTO project.channel_data(name, member, owner,is_public) VALUES (%s,%s, %s, %s);"
    value = (name, [u_id], [u_id], is_public)
    db_connect.execute(sql, value)

    # get the channel_id
    sql = "SELECT MAX(channel_id) FROM project.channel_data"
    db_connect.execute(sql)
    ret = db_connect.fetchone()
    channel_id = ret[0]

    return {
        'channel_id': channel_id,
    }
