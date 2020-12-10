import random
import string
import time
import json
import pytest
import requests
from httptest_helper import url, creatData
from other import clear


# test the case that the token is invalid for message_send
def test_message_send_invalid_token(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/send', json={
            'token': "an.invalid.token",
            'channel_id': channel['channel_id'],
            'message': "hello"
        }).raise_for_status()


# test the case that message > 1000 for message_send
def test_message_send_longerthan1000(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # random a string with length 1001
    letters = string.ascii_lowercase
    message_str = ''.join(random.choice(letters) for i in range(1001))
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/send', json={
            'token': wenyao_dict['token'],
            'channel_id': channel['channel_id'],
            'message': message_str
        }).raise_for_status()


# test the case that the authorised user has not joined the channel
def test_message_send_not_join(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/send', json={
            'token': boyu_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "hello"
        }).raise_for_status()


# test the data of message_send
def test_message_send(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # add 2 messages
    resp_message1 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    time.sleep(1)
    resp_message2 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "how are you"
    })
    message_id1 = json.loads(resp_message1.text)
    message_id2 = json.loads(resp_message2.text)
    # check storage
    resp_messages = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages_detail = json.loads(resp_messages.text)
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 2
    assert messages_detail['messages'][1]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][0]['message_id'] == message_id2['message_id']
    assert messages_detail['messages'][1]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][0]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][1]['message'] == "hello"
    assert messages_detail['messages'][0]['message'] == "how are you"


# test the case that the user does not exist
def test_message_remove_id_not_exist(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.delete(url + 'message/remove', json={
            'token': wenyao_dict['token'],
            'message_id': -1
        }).raise_for_status()



# test the case that token is invalid for message_remove
def test_message_remove_invalid_token(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    # delete the message with invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.delete(url + 'message/remove', json={
            'token': "invalid",
            'message_id': message_id['message_id']
        }).raise_for_status()


# test the case that the user haven't join the channel
def test_message_remove_not_member(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.delete(url + 'message/remove', json={
            'token': boyu_dict['token'],
            'message_id': message_id['message_id']
        }).raise_for_status()


# test the case that the message is not send by authorised user
def test_message_remove_not_authorised_user(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    weiqiang_dict = test_data.register_weiqiang()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    # invite a new user as channel member
    requests.post(url + 'channel/invite', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'u_id': weiqiang_dict['u_id']
    })
    # let tne new member call message remove
    with pytest.raises(requests.exceptions.HTTPError):
        requests.delete(url + 'message/remove', json={
            'token': weiqiang_dict['token'],
            'message_id': message_id['message_id']
        }).raise_for_status()


def test_message_remove(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # add 2 messages
    resp_message1 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    resp_message2 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "how are you"
    })
    message_id1 = json.loads(resp_message1.text)
    message_id2 = json.loads(resp_message2.text)
    # delete the 2 messages
    resp_remove1 = requests.delete(url + 'message/remove', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id']
    })
    resp_remove2 = requests.delete(url + 'message/remove', json={
        'token': wenyao_dict['token'],
        'message_id': message_id2['message_id']
    })
    # check the return value
    assert json.loads(resp_remove1.text) == {}
    assert json.loads(resp_remove2.text) == {}
    # check storage
    resp_messages = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages_detail = json.loads(resp_messages.text)
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert len(messages_detail['messages']) == 0


# test the case that token is invalid for mesage_edit
def test_message_edit_invalid_token(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    # edit the message with invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'message/edit', json={
            'token': "invalid",
            'message_id': message_id['message_id'],
            'message': "hi~"
        }).raise_for_status()


# test the case that user is not a member
def test_message_edit_not_member(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    # let an unreleated user call edit
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'message/edit', json={
            'token': boyu_dict['token'],
            'message_id': message_id['message_id'],
            'message': "hi~"
        }).raise_for_status()


# test the case that the message is not send by authorised user
def test_message_edit_not_by_authorised_user(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    weiqiang_dict = test_data.register_weiqiang()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message
    resp_message = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    message_id = json.loads(resp_message.text)
    # invite a new user as channel member
    requests.post(url + 'channel/invite', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'u_id': weiqiang_dict['u_id']
    })
    # let an unreleated user call edit
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'message/edit', json={
            'token': weiqiang_dict['token'],
            'message_id': message_id['message_id'],
            'message': "hi~"
        }).raise_for_status()


# test call message edit with empty string
def test_message_edit_empty_string(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # send a message in to a channel
    resp_message1 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    # edit the message with empty string
    message_id1 = json.loads(resp_message1.text)
    resp_edit = requests.put(url + 'message/edit', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'message': ""
    })
    # check the return value
    assert json.loads(resp_edit.text) == {}
    # check the return value from messages details
    resp_messages = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages_detail = json.loads(resp_messages.text)
    assert len(messages_detail['messages']) == 0


