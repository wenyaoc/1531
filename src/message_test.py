import random
import string
import time
from time import sleep
import pytest

from error import InputError, AccessError
from message import message_send, message_remove, message_edit, message_sendlater, \
                    message_react, message_unreact, message_pin, message_unpin
from channels import channels_create
from channel import channel_messages, channel_invite
from auth import auth_register
from standup import standup_start, standup_send
from user import user_profile
from other import clear



def initialise_data():
    clear()
    boyu_dict = auth_register('cbyisaac@gmail.com', 'boyupass', 'Boyu', 'Cai')
    wenyao_dict = auth_register('wenyaochen427@gmail.com', 'wenyaopass', 'Wenyao', 'Chen')
    weiqiang_dict = auth_register('weiqiangzhuang24@gmail.com', 'weiqiangpass',
                                  'Weiqiang', 'Zhuang')
    channel_team1 = channels_create(wenyao_dict['token'], "team1", True)
    channel_team2 = channels_create(weiqiang_dict['token'], "team2", True)
    return boyu_dict, wenyao_dict, weiqiang_dict, channel_team1, channel_team2


# test the case that the token is not valid
def test_message_send_token_invalid():
    _, _, _, channel_team1, _ = initialise_data()
    with pytest.raises(AccessError):
        message_send("an.invalid.token", channel_team1['channel_id'], "hello")


# test the case that the message is longer than 1000
def test_message_send_morethan1000():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    letters = string.ascii_lowercase
    # random a string with length 1001
    message_str = ''.join(random.choice(letters) for i in range(1001))
    with pytest.raises(InputError):
        message_send(wenyao_dict['token'], channel_team1['channel_id'], message_str)


# test the case that the user haven't join the channel
def test_message_send_notjoin():
    boyu_dict, _, _, channel_team1, _ = initialise_data()
    with pytest.raises(AccessError):
        message_send(boyu_dict['token'], channel_team1['channel_id'], "a message")


# test the return value
def test_message_send_return_type():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    assert isinstance(message_id['message_id'], int)  # check if the return type is int
    assert len(message_id.keys()) == 1  # check if the return keys correct


# test whether the data store correctly
def test_message_send_data_store():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    sleep(1)
    message_id2 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "how are you")
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the information returned by channel_message
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 2
    assert messages_detail['messages'][1]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][0]['message_id'] == message_id2['message_id']
    assert messages_detail['messages'][1]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][0]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][1]['message'] == "hello"
    assert messages_detail['messages'][0]['message'] == "how are you"


# test the case that the token is invalid
def test_message_remove_token_invalid():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_remove('an.invalid.token', message_id['message_id'])


# test the case that the user does not exist
def test_message_remove_id_not_exist():
    _, wenyao_dict, _, _, _ = initialise_data()
    with pytest.raises(InputError):
        message_remove(wenyao_dict['token'], -1)


# test the case that the user haven't join the channel
def test_message_remove_not_member():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_remove(weiqiang_dict['token'], message_id['message_id'])


# test the case that the message is not send by authorised user
def test_message_remove_not_authorised_user():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'],
                              channel_team1['channel_id'], "hello")
    channel_invite(wenyao_dict['token'],
                   channel_team1['channel_id'], weiqiang_dict['u_id'])
    with pytest.raises(AccessError):
        message_remove(weiqiang_dict['token'], message_id['message_id'])


# test the return value
def test_message_remove_return_type():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'],
                              channel_team1['channel_id'], "hello")
    assert message_remove(wenyao_dict['token'], message_id['message_id']) == {}


# test the case that the authorised user call message remove
def test_message_remove_authorised_user():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_id2 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "how are you")
    message_remove(wenyao_dict['token'], message_id2['message_id'])
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 1
    assert messages_detail['messages'][0]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][0]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][0]['message'] == "hello"


# test the case that the owner of channel call message remove
def test_message_remove_channel_owner():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    channel_invite(wenyao_dict['token'], channel_team1['channel_id'], weiqiang_dict['u_id'])
    message_id = message_send(weiqiang_dict['token'], channel_team1['channel_id'], "hello")
    message_remove(wenyao_dict['token'], message_id['message_id'])
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the return value
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 0


# test the case that the owner of flockr call message remove
def test_message_remove_flockr_owner():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    channel_invite(wenyao_dict['token'], channel_team1['channel_id'], boyu_dict['u_id'])
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_remove(boyu_dict['token'], message_id['message_id'])
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the return value
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 0


