import json
from time import sleep
import pytest
import requests
from httptest_helper import url, creatData
from other import clear



# test the case that the token is invalid for channel invite
def test_channel_invite_invalid_token(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_weiqiang()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/invite', json={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
            'u_id': user['u_id']
        }).raise_for_status()


# test_channel_invite return and store data successfully
def test_channel_invite_pass(url):
    clear()
    data = creatData(url)
    user1 = data.register_wenyao()
    user2 = data.register_boyu()
    channel = data.creat_channel(user1['token'], 'channel01', True)
    resp_profile = requests.get(url + 'user/profile', params={
        "token": user2["token"],
        "u_id": user2["u_id"]
    })
    user_details = json.loads(resp_profile.text)
    # invite one user
    resp_invite = requests.post(url + 'channel/invite', json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id']
    })
    invite_dic = json.loads(resp_invite.text)
    # check return
    assert invite_dic == {}
    # check storage
    resp_details = requests.get(url + 'channel/details', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    })
    # print(resp_details.json())
    channel_details = json.loads(resp_details.text)
    if_invite_success = False
    for member in channel_details["all_members"]:
        lookup_user = user_details['user']
        look_up_temp = {
            'name_first': lookup_user['name_first'],
            'name_last': lookup_user['name_last'],
            'u_id': user2['u_id'],
            'profile_img_url': '',
        }

        if member == look_up_temp:
            if_invite_success = True
            break
    assert if_invite_success is True


# InputError when channel_id does not refer to a valid channel
def test_channel_invite_channelid_not_valid(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_weiqiang()
    data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/invite', json={
            'token': owner['token'],
            'channel_id': -1,
            'u_id': user['u_id']
        }).raise_for_status()


# InputError when u_id does not refer to a valid user
def test_channel_invite_uid_not_valid(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/invite', json={
            'token': owner['token'],
            'channel_id': channel['channel_id'],
            'u_id': -1
        }).raise_for_status()


# AcessError when the authorised user is not already a member of the channel
def test_channel_invite_authorised_user_not_member(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user1 = data.register_weiqiang()
    user2 = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/invite', json={
            'token': user1['token'],
            'channel_id': channel['channel_id'],
            'u_id': user2['u_id']
        }).raise_for_status()


# test the case that the token is invalid for channel details
def test_channel_details_invalid_token(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/details', params={
            'token': "invalid.token",
            'channel_id': channel['channel_id']
        }).raise_for_status()


# test_channel_details return correctly
def test_channel_details_pass(url):
    clear()
    data = creatData(url)
    user1 = data.register_wenyao()
    user2 = data.register_boyu()
    resp1_profile = requests.get(url + 'user/profile', params={
        "token": user1["token"],
        "u_id": user1["u_id"]
    })
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": user2["token"],
        "u_id": user2["u_id"]
    })
    user1_details = json.loads(resp1_profile.text)
    user2_details = json.loads(resp2_profile.text)
    # create one channel
    channel = data.creat_channel(user1['token'], 'channel01', True)
    # invite one user
    requests.post(url + 'channel/invite', json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id']
    })
    # check return
    resp_details = requests.get(url + 'channel/details', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    assert channel_details['name'] == 'channel01'
    owner = user1_details['user']
    assert channel_details['owner_members'] == [
        {'u_id': owner['u_id'],
         'name_first': owner['name_first'],
         'name_last': owner['name_last'],
         'profile_img_url': '',
         }]
    member_not_owner = user2_details['user']
    lookup_member = {'u_id': member_not_owner['u_id'],
                     'name_first': member_not_owner['name_first'],
                     'name_last': member_not_owner['name_last'],
                     'profile_img_url': ''}
    assert lookup_member in channel_details['all_members']


# IputError when the channel_id is not a valid one
def test_channel_details_channelid_not_valid(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/details', params={
            'token': owner['token'],
            'channel_id': -1
        }).raise_for_status()


# AccessError when the authorised user is not the member of the channel with channel_id
def test_channel_details_user_not_member(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/details', params={
            'token': user['token'],
            'channel_id': channel['channel_id']
        }).raise_for_status()


