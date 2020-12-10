import json
import pytest
import requests
from httptest_helper import creatData, url
from other import clear


# test the case that the input token is invalid for channels/creates
def test_channels_create_invalid_token(url):
    clear()
    creatData(url)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channels/create', json={
            'token': "INVALIDHHH",
            'name': 'name1',
            'is_public': True
        }).raise_for_status()


# test the case that name is more than 20 characters long
def test_channels_create_longername(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channels/create', json={
            'token': boyu_dict['token'],
            'name': 'namelongerthan20characters',
            'is_public': True
        }).raise_for_status()


# test if the channel id returned by test_channels is an integer
def test_channels_create_return_value(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel_create = requests.post(url + 'channels/create', json={
        'token': boyu_dict['token'],
        'name': 'name1',
        'is_public': True
    })
    channel_dict = json.loads(channel_create.text)
    assert isinstance(channel_dict['channel_id'], int)


# test if the data for the new channel store successfully
def test_channels_create_store(url):
    clear()
    # create data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # call the channels list all
    channels_listall_pre = requests.get(url + 'channels/listall', params={
        'token': boyu_dict['token']
    })
    channels_dict_1 = json.loads(channels_listall_pre.text)
    before_1 = len(channels_dict_1['channels'])
    requests.post(url + 'channels/create', json={
        'token': boyu_dict['token'],
        'name': 'Team002',
        'is_public': True
    })
    # sending request to recevie all the channels
    channels_list_re = requests.get(url + 'channels/listall', params={
        'token': boyu_dict['token']
    })
    list_dict = json.loads(channels_list_re.text)
    after_1 = len(list_dict['channels'])
    assert (after_1 - before_1) == 1


# test the case that the input token is invalid for channels/list
def test_channels_list_invalid_token(url):
    clear()
    creatData(url)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channels/list', json={
            'token': 'nana'
        }).raise_for_status()


# test the case that the authorised user haven't joined any channels
def test_channels_list_havent_join_channels(url):
    clear()
    data = creatData(url)
    user1_dict = data.register_wenyao()
    channels_listall_re = requests.get(url + 'channels/listall', params={
        'token': user1_dict['token']
    })
    listall_dict = json.loads(channels_listall_re.text)
    assert len(listall_dict['channels']) == 0


# check the correct output for channel list
def test_channels_list_output(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    test_data.creat_channel(wenyao_dict['token'], 'TeamAlfa', True)
    test_data.creat_channel(wenyao_dict['token'], 'AlfaTarui', True)
    test_data.creat_channel(wenyao_dict['token'], 'DC_world', True)
    # input data
    channels_list_re = requests.get(url + 'channels/list', params={
        'token': wenyao_dict['token']
    })
    # sending request
    list_dict = json.loads(channels_list_re.text)
    assert isinstance(list_dict, dict)


# test the case that the authorised user joined some of the channels
def test_channels_list_join_some_channels(url):
    clear()
    data = creatData(url)
    user1_dict = data.register_wenyao()
    user2_dict = data.register_boyu()
    # get channels for user1 and user2
    channels_list_1 = requests.get(url + 'channels/list', params={
        'token': user1_dict['token']
    })
    list_wenyao_pre = json.loads(channels_list_1.text)
    channels_list_2 = requests.get(url + 'channels/list', params={
        'token': user2_dict['token']
    })
    list_boyu_pre = json.loads(channels_list_2.text)
    # create 2 channels
    name1_dict = data.creat_channel(user1_dict['token'], 'TeamOrange', True)
    name2_dict = data.creat_channel(user2_dict['token'], 'TeamGrape', True)
    team_orange_id = name1_dict['channel_id']
    team_grape_id = name2_dict['channel_id']
    # append the new added channel to the previous channels respectively
    team_orange_dict = {'channel_id': team_orange_id, 'name': 'TeamOrange'}
    team_grape_dict = {'channel_id': team_grape_id, 'name': 'TeamGrape'}
    list_wenyao_pre['channels'].append(team_orange_dict)
    list_boyu_pre['channels'].append(team_grape_dict)
    # get the current list of channel for the user1 and user2
    channels_list_3 = requests.get(url + 'channels/list', params={
        'token': user1_dict['token']
    })
    list_wenyao_aft = json.loads(channels_list_3.text)
    channels_list_4 = requests.get(url + 'channels/list', params={
        'token': user2_dict['token']
    })
    list_boyu_aft = json.loads(channels_list_4.text)
    # check if list are same
    assert list_boyu_aft == list_boyu_pre
    assert list_wenyao_aft == list_wenyao_pre


# test the case that the input token is invalid for channels/listall
def test_channels_listall_invalid_token(url):
    clear()
    creatData(url)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channels/listall', json={
            'token': 'nana'
        }).raise_for_status()