# test the case that the token is invalid
def test_message_edit_token_invalid():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_edit('an.invalid.token', message_id['message_id'], "hi there")


# test the case that user is not a member
def test_message_edit_not_member():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_edit(weiqiang_dict['token'], message_id['message_id'], "hi there")


# test the case that the message is not send by authorised user
def test_message_edit_not_by_authorised_user():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    channel_invite(wenyao_dict['token'], channel_team1['channel_id'], weiqiang_dict['u_id'])
    with pytest.raises(AccessError):
        message_edit(weiqiang_dict['token'], message_id['message_id'], "hi there")


# test the return value
def test_message_edit_return_type():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    assert message_edit(wenyao_dict['token'], message_id['message_id'], "hi~") == {}


# test call message edit with empty string
def test_message_edit_empty_string():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_edit(wenyao_dict['token'], message_id1['message_id'], "")
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the return value from messages details
    assert len(messages_detail['messages']) == 0


# test whether the data store correctly
def test_message_edit_data_store():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    sleep(1)
    message_id2 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "how are you")
    sleep(1)
    message_edit(wenyao_dict['token'], message_id2['message_id'], "hi~")
    sleep(1)
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the return value from messages details
    assert len(messages_detail['messages']) == 2
    assert messages_detail['messages'][1]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][0]['message_id'] == message_id2['message_id']
    assert messages_detail['messages'][1]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][0]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][1]['message'] == "hello"
    assert messages_detail['messages'][0]['message'] == "hi~"


# test the case that token is invalid for sendlater
def test_message_sendlater_invalid_token():
    _, _, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent += 5
    with pytest.raises(AccessError):
        message_sendlater('invalid_token', channel_team1['channel_id'], "hi there", time_sent)


# test the case that message longer than for sendlater
def test_message_sendlater_long_message():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent += 5
    letters = string.ascii_lowercase
    message_str = ''.join(random.choice(letters) for i in range(1001))
    with pytest.raises(InputError):
        message_sendlater(wenyao_dict['token'], channel_team1['channel_id'], message_str, time_sent)



# test the case that Channel ID is not a valid channel for sendlater
def test_message_sendlater_invalidchannels_id():
    _, wenyao_dict, _, _, _ = initialise_data()
    with pytest.raises(InputError):
        message_sendlater(wenyao_dict['token'], "-1", "hi there", 12345)


# test the case that Time sent is a time in the past for sendlater
def test_message_sendlater_invalid_time():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent -= 5
    with pytest.raises(InputError):
        message_sendlater(wenyao_dict['token'], channel_team1['channel_id'], "hi there", time_sent)


# test the case that the authorised user has not joined the channel they are trying to post to
def test_message_sendlater_invalid_member():
    boyu_dict, _, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent += 5
    with pytest.raises(AccessError):
        message_sendlater(boyu_dict['token'], channel_team1['channel_id'], "hi there", time_sent)


# check the return value for sendlater
def test_message_sendlater_return_type():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent += 3
    messages = message_sendlater(wenyao_dict['token'], \
                                 channel_team1['channel_id'], "hi there", time_sent)
    time.sleep(5)
    assert isinstance(messages['message_id'], int)


# check the data store for sendlater
def test_message_sendlater_data():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    time_sent = int(time.time())
    time_sent += 3
    message_sendlater(wenyao_dict['token'], channel_team1['channel_id'], "hi there", time_sent)
    # check the return value from messages details
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    assert len(messages_detail['messages']) == 0
    # sleep for 5s
    time.sleep(5)
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    assert len(messages_detail['messages']) == 1
    assert messages_detail['messages'][0]['message'] == "hi there"


# check the data store in 2 different channels for sendlater
def test_message_sendlater_more_channels():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    channel_team2 = channels_create(wenyao_dict['token'], "team2", True)
    time_sent = int(time.time())
    time_sent += 3
    message_sendlater(wenyao_dict['token'], channel_team1['channel_id'], "hi there1", time_sent)
    message_sendlater(wenyao_dict['token'], channel_team2['channel_id'], "hi there2", time_sent)
    # check the return value from messages details
    messages_detail1 = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    messages_detail2 = channel_messages(wenyao_dict['token'], channel_team2['channel_id'], 0)
    assert len(messages_detail1['messages']) == 0
    assert len(messages_detail2['messages']) == 0
    # sleep for 5s
    time.sleep(5)
    messages_detail1 = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    messages_detail2 = channel_messages(wenyao_dict['token'], channel_team2['channel_id'], 0)
    assert len(messages_detail1['messages']) == 1
    assert len(messages_detail2['messages']) == 1
    assert messages_detail1['messages'][0]['message'] == "hi there1"
    assert messages_detail2['messages'][0]['message'] == "hi there2"