# test the case that the token is invalid for channel messages
def test_channel_messages_invalid_token(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    channel = data.creat_channel(user['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/messages', params={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
            'start': 0
        }).raise_for_status()


# test_channel_messages return correctly
def test_channel_messages_pass(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    # create one channel
    channel = data.creat_channel(user['token'], 'channel01', True)
    # add two messages
    resp_message1 = requests.post(url + 'message/send', json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "VSCode is good."})

    sleep(1)
    resp_message2 = requests.post(url + 'message/send', json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "Though I'dont like it."
    })
    msg_id1 = json.loads(resp_message1.text)
    msg_id2 = json.loads(resp_message2.text)
    # check
    resp_msg = requests.get(url + 'channel/messages', params={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    msg_details = json.loads(resp_msg.text)
    assert len(msg_details['messages']) == 2
    assert msg_details['start'] == 0
    assert msg_details['end'] == -1
    assert msg_details['messages'][1]['message_id'] == msg_id1['message_id']
    assert msg_details['messages'][0]['message_id'] == msg_id2['message_id']
    assert msg_details['messages'][1]['message'] == "VSCode is good."
    assert msg_details['messages'][0]['message'] == "Though I'dont like it."
    assert msg_details['messages'][1]['u_id'] == user['u_id']
    assert msg_details['messages'][0]['u_id'] == user['u_id']


# InputError when channel_id is not valid
def test_channel_messages_channelid_not_valid(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    # create channel
    data.creat_channel(user['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/messages', params={
            'token': user['token'],
            'channel_id': -1,
            'start': 0
        }).raise_for_status()


# InputError when start is greater than totoal number of messages in the channel
def test_channel_messages_start_greater_than_total(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    channel = data.creat_channel(user['token'], 'channel01', True)
    # add 2 messages
    requests.post(url + 'message/send', json={
        'token':user['token'],
        'channel_id': channel['channel_id'],
        'message': "VSCode is good."})
    requests.post(url + 'message/send', json={
        'token':user['token'],
        'channel_id': channel['channel_id'],
        'message': "Though I'dont like it."})
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/messages', params={
            'token': user['token'],
            'channel_id': channel['channel_id'],
            'start': 10
        }).raise_for_status()


# AccessError when the authorised user is not an member of the channel
def test_channel_messages_user_not_member(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_weiqiang()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'channel/messages', params={
            'token': user['token'],
            'channel_id': channel['channel_id'],
            'start': 0
        }).raise_for_status()


# test the case that the token is invalid for channel leave
def test_channel_leave_invalid_token(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    channel = data.creat_channel(user['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/leave', json={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
        }).raise_for_status()


# test_channel_leave return and store data successfully
def test_channel_leave_pass(url):
    clear()
    data = creatData(url)
    user1 = data.register_wenyao()
    user2 = data.register_boyu()
    resp1_profile = requests.get(url + 'user/profile', params={
        "token": user1["token"],
        "u_id": user1["u_id"]
    })
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": user2["token"],
        "u_id": user2["u_id"]
    })
    user1_details = json.loads(resp1_profile.text)
    user2_details = json.loads(resp2_profile.text)
    # create channel
    channel = data.creat_channel(user1['token'], 'channel01', True)
    # invite one user
    requests.post(url + 'channel/invite', json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id']
    })
    # user2 leaves
    resp1_leave = requests.post(url + 'channel/leave', json={
        'token': user2['token'],
        'channel_id': channel['channel_id']
    })
    # check return
    assert json.loads(resp1_leave.text) == {}
    # check user2 leave or not
    resp_details = requests.get(url + 'channel/details', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    normal_user = user2_details['user']
    normal_user_dict = {
        'u_id': normal_user['u_id'],
        'name_first': normal_user['name_first'],
        'name_last': normal_user['name_last'],
        'profile_img_url': '',
    }
    assert normal_user_dict not in channel_details['all_members']
    assert len(channel_details['all_members']) == 1
    # check the left user is the owner
    owner_user = user1_details['user']
    owner_user_dict = {
        'u_id': owner_user['u_id'],
        'name_first': owner_user['name_first'],
        'name_last': owner_user['name_last'],
        'profile_img_url': '',
    }
    assert owner_user_dict in channel_details['all_members']
    assert owner_user_dict in channel_details['owner_members']
    # check when owner = user1 leave the channel
    requests.post(url + 'channel/invite', json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id']
    })
    requests.post(url + 'channel/leave', json={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    })
    resp_details = requests.get(url + 'channel/details', params={
        'token': user2['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    assert channel_details['owner_members'] == []
    assert len(channel_details['all_members']) == 1
    assert owner_user_dict not in channel_details['all_members']
    assert normal_user_dict in channel_details['all_members']


# InputError when channel_id does not refer to a valid channel
def test_channel_leave_channelid_not_valid(url):
    clear()
    data = creatData(url)
    user = data.register_wenyao()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/leave', json={
            'token': user['token'],
            'channel_id': -1
        }).raise_for_status()


# AccessError when the authorised user is not a member with channel_id
def test_channel_leave_user_not_member(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/leave', json={
            'token': user['token'],
            'channel_id': channel['channel_id']
        }).raise_for_status()


# test the case that the token is invalid for channel join
def test_channel_join_invalid_token(url):
    clear()
    data = creatData(url)
    user = data.register_weiqiang()
    channel = data.creat_channel(user['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/join', json={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
        }).raise_for_status()


# test_channel_join return and store data successfully
def test_channel_join_pass(url):
    clear()
    data = creatData(url)
    user1 = data.register_wenyao()
    user2 = data.register_boyu()
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": user2["token"],
        "u_id": user2["u_id"]
    })
    user2_details = json.loads(resp2_profile.text)
    # create channel
    channel = data.creat_channel(user1['token'], 'channel01', True)
    # check join public channel
    resp_join = requests.post(url + 'channel/join', json={
        'token': user2['token'],
        'channel_id': channel['channel_id']
    })
    # check return
    assert json.loads(resp_join.text) == {}
    # check join or not
    resp_details = requests.get(url + 'channel/details', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    lookup_user = user2_details['user']
    lookup_user_dict = {
        'u_id': lookup_user['u_id'],
        'name_first': lookup_user['name_first'],
        'name_last': lookup_user['name_last'],
        'profile_img_url': '',
    }
    assert lookup_user_dict in channel_details['all_members']
    assert lookup_user_dict not in channel_details['owner_members']
    assert len(channel_details['all_members']) == 2


# InputError when channel_id does not refer to a valid channel
def test_channel_join_channelid_not_valid(url):
    clear()
    data = creatData(url)
    user = data.register_wenyao()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/join', json={
            'token': user['token'],
            'channel_id': -1
        }).raise_for_status()


# AccessError when the channel with channel_id is private
def test_channel_join_private(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    authorised_user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', False)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/join', json={
            'token': authorised_user['token'],
            'channel_id': channel['channel_id']
        }).raise_for_status()


# test the case that the token is invalid for channel addowner
def test_channel_addowner_invalid_token(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': user['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/addowner', json={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
            'u_id': user['u_id']
        }).raise_for_status()


