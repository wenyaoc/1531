import random
import string
import time
import pytest
from error import InputError, AccessError
from channels import channels_create
from channel import channel_messages, channel_invite
from auth import auth_register
from user import user_profile
from other import clear
from standup import standup_active, standup_send, standup_start


def initialise_data():
    clear()
    boyu_dict = auth_register('123@gmail.com', 'boyupass', 'Boyu', 'Cai')
    wenyao_dict = auth_register('427@gmail.com', 'wenyaopass', 'Wenyao', 'Chen')
    weiqiang_dict = auth_register('234@gmail.com', 'weiqiangpass',
                                  'Weiqiang', 'Zhuang')
    channel_team1 = channels_create(wenyao_dict['token'], "team1", True)
    channel_team2 = channels_create(weiqiang_dict['token'], "team2", True)
    return boyu_dict, wenyao_dict, weiqiang_dict, channel_team1, channel_team2


# test the case that the token is invalid for standup start
def test_standup_start_token_invalid():
    _, _, _, channel_team1, _ = initialise_data()
    with pytest.raises(AccessError):
        assert standup_start('an.invalid.token', channel_team1['channel_id'], 1)


# test channel Id is not valid
def test_standup_start_channel_id_invalid():
    _, wenyao_dict, _, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert standup_start(wenyao_dict['token'], '-1', 1)


# test the case is channel is currently running
def test_standup_start_channel_running():
    time.sleep(1)
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    with pytest.raises(InputError):
        assert standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)


# test the case that the token is invalid for standup active
def test_standup_active_token_invalid():
    time.sleep(5)
    _, _, _, channel_team1, _ = initialise_data()
    with pytest.raises(AccessError):
        assert standup_active('an.invalid.token', channel_team1['channel_id'])


# test the case that the channel is not a valid channel
def test_standup_active_channel_id_invalid():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    with pytest.raises(InputError):
        assert standup_active(wenyao_dict['token'], '-1')


#test the case that standup is not active in a channel
def test_standup_not_active():
    time.sleep(5)
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    active = standup_active(wenyao_dict['token'], channel_team1['channel_id'])
    assert active == {'is_active': False, 'time_finish': None}


#test the case that standup is active in a channel
def test_standup_active():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    times = standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    active = standup_active(wenyao_dict['token'], channel_team1['channel_id'])
    assert active == {'is_active': True, 'time_finish': times['time_finish']}


# test the case that the token is invalid
def test_standup_send_token_invalid():
    time.sleep(5)
    _, _, _, channel_team1, _ = initialise_data()
    with pytest.raises(AccessError):
        assert standup_send('an.invalid.token', channel_team1['channel_id'], "Hello")


# test standup send channel ID is not valid
def test_standup_send_channel_id_invalid():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    with pytest.raises(InputError):
        assert standup_send(wenyao_dict['token'], '-1', "Hello")


# test the case that the message is longer than 1000
def test_standup_send_morethan1000():
    time.sleep(5)
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    standup_active(wenyao_dict['token'], channel_team1['channel_id'])
    letters = string.ascii_lowercase
    # random a string with length 1001
    message_str = ''.join(random.choice(letters) for i in range(1001))
    with pytest.raises(InputError):
        assert standup_send(wenyao_dict['token'], channel_team1['channel_id'], message_str)


# test the case that An active standup is not currently running in this channel
def test_standup_send_not_active():
    time.sleep(5)
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    with pytest.raises(InputError):
        assert standup_send(wenyao_dict['token'], channel_team1['channel_id'], "Hello")


# test the case that The authorised user is not a member of the channel that the message is within
def test_standup_send_not_member():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    with pytest.raises(AccessError):
        assert standup_send(boyu_dict['token'], channel_team1['channel_id'], "Hello")


# test the return value for send
def test_standup_send_is_member():
    time.sleep(5)
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    channel_invite(wenyao_dict['token'], channel_team1['channel_id'],
                   boyu_dict['u_id'])
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    sent = standup_send(boyu_dict['token'], channel_team1['channel_id'], "Hello")
    assert sent == {}


# test the data stored after a whole standup
def test_standup_whole():
    time.sleep (5)
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    # start standup
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    # check if standup is active
    is_active = standup_active(wenyao_dict['token'], channel_team1['channel_id'])['is_active']
    assert is_active == True
    standup_send(wenyao_dict['token'], channel_team1['channel_id'], "Hi")
    time.sleep(1)
    standup_send(wenyao_dict['token'], channel_team1['channel_id'], "Hello")
    # sleep for 5s
    time.sleep(5)
    # check if standup is active
    is_active = standup_active(wenyao_dict['token'], channel_team1['channel_id'])['is_active']
    assert is_active == False
    # get handle
    wenyao_profile = user_profile(wenyao_dict['token'], wenyao_dict['u_id'])
    handle = wenyao_profile['user']['handle_str']
    # check the return value for channel_message
    message_dict = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    msg = handle + ': ' + "Hi" + '\n' + handle + ': ' + "Hello"
    assert message_dict['messages'][0]['message'] == msg
