import pytest
from error import InputError
from auth import auth_register, auth_login, auth_logout, \
    auth_passwordreset_request, auth_passwordreset_reset
from other import clear, users_all
from data import USER_DATA


# test the case that the input email is mot (InputError)
def test_auth_register_email():
    clear()
    with pytest.raises(InputError):
        assert auth_register("team1.team1\team1_team1@google.com", "wendy_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("team1.com", "wendy_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("team&@gamil.com", "wendy_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("Team1@google.com", "wendy_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("Team1@google.com", "who_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("", "no_one_pass", "first", "last")
    with pytest.raises(InputError):
        assert auth_register("  @google.com", "maybe_one_pass", "first", "last")


# test the case that the email is already used
def test_auth_register_email_used():
    clear()
    auth_register("banana@gmail.com", "boyu_pass", "Boyu", "Cai")
    with pytest.raises(InputError):
        assert auth_register("banana@gmail.com", "boyu_pass", "Boyu", "Cai")


# test the case that the password is less than 6
def test_auth_register_password_lessthan6():
    clear()
    with pytest.raises(InputError):
        assert auth_register("apple@gmail.com", "boyu", "Boyu", "Cai")


# test the case that the lengh of the firstname is less than 1
def test_auth_register_firstname_lessthan1():
    clear()
    with pytest.raises(InputError):
        assert auth_register("grape@gmail.com", "boyu_pass", "", "Cai")


# test the case that the lengh of the firstname is greater than 50
def test_auth_register_firstname_greaterthan50():
    clear()
    with pytest.raises(InputError):
        assert auth_register("pear@gmail.com", "boyu_pass",
                             "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                             "Cai")


# test the case that the lengh of the lastname is less than 1
def test_auth_register_lastname_lessthan1():
    clear()
    with pytest.raises(InputError):
        assert auth_register("grape@gmail.com", "boyu_pass", "Boyu", "")


# test the case that the lengh of the lastname is greater than 50
def test_auth_register_lastname_greaterthan50():
    clear()
    with pytest.raises(InputError):
        assert auth_register("pear@gmail.com", "boyu_pass", "Boyu",
                             "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")


# test the case is correct
def test_auth_register_reture_type():
    clear()
    return_value = auth_register("banana.banana@gmail.com", "boyu_pass", "Boyu", "Cai")
    assert isinstance(return_value['u_id'], int)
    assert isinstance(return_value['token'], str)


# check whether handle is correct
def test_auth_register_handle():
    clear()
    user1 = auth_register("boyu1@gmail.com", "boyu_pass", "Boyu", "Cai")
    auth_register("boyu2@gmail.com", "boyu_pass", "Boyu", "Cai")
    auth_register("boyu3@gmail.com", "boyu_pass", "Boyu", "Caiiiiiiiiiiiiiiiiii")
    auth_register("boyu4@gmail.com", "boyu_pass", "Boyu", "Caiiiiiiiiiiiiiiiiii")

    user_dict = users_all(user1['token'])
    assert len(user_dict['users'][0]['handle_str']) <= 20
    assert len(user_dict['users'][1]['handle_str']) <= 20
    assert len(user_dict['users'][2]['handle_str']) <= 20
    assert len(user_dict['users'][3]['handle_str']) <= 20
    assert user_dict['users'][0]['handle_str'] != user_dict['users'][1]['handle_str']
    assert user_dict['users'][2]['handle_str'] != user_dict['users'][3]['handle_str']


# test the case email input is not volid
def test_auth_login_email():
    clear()
    with pytest.raises(InputError):
        assert auth_login("team1.team1\team1_team1@google.com", "wendy_pass")
    with pytest.raises(InputError):
        assert auth_login("team1.com", "wendy_pass")
    with pytest.raises(InputError):
        assert auth_login("team&@gamil.com", "wendy_pass")
    with pytest.raises(InputError):
        assert auth_login("Team1@google.com", "wendy_pass")
    with pytest.raises(InputError):
        assert auth_login("Team1@google.com", "who_pass")
    with pytest.raises(InputError):
        assert auth_login("", "no_one_pass")
    with pytest.raises(InputError):
        assert auth_login("  @google.com", "maybe_one_pass")


#test the case not input user
def test_auth_login_not_user():
    clear()
    with pytest.raises(InputError):
        assert auth_login("not.user@gmail.com", "jay_pass")


#test the case login in error password
def test_auth_login_password():
    clear()
    auth_register("cby@gmail.com", "boyu_pass", "Boyu", "Cai")
    with pytest.raises(InputError):
        assert auth_login("cby@gmail.com", "cby_pass")


# test the return type for auth_login
def test_auth_login_reture_type():
    clear()
    auth_register("isaac.cby@gmail.com", "boyu_pass", "Boyu", "Cai")
    return_value = auth_login("isaac.cby@gmail.com", "boyu_pass")
    assert len(return_value.keys()) == 2
    assert isinstance(return_value['u_id'], int)
    assert isinstance(return_value['token'], str)


# test the case logout with valid token
def test_auth_logout_valid_token():
    clear()
    weiqiang_token = auth_register('weiqiang.zhuang1@gmail.com',
                                   'weiqiangpass1', 'Weiqiang1', 'Zhuang1')
    auth_login("weiqiang.zhuang1@gmail.com", "weiqiangpass1")
    assert auth_logout(weiqiang_token['token'])['is_success'] is True


# test the case logout with invalid token
def test_auth_logout_invalid_token():
    clear()
    token_str = 'happy'
    assert auth_logout(token_str)['is_success'] is False


# logout the same person 2 times
def test_auth_logout_2times():
    clear()
    weiqiang_token = auth_register('weiqiang.zhuang1@gmail.com',
                                   'weiqiangpass1', 'Weiqiang1', 'Zhuang1')
    auth_login("weiqiang.zhuang1@gmail.com", "weiqiangpass1")
    auth_logout(weiqiang_token['token'])
    assert auth_logout(weiqiang_token['token'])['is_success'] is False


# test login after register and logout
def test_not_login_before():
    clear()
    weiqiang_token = auth_register('weiqiang.zhuang1@gmail.com',
                                   'weiqiangpass1', 'Weiqiang1', 'Zhuang1')
    auth_logout(weiqiang_token['token'])
    return_value = auth_login("weiqiang.zhuang1@gmail.com", "weiqiangpass1")
    assert return_value['token'] == weiqiang_token['token']
    

# test reset password request successfully
def test_auth_passwordreset_request_pass():
    clear()
    email = '451248071@qq.com'
    auth_register(email, 'weiqiangpass1', 'Weiqiang1', 'Zhuang1')
    for user in USER_DATA:
        if user['email'] == email:
            assert user['reset_code'] == ""
    auth_passwordreset_request(email)
    for user in USER_DATA:
        if user['email'] == email:
            assert user['reset_code'] != ""


# test reset password request invalid email
def test_auth_passwordreset_request_invalid_email():
    clear()
    with pytest.raises(InputError):
        assert auth_passwordreset_request("invalid.email.com")


# test reset password request email not user
def test_auth_passwordreset_request_not_user():
    clear()
    with pytest.raises(InputError):
        assert auth_passwordreset_request("notuser@gmail.com")


 # test reset password request invalid reset code
def test_auth_passwordreset_reset_code_not_valid():
    clear()
    with pytest.raises(InputError):
        assert auth_passwordreset_reset("invalid_code", "newpassword2")

# test reset/password new password is not valid
def test_auth_passwordreset_reset_password_not_valid():
    clear()
    email = "451248071@qq.com"
    auth_register(email, 'weiqiangpass1', 'Weiqiang1', 'Zhuang1')
    auth_passwordreset_request(email)
    reset_code = ''
    for user in USER_DATA:
        if user['email'] == email:
            reset_code = user['reset_code']
            break
    new_pwd = "123"
    with pytest.raises(InputError):
        assert auth_passwordreset_reset(reset_code, new_pwd)

