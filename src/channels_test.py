import pytest
from channels import channels_list, channels_listall, channels_create
from error import InputError, AccessError
from auth import auth_register
from other import clear

def initialise_data():
    clear()
    boyu_dict = auth_register('cbyisaac@gmail.com', 'boyupass', 'Boyu', 'Cai')
    wenyao_dict = auth_register('wenyaochen427@gmail.com', 'wenyaopass', 'Wenyao', 'Chen')
    weiqiang_dict = auth_register('weiqiangzhuang24@gmail.com', 'weiqiangpass',
                                  'Weiqiang', 'Zhuang')
    yixuan_dict = auth_register('yison517@gmail.com', 'yixuanpass', 'Yixuan', 'Chen')
    yuhan_dict = auth_register('yuhan.liang1021@gmail.com', 'yuhanpass', 'Yuhan', 'Liang')
    return boyu_dict, wenyao_dict, weiqiang_dict, yixuan_dict, yuhan_dict

# test the case that token is invalid for channels create
def test_channels_create_invalid_token():
    with pytest.raises(AccessError):
        assert channels_create("F1_is_boring", "The_F1", True)


# test the case that the input token is invalid for channels listall
def test_channels_listall_invalid_token():
    with pytest.raises(AccessError):
        assert channels_listall("PikaPika")


# test the case that the input token is invalid for channels list
def test_channels_list_invalid_token():
    boyu_dict, _, _, _, _ = initialise_data()

    channels_create(boyu_dict['token'], "TeamApple", False) # create new channels
    with pytest.raises(AccessError):
        assert channels_list("PikaPika")


# test the case that name is more than 20 characters long
def test_channels_create_input_error():
    boyu_dict, _, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channels_create(boyu_dict['token'], "a name longer than 20 characters", True)

# test if the channel id returned by test_channels is an integer
def test_channels_return_value():
    boyu_dict, _, _, _, _ = initialise_data()

    team_apple = channels_create(boyu_dict['token'], "TeamApple", False) # create new channels
    assert isinstance(team_apple['channel_id'], int) # check if the return type is int


# test if the data for the new channel store successfully
def test_channels_create_valid_name():
    boyu_dict, _, _, _, _ = initialise_data()

    prev_channels = channels_listall(boyu_dict['token'])
    num_prev_channels = len(prev_channels["channels"]) # get the previous channels numbers
    channels_create(boyu_dict['token'], "TeamBanana", False) # create new channels
    curr_channels = channels_listall(boyu_dict['token'])
    num_curr_channels = len(curr_channels["channels"]) # get the new channels numbers
    assert num_curr_channels - num_prev_channels == 1 # check if the number increase


#test the case that the authorised user haven't joined any channels
def test_channels_list_havent_join_channels():
    _, _, _, _, _ = initialise_data()

    pikachu_token = auth_register('pikachu@gmail.com', 'pikachupass', 'Pikachu', 'Pikachu')
    assert channels_listall(pikachu_token['token']) == {'channels':[]}


# test the case that the authorised user joined some of the channels
def test_channels_list_join_some_channels():
    _, _, weiqiang_dict, yixuan_dict, _ = initialise_data()

    weiqiang_prev_channels = channels_list(weiqiang_dict['token'])
    yixuan_prev_channels = channels_list(yixuan_dict['token'])
    # creat 2 channels including different members
    team_orange = channels_create(weiqiang_dict['token'], "TeamOrange", False) # create new channel
    team_orange_id = team_orange['channel_id']
    team_grape = channels_create(yixuan_dict['token'], "TeamGrape", False) # create new channel
    team_grape_id = team_grape['channel_id']
    # append the new added channel to the previous channels respectively
    team_orange_dict = {'channel_id': team_orange_id, 'name': 'TeamOrange'}
    team_grape_dict = {'channel_id': team_grape_id, 'name': 'TeamGrape'}
    weiqiang_prev_channels['channels'].append(team_orange_dict)
    yixuan_prev_channels['channels'].append(team_grape_dict)
    # get the current list of channel for the 2 users
    weiqiang_curr_channels = channels_list(weiqiang_dict['token'])
    yixuan_curr_channels = channels_list(yixuan_dict['token'])
    # check if lists are same
    assert weiqiang_prev_channels == weiqiang_curr_channels
    assert yixuan_prev_channels == yixuan_curr_channels


# test the case that the authorised user haven't joined any channels
def test_channels_listall_havent_join_channels():
    boyu_dict, _, _, _, _ = initialise_data()

    pichu_token = auth_register('pichu@gmail.com', 'pikachupass', 'Pikachu', 'Pikachu')
    channels_create(boyu_dict['token'], "TeamApple", False) # create new channels
    assert channels_listall(pichu_token['token']) == channels_listall(boyu_dict['token'])



# test the case that the authorised user koined all channels
def test_channels_listall():
    _, _, _, yixuan_dict, yuhan_dict = initialise_data()

    # get the previous channels for yuhan
    yuhan_prev_channels = channels_listall(yuhan_dict['token'])

    # creat 2 channels including different members
    team_lemon = channels_create(yixuan_dict['token'], "teamLemon", False)
    team_lemon_id = team_lemon['channel_id']
    team_pears = channels_create(yuhan_dict['token'], "teamPears", False)
    team_pears_id = team_pears['channel_id']

    # append the new added channels to the previous channels list
    team_lemon_dict = {'channel_id': team_lemon_id, 'name': 'teamLemon'}
    team_pears_dict = {'channel_id': team_pears_id, 'name': 'teamPears'}
    yuhan_prev_channels['channels'].append(team_lemon_dict)
    yuhan_prev_channels['channels'].append(team_pears_dict)
    # get the current channel list
    yuhan_curr_channels = channels_listall(yuhan_dict['token'])

    # check if the list is same
    assert yuhan_prev_channels == yuhan_curr_channels