# test the case that the token is not valid in react
def test_message_react_invalid_token():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_react("invalid token", channel_team1['channel_id'], 1)


# test the case that the message_id is not valid in react
def test_message_react_invalid_message_id():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(InputError):
        message_react(wenyao_dict['token'], -1, 1)


# test the case that the user does not join the channel in react
def test_message_react_not_join():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(InputError):
        message_react(boyu_dict['token'], message_id1['message_id'], 1)


# test the case that the react id is not 1
def test_message_react_invalid_react_id():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(InputError):
        message_react(wenyao_dict['token'], message_id1['message_id'], 23)


# test the case that do react 2 times
def test_message_react_react_and_react_again():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(InputError):
        message_react(wenyao_dict['token'], message_id1['message_id'], 1)


# test the return value for message_react
def test_message_react_return_value():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    assert message_react(wenyao_dict['token'], message_id1['message_id'], 1) == {}


# test if the data stord correctly for message react
def test_message_react_data():
    _, wenyao_dict, weiqiang_dict, channel1, channel2 = initialise_data()
    # send 2 messages in different channel
    message1 = message_send(wenyao_dict['token'], channel1['channel_id'], "hello1")
    message2 = message_send(weiqiang_dict['token'], channel2['channel_id'], "hello2")
    # react both messages
    message_react(wenyao_dict['token'], message1['message_id'], 1)
    message_react(weiqiang_dict['token'], message2['message_id'], 1)
    messages_detail1 = channel_messages(wenyao_dict['token'], channel1['channel_id'], 0)
    messages_detail2 = channel_messages(weiqiang_dict['token'], channel2['channel_id'], 0)
    # check the information returned by channel_message
    assert messages_detail1['messages'][0]['reacts'][0]['is_this_user_reacted'] == True
    assert messages_detail1['messages'][0]['reacts'][0]['u_ids'] == [wenyao_dict['u_id']]
    assert messages_detail2['messages'][0]['reacts'][0]['is_this_user_reacted'] == True
    assert messages_detail2['messages'][0]['reacts'][0]['u_ids'] == [weiqiang_dict['u_id']]


# test the case that the token is not valid in unreact
def test_message_unreact_invalid_token():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(AccessError):
        message_unreact("invalid token", message_id1['message_id'], 1)


# test the case that the message_id is not valid in unreact
def test_message_unreact_invalid_message_id1():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(wenyao_dict['token'], "-1", 1)


