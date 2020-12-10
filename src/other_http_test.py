import json
from time import sleep
import pytest
import requests
from httptest_helper import url, creatData
from other import clear


def test_clear(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel_1 = test_data.creat_channel(boyu_dict['token'], 'team_1', True)
    resp_message = requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hello1"
    })
    json.loads(resp_message.text)
    #claer
    resp_clear = requests.delete(url + 'clear', params={})
    users_dict = json.loads(resp_clear.text)
    # test user data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    channel_1 = test_data.creat_channel(boyu_dict['token'], 'team_1', True)
    # add one message to 1 channel
    resp_message1 = requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hello!!!"
    })
    id_1 = json.loads(resp_message1.text)
    # check details in users_dict
    resp_users = requests.get(url + 'users/all', params={'token': boyu_dict['token']})
    users_dict = json.loads(resp_users.text)
    assert len(users_dict['users']) == 2
    assert len(users_dict['users'][0].keys()) == 6
    assert users_dict['users'][0]['u_id'] == boyu_dict['u_id']
    assert users_dict['users'][0]['email'] == 'cbyisaac@gmail.com'
    assert users_dict['users'][0]['name_first'] == 'Boyu'
    assert users_dict['users'][0]['name_last'] == 'Cai'
    assert len(users_dict['users'][0]['handle_str']) <= 20
    #test channels data
    requests.post(url + 'channels/create', json={
        'token': boyu_dict['token'],
        'name': 'name1',
        'is_public': False
    })
    channels_listall_re_1 = requests.get(url + 'channels/listall', params={
        'token': wenyao_dict['token']
    })
    listall_dict_1 = json.loads(channels_listall_re_1.text)
    channels_listall_re_2 = requests.get(url + 'channels/listall', params={
        'token': boyu_dict['token']
    })
    listall_dict_2 = json.loads(channels_listall_re_2.text)
    assert listall_dict_1 == listall_dict_2
    #test messages data
    resp_search = requests.get(url + 'search', params={
        'token': boyu_dict['token'],
        'query_str': "hello"
    })
    search_result = json.loads(resp_search.text)
    assert len(search_result['messages']) == 1
    assert search_result['messages'][0]["message"] == 'hello!!!'
    assert search_result['messages'][0]["u_id"] == boyu_dict['u_id']
    assert search_result['messages'][0]["message_id"] == id_1['message_id']


# test invalid token in users all
def test_users_all_token_invalid(url):
    clear()
    test_data = creatData(url)
    test_data.register_user('cbyisaac@gmail.com', 'boyupass', 'Boyu',
                            'Caiiiiiiiiiiiiiiiii')
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'users/all', params={"token": "invalid.token"}).raise_for_status()


# test the data stored for users_all function
def test_users_all(url):
    clear()
    test_data = creatData(url)
    boyu1_dict = test_data.register_user('cbyisaac@gmail.com', 'boyupass', 'Boyu',
                                         'Caiiiiiiiiiiiiiiiii')
    boyu2_dict = test_data.register_user('isaac@gmail.com', 'boyupass', 'Boyu',
                                         'Caiiiiiiiiiiiiiiiii')
    resp_users = requests.get(url + 'users/all', params={'token': boyu1_dict['token']})
    users_dict = json.loads(resp_users.text)
    # check details in users_dict
    assert len(users_dict['users']) == 2
    assert len(users_dict['users'][0].keys()) == 6
    assert len(users_dict['users'][1].keys()) == 6
    assert users_dict['users'][0]['u_id'] == boyu1_dict['u_id']
    assert users_dict['users'][0]['email'] == 'cbyisaac@gmail.com'
    assert users_dict['users'][0]['name_first'] == 'Boyu'
    assert users_dict['users'][0]['name_last'] == 'Caiiiiiiiiiiiiiiiii'
    assert len(users_dict['users'][0]['handle_str']) <= 20
    assert users_dict['users'][1]['u_id'] == boyu2_dict['u_id']
    assert users_dict['users'][1]['email'] == 'isaac@gmail.com'
    assert users_dict['users'][1]['name_first'] == 'Boyu'
    assert users_dict['users'][1]['name_last'] == 'Caiiiiiiiiiiiiiiiii'
    assert len(users_dict['users'][1]['handle_str']) <= 20
    assert users_dict['users'][1]['handle_str'] != users_dict['users'][0]['handle_str']


