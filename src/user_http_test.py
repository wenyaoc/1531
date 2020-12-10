import json
import pytest
import requests
from httptest_helper import url, creatData
from other import clear

# Using an image jpg
IMG_URL = 'https://upload.wikimedia.org/wikipedia/commons/4/48/Unsw_library.jpg'
# For invalid png image for testing
INVALID_IMG_URL = 'https://en.wikipedia.org/wiki/University_\
                   of_New_South_Wales#/media/File:ARC_UNSW_logo.png'

# test token is not valid
def test_user_profile_token_not_valid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # give invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'user/profile', params={
            'token': "invalid_token",
            'u_id': boyu_dict['u_id']
        }).raise_for_status()


# test user u_id is not valid
def test_user_profile_u_id_not_valid(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # give invalid u_id -1
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get(url + 'user/profile', params={
            'token': boyu_dict['token'],
            'u_id': -1
        }).raise_for_status()


# test the returned value for user_profile
def test_user_profile(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    assert len(users['user']) == 6
    assert boyu_dict['u_id'] == users['user']['u_id']
    assert users['user']['email'] == 'cbyisaac@gmail.com'
    assert users['user']['name_first'] == 'Boyu'
    assert users['user']['name_last'] == 'Cai'
    assert len(users['user']['handle_str']) <= 20


# test token is not valid
def test_user_profile_setname_token_not_valid(url):
    clear()
    test_data = creatData(url)
    test_data.register_boyu()
    # give invlid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setname', json={
            'token': "invlid_token",
            'first_name': 'yifan',
            'last_name': 'Wu'
        }).raise_for_status()


# test the case that the first name is empty
def test_user_profile_setname_name_empty_firstname(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # reset first name is empty
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setname', json={
            'token': boyu_dict['token'],
            'first_name': '',
            'last_name': 'He'
        }).raise_for_status()


# test the case that the last name is empty
def test_user_profile_setname_name_empty_lastname(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    #make last name is empty
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setname', json={
            'token': boyu_dict['token'],
            'first_name': 'xukun',
            'last_name': ''
        }).raise_for_status()


# test first_name too long
def test_user_profile_setname_firstname_longerthan50(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # reset first name is longer than 20
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setname', json={
            'token': boyu_dict['token'],
            'first_name': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'last_name': 'He'
        }).raise_for_status()


# test last_name too long
def test_user_profile_setname_lastname_longerthan50(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # set last name is longer than 20
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setname', json={
            'token': boyu_dict['token'],
            'first_name': 'xukun',
            'last_name': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        }).raise_for_status()


# change first and last name
def test_user_profile_setname(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # test first name is already changed
    resp_first_name = requests.put(url + 'user/profile/setname', json={
        'token': boyu_dict['token'],
        'name_first': 'Boyu',
        'name_last': 'He'
    })
    profile_dict1 = json.loads(resp_first_name.text)
    assert profile_dict1 == {}
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    assert users['user']['name_first'] == 'Boyu'
    assert users['user']['name_last'] == 'He'
    # test last name is aleardy changed
    resp_last_name = requests.put(url + 'user/profile/setname', json={
        'token': boyu_dict['token'],
        'name_first': 'Xukun',
        'name_last': 'Cai'
    })
    profile_dict2 = json.loads(resp_last_name.text)
    assert profile_dict2 == {}
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    assert users['user']['name_first'] == 'Xukun'
    assert users['user']['name_last'] == 'Cai'


# test token is not valid
def test_user_profile_setemail_token_not_valid(url):
    clear()
    test_data = creatData(url)
    test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setemail', json={
            'token': "invlid_token",
            'email': 'yifanwu2333@gmail.com'
        }).raise_for_status()


# email methond is not valid
def test_user_profile_setemail_email_not_valid(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setemail', json={
            'token': boyu_dict['token'],
            'email': '....123'
        }).raise_for_status()


# email method is not valid
def test_user_profile_setemail_email_already_used(url):
    clear()
    #initialise data
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()
    # test user profile
    resp_profile = requests.get(url + 'user/profile', params={
        'token': wenyao_dict['token'],
        'u_id': wenyao_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/setemail', json={
            'token': boyu_dict['token'],
            'email': users['user']['email']
        }).raise_for_status()


