from time import sleep
import pytest
from channels import channels_create, channels_listall, channels_list
from message import message_send
from other import clear, users_all, admin_userpermission_change, search, admin_user_remove
from error import InputError, AccessError
from channel import channel_invite, channel_details, channel_removeowner
from auth import auth_register


def initialise_data():
    clear()
    boyu_dict = auth_register('123@gmail.com', 'boyupass', 'Boyu', 'Cai')
    wenyao_dict = auth_register('427@gmail.com', 'wenyaopass', 'Wenyao', 'Chen')
    return boyu_dict, wenyao_dict


#test clear correctly
def test_clear():
    boyu_dict, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    id_1 = message_send(boyu_dict['token'], channel_1['channel_id'], '1')
    message_send(boyu_dict['token'], channel_1['channel_id'], '2')
    message_send(boyu_dict['token'], channel_1['channel_id'], '3')
    # clear original data
    clear()
    # initialise data
    boyu_dict, _ = initialise_data()
    users_dict = users_all(boyu_dict['token'])
    # check user details already update
    assert len(users_dict['users']) == 2
    assert users_dict['users'][0]['u_id'] == boyu_dict['u_id']
    assert users_dict['users'][0]['email'] == '123@gmail.com'
    assert users_dict['users'][0]['name_first'] == 'Boyu'
    assert users_dict['users'][0]['name_last'] == 'Cai'
    # check channels list is already update
    channel_1_id = channels_create(boyu_dict['token'], 'channel_1', True)
    assert channels_listall(boyu_dict['token']) == channels_list(boyu_dict['token'])
    # send two message in a channel
    id_1 = message_send(boyu_dict['token'], channel_1_id['channel_id'], 'hello!')
    message_send(boyu_dict['token'], channel_1_id['channel_id'], 'he_llo')
    message_send(boyu_dict['token'], channel_1_id['channel_id'], 'hi there')
    search_result = search(boyu_dict['token'], "hello")
    # search message order is correct
    assert len(search_result['messages']) == 1
    assert search_result['messages'][0]["message"] == 'hello!'
    assert search_result['messages'][0]["u_id"] == boyu_dict['u_id']
    assert search_result['messages'][0]["message_id"] == id_1['message_id']


# test if the user all return the correct data
def test_users_all():
    boyu_token, _ = initialise_data()
    users_dict = users_all(boyu_token['token'])
    assert len(users_dict['users']) == 2
    assert users_dict['users'][0]['u_id'] == boyu_token['u_id']
    assert users_dict['users'][0]['email'] == '123@gmail.com'
    assert users_dict['users'][0]['name_first'] == 'Boyu'
    assert users_dict['users'][0]['name_last'] == 'Cai'


def test_users_all_invalid_token():
    initialise_data()
    with pytest.raises(AccessError):
        assert users_all("invalid.token")


# user is not in member
def test_admin_userpermission_input_error_invalid_uid():
    boyu_dict, _ = initialise_data()
    with pytest.raises(InputError):
        assert admin_userpermission_change(boyu_dict['token'], -1, 1)


# check permission is wrong
def test_admin_userpermission_inputerror_invalid_permission_id():
    boyu_dict, _ = initialise_data()
    with pytest.raises(InputError):
        assert admin_userpermission_change(boyu_dict['token'], boyu_dict['u_id'], 1.5)


# test admin is not owner for admin_userpermission
def test_admin_userpermission_accesserror_not_owner():
    _, wenyao_dict = initialise_data()
    with pytest.raises(AccessError):
        assert admin_userpermission_change(wenyao_dict['token'], wenyao_dict['u_id'], 2)


# test invalid token for admin_userpermission
def test_permission_token_not_valid():
    _, wenyao_dict = initialise_data()
    with pytest.raises(AccessError):
        assert admin_userpermission_change("invalid.token", wenyao_dict['u_id'], 1)