# test user is not member
def test_admin_userpermission_change_not_member(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'admin/userpermission/change', json={
            'token': boyu_dict['token'],
            'u_id': -1,
            'permission_id': 1
        }).raise_for_status()


# test permission is wrong
def test_admin_userpermission_invalid_permission_id(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'admin/userpermission/change', json={
            'token': boyu_dict['token'],
            'u_id': boyu_dict['u_id'],
            'permission_id': 1.5
        }).raise_for_status()


# test admin is not owner
def test_admin_userpermission_not_owner(url):
    clear()
    test_data = creatData(url)
    test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'admin/userpermission/change', json={
            'token': wenyao_dict['token'],
            'u_id': wenyao_dict['u_id'],
            'permission_id': 2
        }).raise_for_status()


# test admin_userpermission_change
def test_admin_userpermission_change(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    channel_dict = test_data.creat_channel(boyu_dict['token'], 'team_1', True)
    # invite a new user to the channel
    resp_channel_invite = requests.post(url + 'channel/invite', json={
        'token': boyu_dict['token'],
        'channel_id': channel_dict['channel_id'],
        'u_id': wenyao_dict['u_id']
    })
    channel_invite = json.loads(resp_channel_invite.text)
    assert channel_invite == {}
    # add that user as flockr owner
    resp_users1 = requests.post(url + 'admin/userpermission/change', json={
        'token': boyu_dict['token'],
        'u_id': wenyao_dict['u_id'],
        'permission_id': 1
    })
    user_dict1 = json.loads(resp_users1.text)
    assert user_dict1 == {}
    # check is the new added flockr owner has the channel owner's premission
    resp_channel_removeowner = requests.post(url + 'channel/removeowner', json={
        'token': wenyao_dict['token'],
        'channel_id': channel_dict['channel_id'],
        'u_id': boyu_dict['u_id']
    })
    channel_removeowner = json.loads(resp_channel_removeowner.text)
    assert channel_removeowner == {}
    # check if the channel_details are correct
    resp_channel_details = requests.get(url + 'channel/details', params={
        'token': wenyao_dict['token'],
        'channel_id': channel_dict['channel_id']
    })
    channel_details = json.loads(resp_channel_details.text)
    assert channel_details == {
        'name': 'team_1',
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


# test the search message from the same channel
def test_search_message(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel_1 = test_data.creat_channel(boyu_dict['token'], 'team_1', True)
    # add 3 messages to 1 channel
    resp_message1 = requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hello!!!"
    })
    requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "h_e_l_l_o"
    })
    requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hi there"
    })
    id_1 = json.loads(resp_message1.text)
    # test the data returned by search
    resp_search = requests.get(url + 'search', params={
        'token': boyu_dict['token'],
        'query_str': "hello"
    })
    search_result = json.loads(resp_search.text)
    assert len(search_result['messages']) == 1
    assert search_result['messages'][0]["message"] == 'hello!!!'
    assert search_result['messages'][0]["u_id"] == boyu_dict['u_id']
    assert search_result['messages'][0]["message_id"] == id_1['message_id']


# test the search message between different channels
def test_search_message_different_channels(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel_1 = test_data.creat_channel(boyu_dict['token'], 'team_1', True)
    channel_2 = test_data.creat_channel(boyu_dict['token'], 'team_2', True)
    # send a message including hello to channel1
    requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hello1"
    })
    sleep(1)
    # send a message including hello to channel2
    requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_2['channel_id'],
        'message': "hello2"
    })
    sleep(1)
    # send another message including hello to channel1
    requests.post(url + 'message/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel_1['channel_id'],
        'message': "hello3"
    })
    sleep(1)
    resp_search = requests.get(url + 'search', params={
        'token': boyu_dict['token'],
        'query_str': "hello"
    })
    search_result = json.loads(resp_search.text)
    assert len(search_result['messages']) == 3
    assert search_result['messages'][0]['message'] == 'hello3'
    assert search_result['messages'][1]['message'] == 'hello2'
    assert search_result['messages'][2]['message'] == 'hello1'



def test_admin_user_remove(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    res = requests.delete(url + 'admin/user/remove', json={
        'token': boyu_dict['token'],
        'u_id': wenyao_dict['u_id'],
    })
    assert res.status_code == 200