# test update email
def test_user_profile_setemail(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # set legal email in the test
    resp_setemail = requests.put(url + 'user/profile/setemail', json={
        'token': boyu_dict['token'],
        'email': 'cxkisaac@gmail.com'
    })
    profile_dict = json.loads(resp_setemail.text)
    assert profile_dict == {}
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    assert users['user']['email'] == 'cxkisaac@gmail.com'


# test token is not valid
def test_user_profile_sethandle_token_not_valid(url):
    clear()
    test_data = creatData(url)
    test_data.register_boyu()
    # give invalid token
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/sethandle', json={
            'token': "invalid_token",
            'handle_str': 'wulifanfan'
        }).raise_for_status()


# test the case that the handle too short
def test_user_profile_sethandle_smallerthan3(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # test handle is smaller than 3
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/sethandle', json={
            'token': boyu_dict['token'],
            'handle_str': 'a'
        }).raise_for_status()


# test the case that the handle is too long
def test_user_profile_sethandle_greaterthan20(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    #test the handle is greater than 20
    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/sethandle', json={
            'token': boyu_dict['token'],
            'handle_str': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        }).raise_for_status()


# test the case that the handle is already used
def test_user_profile_sethandle_aleady_used(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    wenyao_dict = test_data.register_wenyao()

    resp_profile = requests.get(url + 'user/profile', params={
        'token': wenyao_dict['token'],
        'u_id': wenyao_dict['u_id']
    })
    users = json.loads(resp_profile.text)

    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + 'user/profile/sethandle', json={
            'token': boyu_dict['token'],
            'handle_str': users['user']['handle_str']
        }).raise_for_status()


# test update handle correctly
def test_user_profile_sethandle(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    # set handle
    resp_sethandle = requests.put(url + 'user/profile/sethandle', json={
        'token': boyu_dict['token'],
        'handle_str': 'caixukun'
    })
    profile_dcit = json.loads(resp_sethandle.text)
    # test user profile handle is already changed
    assert profile_dcit == {}
    resp_profile = requests.get(url + 'user/profile', params={
        'token': boyu_dict['token'],
        'u_id': boyu_dict['u_id']
    })
    users = json.loads(resp_profile.text)
    assert users['user']['handle_str'] == 'caixukun'
    assert len(users['user']['handle_str']) < 20
    assert len(users['user']['handle_str']) > 3


# test token is not valid
def test_user_uploadphoto_token_not_valid(url):
    clear()
    test_data = creatData(url)
    test_data.register_boyu()

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': "invalid_token",
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100
        }).raise_for_status()


# test the case that the input image url is not valid
def test_user_profile_uploadphoto_invalid_img_url(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': 'Invalid_url.jpg',
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100
        }).raise_for_status()


# test the case that the input image is not a jpg
def test_user_profile_uploadphoto_not_jpg(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': INVALID_IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_invalid_x_start(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': -1,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_invalid_y_start(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': -1,
            'x_end': 100,
            'y_end': 100
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_invalid_x_end(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': -1,
            'y_end': 100
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_invalid_y_end(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': -1
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_x_start_greater_x_end(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()

    with pytest.raises(requests.exceptions.HTTPError):
        requests.put(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': 100,
            'y_start': 10,
            'x_end': 0,
            'y_end': 100
        }).raise_for_status()


# test the case that the input dimensions is not valid
def test_user_profile_uploadphoto_y_start_greater_y_end(url):
    clear()
    test_data = creatData(url)
    boyu_dict = test_data.register_boyu()

    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + '/user/profile/uploadphoto', json={
            'token': boyu_dict['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 100,
            'x_end': 100,
            'y_end': 0
        }).raise_for_status()


# check the new image url after uploading img
def test_user_profile_uploadphoto(url):
    clear()
    test_data = creatData(url)
    wenyao_dict = test_data.register_wenyao()
    channel = test_data.creat_channel(wenyao_dict['token'], 'team1', True)
    resp_uploadphoto = requests.post(url + '/user/profile/uploadphoto', json={
        'token': wenyao_dict['token'],
        'img_url': IMG_URL,
        'x_start': 10,
        'y_start': 10,
        'x_end': 100,
        'y_end': 100
    })
    uploadphoto_result = json.loads(resp_uploadphoto.text)
    assert uploadphoto_result == {}
    # call channel details
    resp_details = requests.get(url + 'channel/details', params={
        'token': wenyao_dict['token'],
        'channel_id': channel['channel_id']
    })
    channel_details = json.loads(resp_details.text)
    image_url = url + 'image/' + str(wenyao_dict['u_id']) + '.jpg'
    # check the return dictionary
    assert channel_details['owner_members'][0] == {
        'u_id': wenyao_dict['u_id'],
        'name_first': 'Wenyao',
        'name_last': 'Chen',
        'profile_img_url': image_url,
    }
