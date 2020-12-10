import json
import time
import pytest
import requests
from httptest_helper import url, creatData
from other import clear


# test token is not valid
def test_standup_start_token_not_valid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # give invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/start', json={
            'token': "invalid_token",
            'channel_id': channel['channel_id'],
            'length': 1
        }).raise_for_status()


# test standup start channel Id is invalid
def test_standup_start_channel_id_invalid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    test_data.creat_channel(boyu_dict['token'], 'team1', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/start', json={
            'token': boyu_dict['token'],
            'channel_id': -1,
            'length': 1
        }).raise_for_status()


# test standup already run
def test_standup_start_already_run(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # start stabdup
    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 5
    })
    # start standup again
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/start', json={
            'token': boyu_dict['token'],
            'channel_id': channel['channel_id'],
            'length': 5
        }).raise_for_status()


#test standup start is pass
def test_standup_start(url):
    clear()
    #initialise data
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team2', True)

    resp_standup_start = requests.post(url + 'standup/start', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 5
    })
    #test standup message is not same with send message
    standup_dict = json.loads(resp_standup_start.text)
    assert isinstance(standup_dict['time_finish'], int)


# test token is not valid
def test_standup_active_token_not_valid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # give invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'standup/active', params={
            'token': "invalid_token",
            'channel_id': channel['channel_id'],
        }).raise_for_status()


#test channel id is not valid
def test_standup_active_channel_id_invalid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'standup/active', params={
            'token': boyu_dict['token'],
            'channel_id': -1,
        }).raise_for_status()


def test_standup_active(url):
    clear()
    #initialise data
    test_data = creatData(url)
    weiqiang_dict = test_data.register_weiqiang()
    channel = test_data.creat_channel(weiqiang_dict['token'], 'team3', True)
    requests.post(url + 'standup/start', json={
        "token": weiqiang_dict["token"],
        "channel_id": channel["channel_id"],
        'length': 10
    })
    resp_standup_active = requests.get(url + 'standup/active', params={
        "token": weiqiang_dict["token"],
        "channel_id": channel["channel_id"]
    })

    active_data = json.loads(resp_standup_active.text)
    assert active_data['is_active'] is True


# test token is not valid
def test_standup_send_token_not_valid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # give invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/send', json={
            'token': "invalid_token",
            'channel_id': channel['channel_id'],
            'message': "hello"
        }).raise_for_status()


def test_standup_send_channel_id_invalid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 1
    })

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/send', json={
            'token': boyu_dict['token'],
            'channel_id': -1,
            'message': "hello"
        }).raise_for_status()


def test_standup_send_message_too_long(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)

    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 5
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/send', json={
            'token': boyu_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "hello"*1001
        }).raise_for_status()


#test user not channel memmber
def test_standup_send_not_member(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)

    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 1
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/send', json={
            'token': wenyao_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "hello"
        }).raise_for_status()


#test standup is inactive
def test_standup_send_inactive(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'standup/send', json={
            'token': boyu_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "hello"
        }).raise_for_status()


def test_standup_send(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # start standup
    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 5
    })
    # send a message
    resp_srtandup_send = requests.post(url + 'standup/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    #test standup message is not same with send message
    send_dict = json.loads(resp_srtandup_send.text)
    assert send_dict == {}


def test_standup_whole(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(boyu_dict['token'], 'team1', True)
    # start standup
    requests.post(url + 'standup/start', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'length': 4
    })
    # send a message
    requests.post(url + 'standup/send', json={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    # time sleep for 5s
    time.sleep(5)
    # check if the standup is active
    resp_standup_active = requests.get(url + 'standup/active', params={
        "token": boyu_dict["token"],
        "channel_id": channel["channel_id"]
    })
    active_data = json.loads(resp_standup_active.text)
    assert active_data['is_active'] is False
    # get the return value of channel_messages
    resp_channel_messages = requests.get(url + '/channel/messages', params={
        'token': boyu_dict['token'],
        'channel_id': channel['channel_id'],
        'start' : 0
    })
    messages_dict = json.loads(resp_channel_messages.text)
    # get handle
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    handle = users['user']['handle_str']
    # check if standup messages stored correctly
    assert messages_dict['messages'][0]['message'] == handle + ': ' + "hello"