# test the case that the message_id is not valid in unreact
def test_message_unreact_invalid_message_id2():
    _, wenyao_dict, weiqiang_dict, channel_team1, channel_team2 = initialise_data()
    message1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message2 = message_send(weiqiang_dict['token'], channel_team2['channel_id'], "hello")
    message_react(wenyao_dict['token'], message1['message_id'], 1)
    message_react(weiqiang_dict['token'], message2['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(wenyao_dict['token'], message2['message_id'], 1)


# test the case that user doesn't join the channel in unreact
def test_message_unreact_not_join():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(boyu_dict['token'], "-1", 1)


# test the case that react id is not valid
def test_message_unreact_invalid_react_id():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(wenyao_dict['token'], message_id1['message_id'], 23)


# test the case that do unreact 2 times
def test_message_unreact_react_and_unreact_again():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    message_unreact(wenyao_dict['token'], message_id1['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(wenyao_dict['token'], message_id1['message_id'], 1)


# test the return value for unreact
def test_message_unreact_return_value():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_react(wenyao_dict['token'], message_id1['message_id'], 1)
    assert message_unreact(wenyao_dict['token'], message_id1['message_id'], 1) == {}


# test the case that token is not valid for message_pin
def test_message_pin_invalid_token():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_pin("invalid", message_id1['message_id'])


# test the case that message_id is not valid for message_pin
def test_message_pin_invalid_message_id():
    _, wenyao_dict, _, _, _ = initialise_data()
    with pytest.raises(InputError):
        message_pin(wenyao_dict['token'], "-1")


# test the case that do message_pin 2 times
def test_message_pin_and_pin_again():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    with pytest.raises(InputError):
        message_pin(wenyao_dict['token'], message_id1['message_id'])


# # test message unpin with invalid user
def test_message_pin_invalid_user():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    with pytest.raises(AccessError):
        message_pin(weiqiang_dict['token'], message_id1['message_id'])


# test the return value for message_pin
def test_message_pin_return_value():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_id2 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    assert message_pin(wenyao_dict['token'], message_id1['message_id']) == {}
    assert message_pin(boyu_dict['token'], message_id2['message_id']) == {}


# test the data store for message_pin_data():
def test_message_pin_dict():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    details_dict = channel_messages((wenyao_dict['token']), channel_team1['channel_id'], 0)
    assert details_dict['messages'][0]['is_pinned'] is True


# test pin a standup message
def test_message_pin_standup():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    # start standup and send messages
    standup_start(wenyao_dict['token'], channel_team1['channel_id'], 5)
    standup_send(wenyao_dict['token'], channel_team1['channel_id'], "Hi")
    time.sleep(5) # sleep for 5s
    # send more messages after standup
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello1")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello2")
    # get the message_id for standup
    details_dict = channel_messages((wenyao_dict['token']), channel_team1['channel_id'], 0)
    message_id = details_dict['messages'][2]['message_id']
    message_pin(wenyao_dict['token'], message_id)
    details_dict = channel_messages((wenyao_dict['token']), channel_team1['channel_id'], 0)
    assert details_dict['messages'][2]['is_pinned'] is True
    # get handle
    wenyao_profile = user_profile(wenyao_dict['token'], wenyao_dict['u_id'])
    handle = wenyao_profile['user']['handle_str']
    assert details_dict['messages'][2]['message'] == handle + ': ' + "Hi"


# test message unpin with invalid token
def test_message_unpin_invalid_token():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    with pytest.raises(AccessError):
        message_unpin("invalid_token", "not_valid_id")


# test message unpin with invalid message_id
def test_message_unpin_invalid_message_id():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    with pytest.raises(InputError):
        message_unpin(wenyao_dict['token'], "-1")


# test doing unpin 2 times
def test_message_unpin_and_unpin_again():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    message_unpin(wenyao_dict['token'], message_id1['message_id'])
    with pytest.raises(InputError):
        message_unpin(wenyao_dict['token'], message_id1['message_id'])


# test doing message_unpin with invalud user
def test_message_unpin_invalid_user():
    _, wenyao_dict, weiqiang_dict, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    with pytest.raises(AccessError):
        message_unpin(weiqiang_dict['token'], message_id1['message_id'])


# test the return value for message_unpin
def test_message_unpin_return_value():
    boyu_dict, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    # member of channel
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    assert message_unpin(wenyao_dict['token'], message_id1['message_id']) == {}
    # owner
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    assert message_unpin(boyu_dict['token'], message_id1['message_id']) == {}


# test the data store for message_unpin
def test_message_unpin_data():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "hello")
    # member of channel
    message_pin(wenyao_dict['token'], message_id1['message_id'])
    message_unpin(wenyao_dict['token'], message_id1['message_id'])
    details_dict = channel_messages((wenyao_dict['token']), channel_team1['channel_id'], 0)
    assert details_dict['messages'][0]['is_pinned'] == False


# test hangman with invalid input
def test_hangman_invalidinput():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess a a")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess aa")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess 1")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess A")
    sleep(1)
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    #if the input is lnvalid, hangman won't be triggered
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 5
    assert messages_detail['messages'][0]['message'] == "/guess A"
    assert messages_detail['messages'][1]['message'] == "/guess 1"
    assert messages_detail['messages'][2]['message'] == "/guess"
    assert messages_detail['messages'][3]['message'] == "/guess aa"
    assert messages_detail['messages'][4]['message'] == "/guess a a"


# test hangman
def test_hangman():
    _, wenyao_dict, _, channel_team1, _ = initialise_data()
    message_id1 = message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess a")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess e")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess i")
    sleep(1)
    message_send(wenyao_dict['token'], channel_team1['channel_id'], "/guess o")
    sleep(1)
    messages_detail = channel_messages(wenyao_dict['token'], channel_team1['channel_id'], 0)
    # check the information returned by channel_message
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 4
    assert messages_detail['messages'][3]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][3]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][3]['message'] != "/guess a"
    assert messages_detail['messages'][2]['message'] != "/guess e"
    assert messages_detail['messages'][1]['message'] != "/guess i"
    assert messages_detail['messages'][0]['message'] != "/guess o"