def test_message_edit(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    # add 2 messages
    resp_message1 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "hello"
    })
    resp_message2 = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "how are you"
    })
    message_id1 = json.loads(resp_message1.text)
    message_id2 = json.loads(resp_message2.text)
    # edit a message
    resp_edit = requests.put(url + 'message/edit', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'message': "hi~"
    })
    # check the return value
    assert json.loads(resp_edit.text) == {}
    # check storage
    resp_messages = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages_detail = json.loads(resp_messages.text)
    assert messages_detail['start'] == 0
    assert messages_detail['end'] == -1
    assert messages_detail['messages'][1]['message_id'] == message_id1['message_id']
    assert messages_detail['messages'][0]['message_id'] == message_id2['message_id']
    assert messages_detail['messages'][1]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][0]['u_id'] == wenyao_dict['u_id']
    assert messages_detail['messages'][1]['message'] == "hi~"
    assert messages_detail['messages'][0]['message'] == "how are you"

#tese the case that token is invalid for sendlater:
def test_message_send_later_invalid_token(url):
    clear()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/sendlater', json={
            'token': 'INVALID_token',
            'channel_id': 'ITHINKISRIGHT',
            'message': "Hello There !",
            'time_sent': '2020/05/17'
        }).raise_for_status()


#test the case that Channel id is invalid for sendlater:
def test_message_send_later_invalid_channel_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    time_sent = int(time.time())
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/sendlater', json={
            'token': wenyao_dict['token'],
            'channel_id':'who?',
            'message': "how are you",
            'time_sent': time_sent
        }).raise_for_status()


#test the case Time send is the invalid time
def test_message_send_later_invalid_time(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    time_sent = int(time.time())
    time_sent -= 10
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/sendlater', json={
            'token': wenyao_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "Hello There !",
            'time_sent': time_sent
        }).raise_for_status()


# test the case that the authorised user has not joined the channel they are trying to post to
def test_message_send_later_invalid_team_member(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    time_sent_1 = int(time.time())
    time_sent_1 += 10
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/sendlater', json={
            'token': boyu_dict['token'],
            'channel_id': channel['channel_id'],
            'message': "General Kenobi !",
            'time_sent': time_sent_1
        }).raise_for_status()


#test the case return valid value of send later:
def test_message_sendlater_return_type(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    time_sent = int(time.time())
    time_sent += 5
    #send later a message in 5s
    send_later_mes_2 = requests.post(url + 'message/sendlater', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !",
        'time_sent': time_sent
        })
    # time sleep for 5s
    time.sleep(5)
    return_text = json.loads(send_later_mes_2.text)
    assert isinstance(return_text['message_id'], int)


# check the data store for sendlater
def test_message_sendlater_data(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    time_sent = int(time.time())
    time_sent += 5
    #send_later a message
    requests.post(url + 'message/sendlater', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !",
        'time_sent': time_sent
        })
    resp_messages_1 = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages_detail = json.loads(resp_messages_1.text)
    assert messages_detail['messages'] == []
    # sleep for 5s
    time.sleep(5)
    resp_messages_2 = requests.get(url + 'channel/messages', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    message_detail_2_re = json.loads(resp_messages_2.text)
    assert len(message_detail_2_re['messages']) == 1
    assert message_detail_2_re['messages'][0]['message'] == "General Kenobi !"


# test the case that the token is not valid in react
def test_message_react_invalid_token(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/react', json={
            'token': "MAYTHEFORCE",
            'message_id': channel['channel_id'],
            'react_id': 1
        }).raise_for_status()


# test the case that the message_id is not valid in react
def test_message_react_invalid_message_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !"
    })
    #check incorrect message_id
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/react', json={
            'token': wenyao_dict['token'],
            'message_id': '043',
            'react_id': 1
        }).raise_for_status()


# test the case that the user is not join in the channel
def test_message_react_invalid_member(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/react', json={
            'token': boyu_dict['token'],
            'message_id': channel['channel_id'],
            'react_id': 1
        }).raise_for_status()


# test the case the react Id is invalid
def test_message_react_invalid_react_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "Tesla MODEL X"
    })
    message_id1 = json.loads(message_test.text)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/react', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
            'react_id': 2
        }).raise_for_status()


# test the case react 2nd time over message
def test_message_react_and_react_again(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !"
    })
    # react
    message_id1 = json.loads(message_test.text)
    requests.post(url + 'message/react', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    #react second time
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/react', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
            'react_id': 1
        }).raise_for_status()


#test the case for correct react return
def test_message_react_valid_outcome(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !"
    })
    # react to message
    message_id1 = json.loads(message_test.text)
    react_re = requests.post(url + 'message/react', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    message_return = json.loads(react_re.text)
    assert message_return == {}


# test the case unreact invalid token
def test_message_unreact_invalid_token(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unreact', json={
            'token': "MAYTHEFORCE",
            'message_id': channel['channel_id'],
            'react_id': 1
        }).raise_for_status()


