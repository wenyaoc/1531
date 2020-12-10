import pytest
from auth import auth_register
from error import InputError, AccessError
from other import clear
from user import user_profile, user_profile_setname, user_profile_sethandle, user_profile_setemail, user_profile_uploadphoto
from channels import channels_create

# Using an image jpg
IMG_URL = 'https://upload.wikimedia.org/wikipedia/commons/4/48/Unsw_library.jpg'
# For invalid png image for testing
INVALID_IMG_URL = 'https://en.wikipedia.org/wiki/University_of_New_South_Wales#/media/File:ARC_UNSW_logo.png'

def initialise_data():
    clear()
    boyu_dict = auth_register('cbyisaac@gmail.com', 'boyupass', 'Boyu', 'Cai')
    yuhan_dict = auth_register('yuhan.liang1021@gmail.com', 'yuhanpass', 'Yuhan', 'Liang')
    channel_team1 = channels_create(boyu_dict['token'], "team1", True)
    return boyu_dict, yuhan_dict, channel_team1


# test token is not valid
def test_user_profile_token_not_valid():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(AccessError):
        assert user_profile("invalid_token", boyu_dict['u_id'])

# test user u_id is not valid
def test_user_profile_u_id_not_valid():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile(boyu_dict['token'], -1)


# test user call user_profile himself
def test_user_profile_u_id_same_user():
    boyu_dict, _, _ = initialise_data()
    profile_dict = user_profile(boyu_dict['token'], boyu_dict['u_id'])
    # check length is equal 5
    assert len(profile_dict['user'].keys()) == 6
    assert profile_dict['user']['u_id'] == boyu_dict['u_id']
    assert profile_dict['user']['email'] == 'cbyisaac@gmail.com'
    assert profile_dict['user']['name_first'] == 'Boyu'
    assert profile_dict['user']['name_last'] == 'Cai'
    assert len(profile_dict['user']['handle_str']) <= 20


# test user check other user's user_profile
def test_user_profile_u_id_diff_user():
    boyu_dict, yuhan_dict, _ = initialise_data()
    profile_dict = user_profile(yuhan_dict['token'], boyu_dict['u_id'])
    assert len(profile_dict['user'].keys()) == 6
    assert profile_dict['user']['u_id'] == boyu_dict['u_id']
    assert profile_dict['user']['email'] == 'cbyisaac@gmail.com'
    assert profile_dict['user']['name_first'] == 'Boyu'
    assert profile_dict['user']['name_last'] == 'Cai'
    assert len(profile_dict['user']['handle_str']) <= 20


# test token is not valid
def test_user_profile_setname_token_not_valid():
    with pytest.raises(AccessError):
        assert user_profile_setname("invalid_token", 'xukun', 'He')

# test the case that the first name is empty
def test_user_profile_setname_name_empty_firstname():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setname(boyu_dict['token'], '', 'He')


# test the case that the last name is empty
def test_user_profile_setname_name_empty_lastname():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setname(boyu_dict['token'], 'xukun', '')


# test first_name too long
def test_user_profile_setname_firstname_longerthan50():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setname(boyu_dict['token'],
                                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'He')


# test last_name too long
def test_user_profile_setname_lastname_longerthan50():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setname(boyu_dict['token'], 'xukun',
                                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')


# change last name
def test_user_profile_setname_change_firstname():
    boyu_dict, _, _ = initialise_data()
    user_profile_setname(boyu_dict['token'], 'Boyu', 'He')
    # user user_profile to compare
    profile_dict = user_profile(boyu_dict['token'], boyu_dict['u_id'])
    assert profile_dict['user']['name_first'] == 'Boyu'
    assert profile_dict['user']['name_last'] == 'He'


# change first name
def test_user_profile_setname_change_secondname():
    boyu_dict, _, _ = initialise_data()
    user_profile_setname(boyu_dict['token'], 'Xukun', 'Cai')
    profile_dict = user_profile(boyu_dict['token'], boyu_dict['u_id'])
    assert profile_dict['user']['name_first'] == 'Xukun'
    assert profile_dict['user']['name_last'] == 'Cai'


# test token is not valid
def test_user_profile_setmail_token_not_valid():
    with pytest.raises(AccessError):
        assert user_profile_setemail("invalid_token", 'cxkisaac@gmail.com')

# email methond is not valid
def test_user_profile_setemail_email_not_valid():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setemail(boyu_dict['token'], '...123')


# email methond is not valid
def test_user_profile_setemail_email_already_used():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_setemail(boyu_dict['token'], 'yuhan.liang1021@gmail.com')


# test update email
def test_user_profile_setemail_email_valid():
    boyu_dict, _, _ = initialise_data()
    # set legal email
    user_profile_setemail(boyu_dict['token'], 'cxkisaac@gmail.com')
    profile_dict = user_profile(boyu_dict['token'], boyu_dict['u_id'])
    assert profile_dict['user']['email'] == 'cxkisaac@gmail.com'


# test token is not valid
def test_user_profile_sethandle_token_not_valid():
    with pytest.raises(AccessError):
        assert user_profile_sethandle("invalid_token", 'wulifanfan')

# test the case that the handle is smaller than 3
def test_user_profile_sethandle_inputerror_smallerthan3():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_sethandle(boyu_dict['token'], 'a')


# test the case that the handle is greater than 20
def test_user_profile_sethandle_inputerror_greaterthan20():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_sethandle(boyu_dict['token'], 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')


# test the case that the handle is already used
def test_user_profile_sethandle_inputerror_used_handle():
    boyu_dict, yuhan_dict, _ = initialise_data()
    user_profile_sethandle(yuhan_dict['token'], 'yuhan')
    with pytest.raises(InputError):
        assert user_profile_sethandle(boyu_dict['token'], 'yuhan')


def test_user_profile_sethandle_pass():
    boyu_dict, _, _ = initialise_data()
    # reset handle is legal
    user_profile_sethandle(boyu_dict['token'], "caixukun")
    profile_dict = user_profile(boyu_dict['token'], boyu_dict['u_id'])
    assert profile_dict['user']['handle_str'] == 'caixukun'


# test token is not valid
def test_user_profile_uploadphoto_token_not_valid():
    with pytest.raises(AccessError):
        assert user_profile_uploadphoto("invalid_token", IMG_URL, 20, 20, 100, 100)


#test img_url is invalid
def test_user_profile_uploadphoto_invalid_img_url():
    boyu_dict, _, _ = initialise_data()
    invalid_url = 'https://upload.wikimedia.org/wikipedia/commons/5/48/Unsw_library.jpg'
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], invalid_url, 20, 20, 100, 100)


# test cases that the dimensions are invalid
def test_user_profile_uploadphoto_invalid_dimensions():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 100000, 20, 100, 100)
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 20, 100000, 100, 100)
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 20, 20, 100000, 100)
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 20, 20, 100, 100000)
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 20, 0, 0, 20)
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], IMG_URL, 0, 20, 20, 0)


# test image uploaded is not a JPG
def test_user_profile_uploadphoto_not_jpg():
    boyu_dict, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert user_profile_uploadphoto(boyu_dict['token'], INVALID_IMG_URL, 20, 20, 100, 100)
