import json
import pytest
import requests
from httptest_helper import url, creatData
from other import clear


# test the case that emails are not valid
def test_register_email_not_valid(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': r'team1.team1\team1_team1@google.com',
            'password': 'wendy_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'team1.com',
            'password': 'wendy_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'team&@gamil.com',
            'password': 'wendy_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'Team1@google.com',
            'password': 'wendy_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': '',
            'password': 'no_one_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': '    @google.com',
            'password': 'maybe_one_pass',
            'name_first': 'Wenyao',
            'name_last': 'Chen'
        }).raise_for_status()


# test the case that email is already been used by another user
def test_auth_register_email_already_used(url):
    clear()
    test_data = creatData(url)
    # creat a user
    user = test_data.register_wenyao()
    resp_profile = requests.get(url + 'user/profile', params={
        "token": user["token"],
        "u_id": user["u_id"]
    })
    user_details = json.loads(resp_profile.text)
    test_email = user_details['user']['email']
    # creat another user with the same email
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': test_email,
            'password': 'wenyaocool',
            'name_first': 'Wenyao',
            'name_last': 'Lee'
        }).raise_for_status()


# test the case that password entered is lass than 6 characters
def test_auth_register_password_lessthan6(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'ironman007@gmail.com',
            'password': 'cool',
            'name_first': 'Iron',
            'name_last': 'Man'
        }).raise_for_status()


# test the case that firstname is lass than 1 character
def test_auth_register_firstname_lessthan1(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'ironman007@gmail.com',
            'password': 'ironisgood',
            'name_first': '',
            'name_last': 'Lee'
        }).raise_for_status()


# test the case that firstname is longer than 50 characters
def test_auth_register_firstname_morethan50(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'ironman007@gmail.com',
            'password': 'ironisgood',
            'name_first': 'Xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'name_last': 'Man'
        }).raise_for_status()


# test the case that lastname is lass than 1 character
def test_auth_register_lastname_lessthan1(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'ironman007@gmail.com',
            'password': 'ironisgood',
            'name_first': 'Iron',
            'name_last': ''
        }).raise_for_status()


# test the case that lastname is longer than 50 characters
def test_auth_register_lastname_morethan50(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/register', json={
            'email': 'ironman007@gmail.com',
            'password': 'ironisgood',
            'name_first': 'Iron',
            'name_last': 'Gggggggggggggggggggggggggggggggggggggggggggggggggggg'
        }).raise_for_status()


# test the return value for auth_register
def test_auth_register_return_types(url):
    resp_register = requests.post(url + 'auth/register', json={
        'email': 'ironman007@gmail.com',
        'password': 'ironisgood',
        'name_first': 'Iron',
        'name_last': 'Man'
    })
    return_value = json.loads(resp_register.text)
    assert isinstance(return_value['u_id'], int)
    assert isinstance(return_value['token'], str)


# test if the handle is unipue and less than 20
def test_auth_register_handle(url):
    # register 2 user with same name
    resp1_register = requests.post(url + 'auth/register', json={
        'email': 'boyu1@gmail.com',
        'password': 'boyu_pass',
        'name_first': 'Boyu',
        'name_last': 'Cai'
    })
    resp2_register = requests.post(url + 'auth/register', json={
        'email': 'boyu2@gmail.com',
        'password': 'boyu_pass',
        'name_first': 'Boyu',
        'name_last': 'Cai'
    })
    # register another 2 users with same name and longer than 20
    resp3_register = requests.post(url + 'auth/register', json={
        'email': 'boyu3@gmail.com',
        'password': 'boyu_pass',
        'name_first': 'Boyu',
        'name_last': 'Caiiiiiiiiiiiiiiiiii'
    })
    resp4_register = requests.post(url + 'auth/register', json={
        'email': 'boyu4@gmail.com',
        'password': 'boyu_pass',
        'name_first': 'Boyu',
        'name_last': 'Caiiiiiiiiiiiiiiiiii'
    })
    user1 = json.loads(resp1_register.text)
    user2 = json.loads(resp2_register.text)
    user3 = json.loads(resp3_register.text)
    user4 = json.loads(resp4_register.text)
    # get handles from user_profile
    resp1_profile = requests.get(url + 'user/profile', params={
        "token": user1["token"],
        "u_id": user1["u_id"]
    })
    resp2_profile = requests.get(url + 'user/profile', params={
        "token": user2["token"],
        "u_id": user2["u_id"]
    })
    resp3_profile = requests.get(url + 'user/profile', params={
        "token": user3["token"], "u_id": user3["u_id"]})
    resp4_profile = requests.get(url + 'user/profile', params={
        "token": user4["token"],
        "u_id": user4["u_id"]
    })
    user1_dict = json.loads(resp1_profile.text)['user']
    user2_dict = json.loads(resp2_profile.text)['user']
    user3_dict = json.loads(resp3_profile.text)['user']
    user4_dict = json.loads(resp4_profile.text)['user']
    handle1 = user1_dict['handle_str']
    handle2 = user2_dict['handle_str']
    handle3 = user3_dict['handle_str']
    handle4 = user4_dict['handle_str']
    # check length does not exist 20
    assert len(handle1) <= 20
    assert len(handle2) <= 20
    assert len(handle3) <= 20
    assert len(handle4) <= 20
    # check unique handle generation
    assert handle1 != handle2
    assert handle3 != handle4