# test_channel_addowner return and store data successfully
def test_channel_addowner_pass(url):
    clear()
    data = creatData(url)
    flockr_owner = data.register_weiqiang()
    channel_owner = data.register_wenyao()
    owner_to_be_added = data.register_boyu()
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": owner_to_be_added["token"],
        "u_id": owner_to_be_added["u_id"]
    })
    # user1_details = json.loads(resp1_profile.text)
    owner_to_be_added_details = json.loads(resp2_profile.text)
    # create channel
    channel = data.creat_channel(channel_owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': owner_to_be_added['token'],
        'channel_id': channel['channel_id']
    })
    # add one owner
    resp_addowner = requests.post(url + 'channel/addowner', json={
        'token': channel_owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner_to_be_added['u_id']
    })
    # check return
    assert json.loads(resp_addowner.text) == {}
    # check add or not
    resp_details = requests.get(url + 'channel/details', params={
        'token': channel_owner['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    lookup_user = owner_to_be_added_details['user']
    lookup_user_dict = {
        'u_id': lookup_user['u_id'],
        'name_first': lookup_user['name_first'],
        'name_last': lookup_user['name_last'],
        'profile_img_url': '',
    }
    assert lookup_user_dict in channel_details['all_members']
    assert lookup_user_dict in channel_details['owner_members']
    assert len(channel_details['all_members']) == 2
    # check when flockr owner in the channel and add owner
    requests.post(url + 'channel/removeowner', json={
        'token': channel_owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner_to_be_added['u_id']
    })
    requests.post(url + 'channel/join', json={
        'token': flockr_owner['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/addowner', json={
        'token': flockr_owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner_to_be_added['u_id']
    })
    assert lookup_user_dict in channel_details['owner_members']
    assert len(channel_details['owner_members']) == 2


# InputError when channel_id does not refer to a valid channel
def test_channel_addowner_channelid_not_valid(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': user['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/addowner', json={
            'token': owner['token'],
            'channel_id': -1,
            'u_id': user['u_id']
        }).raise_for_status()


# InputError when user with u_id is already an owner of the channel
def test_channel_addowner_user_already_owner(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    test_owner = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': test_owner['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/addowner', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': test_owner['u_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/addowner', json={
            'token': owner['token'],
            'channel_id': channel['channel_id'],
            'u_id': test_owner['u_id']
        }).raise_for_status()


# AccessError when the authorised user is not an owner of the channel
def test_channel_addowner_authorised_user_not_owner(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    authorised_user = data.register_weiqiang()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': authorised_user['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/join', json={
        'token': user['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/addowner', json={
            'token': authorised_user['token'],
            'channel_id': channel['channel_id'],
            'u_id': user['u_id']
        }).raise_for_status()


# AccessError when the authorised user is the owner of flockr but not member of the channel
def test_channel_addowner_authorised_flockr_owner_not_in_channel(url):
    clear()
    data = creatData(url)
    flockr_owner = data.register_wenyao()
    channel_owner = data.register_weiqiang()
    owner_to_be_added = data.register_boyu()
    channel = data.creat_channel(channel_owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': owner_to_be_added['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/addowner', json={
            'token': flockr_owner['token'],
            'channel_id': channel['channel_id'],
            'u_id': owner_to_be_added['u_id']
        }).raise_for_status()


# test the case that the token is invalid for channel removeowner
def test_channel_removeowner_invalid_token(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    test_owner = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': test_owner['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/addowner', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': test_owner['u_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/removeowner', json={
            'token': "invalid.token",
            'channel_id': channel['channel_id'],
            'u_id': test_owner['u_id']
        }).raise_for_status()


# test_channel_removeowner return and store data successfully
def test_channel_removeowner_pass(url):
    clear()
    data = creatData(url)
    flockr_owner = data.register_weiqiang()
    owner1 = data.register_wenyao()
    owner2 = data.register_boyu()
    resp1_profile = requests.get(url + 'user/profile', params={
        "token": owner1["token"],
        "u_id": owner1["u_id"]
    })
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": owner2["token"],
        "u_id": owner2["u_id"]
    })
    owner1_details = json.loads(resp1_profile.text)
    owner2_details = json.loads(resp2_profile.text)
    # create channel
    channel = data.creat_channel(owner1['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': owner2['token'],
        'channel_id': channel['channel_id']
    })
    # add one owner
    requests.post(url + 'channel/addowner', json={
        'token': owner1['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner2['u_id']
    })
    # remove the original owner = creator
    resp_removeowner = requests.post(url + 'channel/removeowner', json={
        'token': owner2['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner1['u_id']
    })
    # check return
    assert json.loads(resp_removeowner.text) == {}
    # check remove or not
    resp_details = requests.get(url + 'channel/details', params={
        'token': owner2['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    lookup_user = owner1_details['user']
    lookup_user_dict = {
        'u_id': lookup_user['u_id'],
        'name_first': lookup_user['name_first'],
        'name_last': lookup_user['name_last'],
        'profile_img_url': '',
    }
    assert lookup_user_dict not in channel_details['owner_members']
    assert lookup_user_dict in channel_details['all_members']
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 2
    # check when the flockr owner is a member of the channel and remove owner
    requests.post(url + 'channel/join', json={
        'token': flockr_owner['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/removeowner', json={
        'token': flockr_owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner2['u_id']
    })
    resp_details = requests.get(url + 'channel/details', params={
        'token': flockr_owner['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    lookup_user = owner2_details['user']
    lookup_user_dict = {
        'u_id': lookup_user['u_id'],
        'name_first': lookup_user['name_first'],
        'name_last': lookup_user['name_last']
    }
    assert lookup_user_dict not in channel_details['owner_members']
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 3


# InputError when channel_id is not valid
def test_channel_removeowner_channelid_not_valid(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    test_owner = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': test_owner['token'],
        'channel_id': channel['channel_id']
    })
    requests.post(url + 'channel/addowner', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': test_owner['u_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/removeowner', json={
            'token': owner['token'],
            'channel_id': -1,
            'u_id': test_owner['u_id']
        }).raise_for_status()


# InputError when user with u_id is not an owner of the channel
def test_channel_removeowner_user_not_owner(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': user['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/removeowner', json={
            'token': owner['token'],
            'channel_id': channel['channel_id'],
            'u_id': user['u_id']
        }).raise_for_status()


# AccessError when the authorised user is not an owner of the channel
def test_channel_removeowner_authorised_user_not_owner(url):
    clear()
    data = creatData(url)
    owner = data.register_wenyao()
    authorised_user = data.register_boyu()
    channel = data.creat_channel(owner['token'], 'channel01', True)
    requests.post(url + 'channel/join', json={
        'token': authorised_user['token'],
        'channel_id': channel['channel_id']
    })
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/removeowner', json={
            'token': authorised_user['token'],
            'channel_id': channel['channel_id'],
            'u_id': owner['u_id']
        }).raise_for_status()


# AccessError when the authorised user is an owner of the flockr but not a member of this channel
def test_channel_removeowner_flockr_owner_not_in_channel(url):
    clear()
    data = creatData(url)
    flockr_owner = data.register_wenyao()
    owner_to_be_removed = data.register_boyu()
    channel = data.creat_channel(owner_to_be_removed['token'], 'channel01', True)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'channel/removeowner', json={
            'token': flockr_owner['token'],
            'channel_id': channel['channel_id'],
            'u_id': owner_to_be_removed['u_id'],
        }).raise_for_status()