# test the case that change a user's permission form 2 to 1
def test_admin_userpermission_change_2to1():
    boyu_dict, wenyao_dict = initialise_data()
    admin_userpermission_change(boyu_dict['token'], wenyao_dict['u_id'], 1)
    # create a channel and add the new flockr owner as a member
    channel = channels_create(boyu_dict['token'], "team1", True)
    channel_id = channel['channel_id']
    channel_invite(boyu_dict['token'], channel_id, wenyao_dict['u_id'])
    # check if the new flockr owner has owner permission in the channel
    channel_removeowner(wenyao_dict['token'], channel_id, boyu_dict['u_id'])
    assert channel_details(wenyao_dict['token'], channel_id) == {
        'name': 'team1',
        'owner_members': [
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
    }


# test the case that user does not have permission to change other's permission
def test_admin_userpermission_no_permission():
    boyu_dict, wenyao_dict = initialise_data()
    admin_userpermission_change(boyu_dict['token'], wenyao_dict['u_id'], 1)
    admin_userpermission_change(boyu_dict['token'], wenyao_dict['u_id'], 2)
    # create a channel and add the new flockr owner as a member
    channel = channels_create(boyu_dict['token'], "team1", True)
    channel_id = channel['channel_id']
    channel_invite(boyu_dict['token'], channel_id, wenyao_dict['u_id'])
    # check if the user has owner permission in the channel
    with pytest.raises(AccessError):
        assert channel_removeowner(wenyao_dict['token'], channel_id, boyu_dict['u_id'])


# test the case that change a user's permission form 1 to 2
def test_admin_userpermission_1to2():
    boyu_dict, wenyao_dict = initialise_data()
    # create a channel and add the new flockr owner as a member
    channel = channels_create(boyu_dict['token'], "team1", True)
    channel_id = channel['channel_id']
    channel_invite(boyu_dict['token'], channel_id, wenyao_dict['u_id'])
    # check if the new flockr owner has owner permission in the channel
    admin_userpermission_change(boyu_dict['token'], wenyao_dict['u_id'], 1)
    # check the data returned by channel_details
    # the new flockr owner should become the channel owner as well
    assert channel_details(wenyao_dict['token'], channel_id) == {
        'name': 'team1',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
    }


# test search_messages
def test_search_message():
    boyu_dict, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    id_1 = message_send(boyu_dict['token'], channel_1['channel_id'], 'hello!')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'he_llo')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hi there')

    search_result = search(boyu_dict['token'], "hello")
    assert len(search_result['messages']) == 1
    assert search_result['messages'][0]["message"] == 'hello!'
    assert search_result['messages'][0]["u_id"] == boyu_dict['u_id']
    assert search_result['messages'][0]["message_id"] == id_1['message_id']


# test invlaid token for search()
def test_search_invalid_token():
    boyu_dict, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    with pytest.raises(AccessError):
        assert search("invalid.token", 'hello1')


# test the case that sending messages with same query_str from different channels
def test_search_message_different_channels():
    boyu_dict, _ = initialise_data()
    # creat 3 channels
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    channel_2 = channels_create(boyu_dict['token'], 'channel_2', True)
    # send a message including "hello" in channel 1
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    sleep(1)
    # send a message including "hello" in channel 2
    message_send(boyu_dict['token'], channel_2['channel_id'], 'hello2')
    sleep(1)
    # send another message including "hello" in channel 1
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello3')
    sleep(1)
    search_result = search(boyu_dict['token'], "hello")
    assert search_result['messages'][0]["message"] == 'hello3'
    assert search_result['messages'][1]["message"] == 'hello2'
    assert search_result['messages'][2]["message"] == 'hello1'



# user is not member for admin_user_remove
def test_remove_invalid_uid():
    boyu_dict, _ = initialise_data()
    with pytest.raises(InputError):
        assert admin_user_remove(boyu_dict['token'], -1)


# test admin is not owner for admin_user_remove
def test_remove_not_owner():
    _, wenyao_dict = initialise_data()
    with pytest.raises(AccessError):
        assert admin_user_remove(wenyao_dict['token'], wenyao_dict['u_id'])


# test invalid token or admin_user_remove
def test_remove_token_not_valid():
    _, wenyao_dict = initialise_data()
    with pytest.raises(AccessError):
        assert admin_user_remove("invalid.token", wenyao_dict['u_id'])


# test if the user all return the correct data
def test_remove():
    boyu_dict, wenyao_dict = initialise_data()
    admin_user_remove(boyu_dict['token'], wenyao_dict['u_id'])
    users_dict = users_all(boyu_dict['token'])
    assert len(users_dict['users']) == 1
    assert users_dict['users'][0]['u_id'] == boyu_dict['u_id']
    assert users_dict['users'][0]['email'] == '123@gmail.com'
    assert users_dict['users'][0]['name_first'] == 'Boyu'
    assert users_dict['users'][0]['name_last'] == 'Cai'