# test the case that the authorised user haven't joined any channels
def test_channels_listall_havent_join_channels(url):
    clear()
    data = creatData(url)
    user1 = data.register_boyu()
    user2 = data.register_wenyao()
    requests.post(url + 'channels/create', json={
        'token': user1['token'],
        'name': 'name1',
        'is_public': False
    })
    channels_listall_re_1 = requests.get(url + 'channels/listall', params={
        'token': user2['token']
    })
    listall_dict_1 = json.loads(channels_listall_re_1.text)
    channels_listall_re_2 = requests.get(url + 'channels/listall', params={
        'token': user1['token']
    })
    listall_dict_2 = json.loads(channels_listall_re_2.text)
    assert listall_dict_1 == listall_dict_2


# check outcome for listall function
def test_channels_listall(url):
    clear()
    data = creatData(url)
    user1_dict = data.register_wenyao()
    data.creat_channel(user1_dict['token'], 'Teambana', True)
    data.creat_channel(user1_dict['token'], 'Teamcaa', True)
    user2_dict = data.register_boyu()
    data.creat_channel(user2_dict['token'], 'Teamimposter', True)
    channels_listall_re = requests.get(url + 'channels/listall', params={
        'token': user2_dict['token']
    })
    # sending request
    listall_dict = json.loads(channels_listall_re.text)
    # assert isinstance(listall_dict)
    assert len(listall_dict['channels']) == 3


def test_channels_listall_joined(url):
    clear()
    data = creatData(url)
    user1_dict = data.register_wenyao()
    user2_dict = data.register_boyu()
    channels_list_3 = requests.get(url + 'channels/listall', params={
        'token': user2_dict['token']
    })
    list_boyu_pre = json.loads(channels_list_3.text)
    # channels create by other user
    # create channel one
    channel_create_1 = requests.post(url + 'channels/create', json={
        'token': user1_dict['token'],
        'name': 'TeamAMG',
        'is_public': False
    })
    name1_dict = json.loads(channel_create_1.text)
    team_amg_id = name1_dict['channel_id']
    team_amg_dict = {'channel_id': team_amg_id, 'name': 'TeamAMG'}
    # add channel to the list
    list_boyu_pre['channels'].append(team_amg_dict)
    # create second channel
    channel_create_2 = requests.post(url + 'channels/create', json={
        'token': user1_dict['token'],
        'name': 'TeamRS',
        'is_public': False
    })
    name2_dict = json.loads(channel_create_2.text)
    team_rs_id = name2_dict['channel_id']
    team_rs_dict = {'channel_id': team_rs_id, 'name': 'TeamRS'}
    # add channel into list
    list_boyu_pre['channels'].append(team_rs_dict)
    # list the current channels
    channels_listall_2 = requests.get(url + 'channels/listall', params={
        'token': user2_dict['token']
    })
    list_boyu_aft = json.loads(channels_listall_2.text)
    # assert the channels pre and current
    assert list_boyu_pre == list_boyu_aft