# test the return value for auth_login
def test_auth_login_return_type(url):
    # register
    dict_user = {
        'email': 'cbyisaac@gmail.com',
        'password': 'boyupass',
        'name_first': 'Boyuuuuuuuuuu',
        'name_last': 'Caiiiiiiiiii',
    }
    requests.post(url + 'auth/register', json=dict_user)
    resp_login = requests.post(url + 'auth/login', json={
        'email': dict_user['email'],
        'password': dict_user['password']
    })
    login_dict = json.loads(resp_login.text)
    # check if u_id is an int and token is a string
    assert isinstance(login_dict['u_id'], int)
    assert isinstance(login_dict['token'], str)


# test the case that email is not valid for auth_login
def test_auth_login_email_not_valid(url):
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': r'team1.team1\team1_team1@google.com',
            'password': 'wendy_pass'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': 'team1.com',
            'password': 'wendy_pass'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': 'team&@gamil.com',
            'password': 'wendy_pass'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': 'Team1@google.com',
            'password': 'wendy_pass'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': '',
            'password': 'no_one_pass'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': '    @google.com',
            'password': 'maybe_one_pass'
        }).raise_for_status()


# test the case that email does not belongs to an user
def test_auth_login_email_not_match(url):
    # register an user
    dict_user = {
        'email': 'cbyisaac@gmail.com',
        'password': 'boyupass',
        'name_first': 'Boyuuuuuuuuuu',
        'name_last': 'Caiiiiiiiiii',
    }
    requests.post(url + 'auth/register', json=dict_user)
    # login with a wrong password
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': 'cbyissac@gmail.com',
            'password': 'boyupass'
        }).raise_for_status()


# test the case that the password is incorrect
def test_auth_login_password_incorrect(url):
    # register an user
    dict_user = {
        'email': 'cbyisaac@gmail.com',
        'password': 'boyupass',
        'name_first': 'Boyuuuuuuuuuu',
        'name_last': 'Caiiiiiiiiii',
    }
    requests.post(url + 'auth/register', json=dict_user)
    # login with a wrong password
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/login', json={
            'email': 'cbyisaac@gmail.com',
            'password': 'xukunpass'
        }).raise_for_status()


# test the case that token is valid for auth_logout
def test_auth_logout_valid_token(url):
    clear()
    test_data = creatData(url)
    user = test_data.register_weiqiang()
    resp_logout = requests.post(url + 'auth/logout', json={'token': user['token']})
    logout_status = json.loads(resp_logout.text)
    assert logout_status['is_success'] is True


# test the case that token is invalid for auth_logout
def test_auth_logout_invalid_token(url):
    # a ramdom token
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZWFtMSI6InRlYW0xIn0.\
        ICv4CTF9anBjCdNFp8fa_xHrmgUGVC001v7UjFwe9Kk'
    resp_logout = requests.post(url + 'auth/logout', json={'token': token})
    logout_status = json.loads(resp_logout.text)
    assert logout_status['is_success'] is False


# test the case that email is invalid for passwordreset request
def test_passwordreset_request_email_invalid(url):
    dict_user = {
        'email': 'cbyisaac@gmail.com',
        'password': 'boyupass',
        'name_first': 'Boyuuuuuuuuuu',
        'name_last': 'Caiiiiiiiiii',
    }
    requests.post(url + 'auth/register', json=dict_user)
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/passwordreset/request', json={
            'email': 'invalid.email.com'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/passwordreset/request', json={
            'email': 'cbyissac@gmail.com'
        }).raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        requests.post(url + 'auth/passwordreset/request', json={
            'email': ''
        }).raise_for_status()


# test the case that password reset request pass
def test_passwordreset_request_pass(url):
    dict_user = {
        'email': '138876722@qq.com',
        'password': 'yuhanpass',
        'name_first': 'Yuhan',
        'name_last': 'Liang',
    }
    requests.post(url + 'auth/register', json=dict_user)
    requests.post(url + 'auth/passwordreset/request', json=dict_user)