# test the case that the user is not join in the channel for unreact
def test_message_unreact_invalid_member(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #react a message:
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unreact', json={
            'token': boyu_dict['token'],
            'message_id': channel['channel_id'],
            'react_id': 1
        }).raise_for_status()


# test the case unreact with invalid message_id
def test_message_unreact_invalid_message_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "It's over Anakin, I have the high ground!"
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unreact', json={
            'token': wenyao_dict['token'],
            'message_id': '043',
            'react_id': 1
        }).raise_for_status()


# test the case the react id is in invalid for unreact
def test_message_unreact_invalid_react_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "Don't Try it."
    })
    message_id1 = json.loads(message_test.text)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unreact', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
            'react_id': 2
        }).raise_for_status()


# test the case of unreact second time of a message
def test_message_unreact_and_unreact_again(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "You underestimate my POWER!"
    })
    message_id1 = json.loads(message_test.text)
    requests.post(url + 'message/react', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    requests.post(url + 'message/unreact', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unreact', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
            'react_id': 1
        }).raise_for_status()

# test the case of correct unreact output
def test_message_unreact_valid_message_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "General Kenobi !"
    })
    message_id1 = json.loads(message_test.text)
    #react a message
    requests.post(url + 'message/react', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    # unreact the message
    message_unreact_1 = requests.post(url + 'message/unreact', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
        'react_id': 1
    })
    return_text = json.loads(message_unreact_1.text)
    assert return_text == {}


#test the case invalid token for pin
def test_message_pin_invalid_token(url):
    clear()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/pin', json={
            'token': 'HAIRCUT',
            'message_id': 43258158,
        }).raise_for_status()


# test the case pin with invalid message id
def test_message_pin_invalid_message_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "YOU were the chosen ONE, it was said you would destory the Sith, not join them "
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/pin', json={
            'token': wenyao_dict['token'],
            'message_id': 43258158,
        }).raise_for_status()


# test the case pin with invalid user
def test_message_pin_invalid_user(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "Bring balance to the force, not leave it in darkness"
    })
    message_id1 = json.loads(message_test.text)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/pin', json={
            'token': boyu_dict['token'],
            'message_id': message_id1['message_id']
        }).raise_for_status()


# test the case of pin and pin 2nd times
def test_message_pin_2nd_times(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "YOU were the chosen ONE, it was said you would destory the Sith, not join them "
    })
    message_id1 = json.loads(message_test.text)
    # pin the message
    requests.post(url + 'message/pin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    # pin the message for the second time
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/pin', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
        }).raise_for_status()


# test the case for valid token for pin
def test_message_pin_valid_outcome(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "YOU were the chosen ONE, it was said you would destory the Sith, not join them "
    })
    message_id1 = json.loads(message_test.text)
    # pin the message
    message_pin_1 = requests.post(url + 'message/pin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    return_text = json.loads(message_pin_1.text)
    assert return_text == {}


#test the case invalid token for unpin
def test_message_unpin_invalid_token(url):
    clear()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unpin', json={
            'token': 'HAIRCUT',
            'message_id': 43258158,
        }).raise_for_status()


# test the case unpin with invalid message id
def test_message_unpin_invalid_message_id(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    #send a message:
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unpin', json={
            'token': wenyao_dict['token'],
            'message_id': 43258158,
        }).raise_for_status()


# test the case pin with invalid user
def test_message_unpin_invalid_user(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    boyu_dict = test_data.register_boyu()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unpin', json={
            'token': boyu_dict['token'],
            'message_id': channel['channel_id']
        }).raise_for_status()


# test the case of unpin and pin 2nd times
def test_message_unpin_2nd_times(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "YOU were the chosen ONE, it was said you would destory the Sith, not join them "
    })
    message_id1 = json.loads(message_test.text)
    # pin the message first
    requests.post(url + 'message/pin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    # unpin the message
    requests.post(url + 'message/unpin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    # unpin again
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'message/unpin', json={
            'token': wenyao_dict['token'],
            'message_id': message_id1['message_id'],
        }).raise_for_status()


# test the case for valid token for unpin
def test_message_unpin_valid_outcome(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    #send a message:
    message_test = requests.post(url + 'message/send', json={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id'],
        'message': "YOU were the chosen ONE, it was said you would destory the Sith, not join them "
    })
    message_id1 = json.loads(message_test.text)
    requests.post(url + 'message/pin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    #unpin message
    message_unpin = requests.post(url + 'message/unpin', json={
        'token': wenyao_dict['token'],
        'message_id': message_id1['message_id'],
    })
    return_text = json.loads(message_unpin.text)
    assert return_text == {}
