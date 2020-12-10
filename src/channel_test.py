from time import sleep
import pytest
from auth import auth_register
from channel import channel_invite, channel_details, channel_leave, \
    channel_join, channel_addowner, channel_removeowner, channel_messages
from channels import channels_create
from error import InputError, AccessError
from message import message_send
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


# test channel invite token is not valid
def test_channel_invite_invalid_token():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_dict = channels_create(boyu_dict['token'], "team1", True)  # cannot delete this line
    with pytest.raises(AccessError):
        # make sure only token is incorrect
        assert channel_invite("invalid.token", channel_dict['channel_id'], wenyao_dict['u_id'])


# test channel invite channe_ID is not valid
def test_channel_invite_channelid_notvalid():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channels_create(boyu_dict['token'], "team1", True)  # cannot delete this line
    with pytest.raises(InputError):
        # make sure only channel Id is incorrect
        assert channel_invite(boyu_dict['token'], -1, wenyao_dict['u_id'])


# test channel invite U_ID is not valid
def test_channel_invite_uid_not_valid():
    boyu_dict, _, _, _, _ = initialise_data()

    channel_team_ham = channels_create(boyu_dict['token'], "teamham", True)
    with pytest.raises(InputError):
        assert channel_invite(boyu_dict['token'], channel_team_ham['channel_id'], -1)


# the authorised user is not already a member of the channel
def test_channel_invite_not_member():
    boyu_dict, wenyao_dict, _, yixuan_dict, _ = initialise_data()

    channel_team_salami = channels_create(boyu_dict['token'], "team1", True)
    with pytest.raises(AccessError):
        assert channel_invite(wenyao_dict['token'], channel_team_salami['channel_id'],
                              yixuan_dict['u_id'])


# test the return value of channel_invite
def test_channel_invite_return():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_burger = channels_create(boyu_dict['token'], "teamBurger", True)
    channel_team_burger_id = channel_team_burger['channel_id']
    return_value = channel_invite(boyu_dict['token'], channel_team_burger_id, wenyao_dict['u_id'])
    assert return_value == {}


# test if channel_invite store three data correctly
def test_channel_invite_data_store():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_lamb = channels_create(boyu_dict['token'], "teamlamb", True)
    channel_team_lamb_id = channel_team_lamb['channel_id']
    channel_invite(boyu_dict['token'], channel_team_lamb_id, wenyao_dict['u_id'])
    assert channel_details(boyu_dict['token'], channel_team_lamb_id) == {
        'name': 'teamlamb',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
    }


# test channel details token is not valid
def test_channel_details_invalid_token():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_team_bacon = channels_create(boyu_dict['token'], "teamBacon", True)
    with pytest.raises(AccessError):
        assert channel_details("invalid_token", channel_team_bacon['channel_id'])


# test channel details channel_Id is not valid
def test_channel_details_channelid_not_valid():
    boyu_dict, _, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channel_details(boyu_dict['token'], -1)


# test channel details is AccessError
def test_channel_details_accesserror():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_bacon = channels_create(boyu_dict['token'], "teamBacon", True)
    with pytest.raises(AccessError):
        assert channel_details(wenyao_dict['token'], channel_team_bacon['channel_id'])


def test_channel_details_pass():
    boyu_dict, _, _, _, _ = initialise_data()

    channel_team_icecream = channels_create(boyu_dict['token'], "teamIcecream", True)
    assert channel_details((boyu_dict['token']), channel_team_icecream['channel_id']) == {
        'name': 'teamIcecream',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
    }

# test channel_leave
# test channel details token is not valid
def test_channel_leave_invalid_token():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_team_bacon = channels_create(boyu_dict['token'], "teamBacon", True)
    with pytest.raises(AccessError):
        assert channel_leave("invalid_token", channel_team_bacon['channel_id'])


# test channelid is not valid
def test_channel_leave_channelid_not_valid():
    boyu_dict, _, _, _, _ = initialise_data()
    with pytest.raises(InputError):
        assert channel_leave(boyu_dict['token'], -1)


# test is AccessError
def test_channel_leave_accesserror():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_tacco = channels_create(boyu_dict['token'], "teamTacco", True)
    with pytest.raises(AccessError):
        assert channel_leave(wenyao_dict['token'], channel_team_tacco['channel_id'])


# check the return value for channel_leave
def test_channel_leave_return():
    boyu_dict, _, _, _, _ = initialise_data()

    channel_team_sausages = channels_create(boyu_dict['token'], "teamsausages", True)
    assert channel_leave(boyu_dict['token'], channel_team_sausages['channel_id']) == {}


# check the data managed correctly when a member call channel_leave
def test_channel_leave_member():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_noodles = channels_create(boyu_dict['token'], "teamNoodles", True)
    channel_team_noodles_id = channel_team_noodles['channel_id']
    channel_invite(boyu_dict['token'], channel_team_noodles_id, wenyao_dict['u_id'])  # add a member
    channel_leave(wenyao_dict['token'], channel_team_noodles_id)  # the member leave the channel
    assert channel_details((boyu_dict['token']), channel_team_noodles_id) == {
        'name': 'teamNoodles',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
    }


# check the data managed correctly when an owner call channel_leave
# check the data managed correctly when a member call channel_leave
def test_channel_leave_owner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_turkey = channels_create(boyu_dict['token'], "teamTurkey", True)
    channel_team_turkey_id = channel_team_turkey['channel_id']
    channel_invite(boyu_dict['token'], channel_team_turkey_id, wenyao_dict['u_id'])  # add a member
    #the owner leave the channel
    channel_leave(boyu_dict['token'], channel_team_turkey_id)
    assert channel_details((wenyao_dict['token']), channel_team_turkey_id) == {
        'name': 'teamTurkey',
        'owner_members': [],
        'all_members': [
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
    }


# test channel_join token is not valid
def test_channel_join_invalid_token():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_kiwi_id = channels_create(boyu_dict['token'], "team2", False)
    with pytest.raises(AccessError):
        assert channel_join("invalid_token", channel_kiwi_id['channel_id'])

# test channel_ID is not valid
def test_channel_join_channelid_not_valid1():
    boyu_dict, _, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channel_join(boyu_dict['token'], {'channel_id': -1})


# test channel_ID is not valid
def test_channel_join_channelid_not_valid2():
    boyu_dict, _, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channel_join(boyu_dict['token'], -1)


# check AccessError when channels is private
def test_channel_join_accesserror_private():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_kiwi_id = channels_create(boyu_dict['token'], "team2", False)
    with pytest.raises(AccessError):
        assert channel_join(wenyao_dict['token'], channel_kiwi_id['channel_id'])


# test the return value when flockr owner join the channel
def test_channel_join_flockr_owner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_candy = channels_create(wenyao_dict['token'], "teamCandy", True)
    assert channel_join(boyu_dict['token'], channel_team_candy['channel_id']) == {}


# check if the return value when a user join the channel
def test_channel_join_return():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_candy = channels_create(boyu_dict['token'], "teamCandy", True)
    assert channel_join(wenyao_dict['token'], channel_team_candy['channel_id']) == {}


# check if the data store correctly
# when a member join a public channel
def test_channel_join_notowner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_milk = channels_create(boyu_dict['token'], "teamMilk", True)
    channel_team_milk_id = channel_team_milk['channel_id']
    channel_join(wenyao_dict['token'], channel_team_milk_id)
    # check the values returned by channel_details
    assert channel_details(boyu_dict['token'], channel_team_milk_id) == {
        'name': 'teamMilk',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': wenyao_dict['u_id'],
                'name_first': 'Wenyao',
                'name_last': 'Chen',
                'profile_img_url': '',
            }
        ],
    }


# check if the data store correctly
# when a flockr owner join a private channel
def test_channel_join_owner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    channel_team_milk = channels_create(wenyao_dict['token'], "teamMilk", False)
    channel_team_milk_id = channel_team_milk['channel_id']
    channel_join(boyu_dict['token'], channel_team_milk_id)
    # check the values returned by channel_details
    detalis = channel_details(boyu_dict['token'], channel_team_milk_id)['all_members']
    u_id_list = []
    for member in detalis:
        u_id_list.append(member['u_id'])

    assert boyu_dict['u_id'] in u_id_list


    # assert channel_details(boyu_dict['token'], channel_team_milk_id) == {
    #     'name': 'teamMilk',
    #     'owner_members': [
    #         {
    #             'u_id': wenyao_dict['u_id'],
    #             'name_first': 'Wenyao',
    #             'name_last': 'Chen',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': None,
    #         }
    #     ],
    #     'all_members': [
    #         {
    #             'u_id': wenyao_dict['u_id'],
    #             'name_first': 'Wenyao',
    #             'name_last': 'Chen',
    #             'profile_img_url': ,
    #         },
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': ,
    #         },
    #     ],
    # }


# test channel add owner token is not valid
def test_channel_addowner_invalid_token():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()
    team_pineapple = channels_create(boyu_dict['token'], "teamPineapple", True)
    team_pineapple_id = team_pineapple['channel_id']
    channel_addowner(boyu_dict['token'], team_pineapple_id, weiqiang_dict['u_id'])
    with pytest.raises(AccessError):
        assert channel_addowner("invalid_token", team_pineapple_id, boyu_dict['u_id'])

# test channel id is not valid
def test_channel_addowner_inputerror_invalid_id():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channel_addowner(wenyao_dict['token'], 9999, boyu_dict['u_id'])


# InputError when user with user id u_id  is already an owner of the channel
def test_channel_addowner_inputerror_user_already_owner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    team_strawberry = channels_create(wenyao_dict['token'], "TeamStrawberry", True)
    team_strawberry_id = team_strawberry['channel_id']
    channel_addowner(wenyao_dict['token'], team_strawberry_id, boyu_dict['u_id'])
    with pytest.raises(InputError):
        assert channel_addowner(wenyao_dict['token'], team_strawberry_id, boyu_dict['u_id'])


# AccessError when the authorised user is not an owner of this channel
def test_channel_addowner_accesserror_authorised_user_not_owner():
    _, wenyao_dict, weiqiang_dict, yixuan_dict, _ = initialise_data()

    team_blueberry = channels_create(wenyao_dict['token'], "TeamBlueberry", True)
    team_blueberry_id = team_blueberry['channel_id']
    with pytest.raises(AccessError):
        assert channel_addowner(weiqiang_dict['token'], team_blueberry_id, yixuan_dict['u_id'])


# AccessError when the authorised user is owner of the flockr but not member if the channel
def test_channel_addowner_accesserror_flockr_owner_not_member():
    boyu_dict, wenyao_dict, _, yixuan_dict, _ = initialise_data()

    team_raspberry = channels_create(wenyao_dict['token'], "TeamRaspberry", True)
    team_raspberry_id = team_raspberry['channel_id']
    with pytest.raises(AccessError):
        assert channel_addowner(boyu_dict['token'], team_raspberry_id, yixuan_dict['u_id'])


# Valid input when the authorised user is the owner of this channel
def test_channel_addowner_owner_of_channel():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()

    team_pineapple = channels_create(boyu_dict['token'], "teamPineapple", True)
    team_pineapple_id = team_pineapple['channel_id']
    channel_addowner(boyu_dict['token'], team_pineapple_id, weiqiang_dict['u_id'])
    details = channel_details(weiqiang_dict['token'], team_pineapple_id)
    assert details == {
        'name': 'teamPineapple',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
    }


# Valid input when the authorised user is the owner of flockr
def test_channel_addowner_owner_of_flockr():
    boyu_dict, wenyao_dict, weiqiang_dict, _, _ = initialise_data()

    team_watermelon = channels_create(wenyao_dict['token'], "teamWatermelon", True)
    team_watermelon_id = team_watermelon['channel_id']
    channel_invite(wenyao_dict['token'], team_watermelon_id, boyu_dict['u_id'])  # add a member
    channel_addowner(boyu_dict['token'], team_watermelon_id, weiqiang_dict['u_id'])
    detalis = channel_details(weiqiang_dict['token'], team_watermelon_id)['owner_members']
    u_id_list = []
    for owner in detalis:
        u_id_list.append(owner['u_id'])

    assert weiqiang_dict['u_id'] in u_id_list
    # details = channel_details(weiqiang_dict['token'], team_watermelon_id)
    # assert details == {
    #     'name': 'teamWatermelon',
    #     'owner_members': [
    #         {
    #             'u_id': wenyao_dict['u_id'],
    #             'name_first': 'Wenyao',
    #             'name_last': 'Chen',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': weiqiang_dict['u_id'],
    #             'name_first': 'Weiqiang',
    #             'name_last': 'Zhuang',
    #             'profile_img_url': None,
    #         }
    #     ],
    #     'all_members': [
    #         {
    #             'u_id': wenyao_dict['u_id'],
    #             'name_first': 'Wenyao',
    #             'name_last': 'Chen',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': weiqiang_dict['u_id'],
    #             'name_first': 'Weiqiang',
    #             'name_last': 'Zhuang',
    #             'profile_img_url': None,
    #         }
    #     ],
    #}


# Valid input when the owner to be added is already a member
def test_channel_addowner_already_member():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()

    team_avocado = channels_create(boyu_dict['token'], "teamAvocado", True)
    team_avocado_id = team_avocado['channel_id']
    channel_invite(boyu_dict['token'], team_avocado_id, weiqiang_dict['u_id'])
    channel_addowner(boyu_dict['token'], team_avocado_id, weiqiang_dict['u_id'])
    details = channel_details(weiqiang_dict['token'], team_avocado_id)
    assert details == {
        'name': 'teamAvocado',
        'owner_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
    }

# test invalid token in removeowner
def test_channel_removeowner_invalid_token():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()
    team_pears = channels_create(boyu_dict['token'], "teamPears", True)
    team_pears_id = team_pears['channel_id']
    channel_addowner(boyu_dict['token'], team_pears_id, weiqiang_dict['u_id'])
    channel_removeowner(weiqiang_dict['token'], team_pears_id, boyu_dict['u_id'])
    with pytest.raises(AccessError):
        assert channel_addowner("invalid_token", team_pears_id, boyu_dict['u_id'])


# InputError when Channel ID is not a valid channel
def test_channel_removeowner_inputerror_invalid_id():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    with pytest.raises(InputError):
        assert channel_removeowner(wenyao_dict['token'], 9999, boyu_dict['u_id'])


# InputError when user with user id u_id is not an owner of the channel
def test_channel_removeowner_inputerror_user_not_owner():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    team_apple = channels_create(boyu_dict['token'], "teamApple", True)
    team_apple_id = team_apple['channel_id']
    with pytest.raises(InputError):
        assert channel_removeowner(boyu_dict['token'], team_apple_id, wenyao_dict['u_id'])


# AccessError when the authorised user is not an owner of this channel
def test_channel_removeowner_accesserror_authorised_user_not_owner():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()

    team_cherry = channels_create(boyu_dict['token'], "teamCherry", True)
    team_cherry_id = team_cherry['channel_id']
    channel_invite(boyu_dict['token'], team_cherry_id, weiqiang_dict['u_id'])
    with pytest.raises(AccessError):
        assert channel_removeowner(weiqiang_dict['token'], team_cherry_id, boyu_dict['u_id'])


# AccessError when the authorised user is an owner of the flockr but not a member of this channel
def test_channel_removeowner_accesserror_authorised_flockr_owner_not_member():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    team_coconut = channels_create(wenyao_dict['token'], "teamCoconut", True)
    team_coconut_id = team_coconut['channel_id']
    with pytest.raises(AccessError):
        assert channel_removeowner(boyu_dict['token'], team_coconut_id, wenyao_dict['u_id'])


# Valid input when the authorised user is the owner of this channel
def test_channel_delete_owner_of_channel():
    boyu_dict, _, weiqiang_dict, _, _ = initialise_data()

    team_pears = channels_create(boyu_dict['token'], "teamPears", True)
    team_pears_id = team_pears['channel_id']
    channel_addowner(boyu_dict['token'], team_pears_id, weiqiang_dict['u_id'])
    channel_removeowner(weiqiang_dict['token'], team_pears_id, boyu_dict['u_id'])
    details = channel_details(weiqiang_dict['token'], team_pears_id)
    # check the values returned by channel_details
    assert details == {
        'name': 'teamPears',
        'owner_members': [
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
        'all_members': [
            {
                'u_id': boyu_dict['u_id'],
                'name_first': 'Boyu',
                'name_last': 'Cai',
                'profile_img_url': '',
            },
            {
                'u_id': weiqiang_dict['u_id'],
                'name_first': 'Weiqiang',
                'name_last': 'Zhuang',
                'profile_img_url': '',
            }
        ],
    }


# Valid input when the authorised user is the owner flockr
def test_channel_delete_owner_of_flockr():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()

    team_mandarin = channels_create(wenyao_dict['token'], "teamMandarin", True)
    team_mandarin_id = team_mandarin['channel_id']
    channel_invite(wenyao_dict['token'], team_mandarin_id, boyu_dict['u_id'])
    channel_removeowner(boyu_dict['token'], team_mandarin_id, wenyao_dict['u_id'])
    details = channel_details(boyu_dict['token'], team_mandarin_id)['owner_members']
    u_id_list = []
    for owner in details:
        u_id_list.append(owner['u_id'])

    assert wenyao_dict['u_id'] not in u_id_list
    # check the values returned by channel_details
    # assert details == {
    #     'name': 'teamMandarin',
    #     'owner_members': [
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': None,
    #         }
    #     ],
    #     'all_members': [
    #         {
    #             'u_id': wenyao_dict['u_id'],
    #             'name_first': 'Wenyao',
    #             'name_last': 'Chen',
    #             'profile_img_url': None,
    #         },
    #         {
    #             'u_id': boyu_dict['u_id'],
    #             'name_first': 'Boyu',
    #             'name_last': 'Cai',
    #             'profile_img_url': None,
    #         },
    #     ],
    # }


# test token is not valid
def test_channel_message_invalid_token():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello2')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello3')
    with pytest.raises(AccessError):
        assert channel_messages("invalid_token", channel_1['channel_id'], 1)


#test channel id is not volid
def test_channel_messages_invalid_channel_id():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    message_send(boyu_dict['token'], channel_1['channel_id'], "hello")
    channel_id_2 = {'channel_id': -1}
    with pytest.raises(InputError):
        assert channel_messages(wenyao_dict['token'], channel_id_2['channel_id'], 0)


# test channel messages is not searchable
def test_channel_messages_greater_total():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello2')
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello3')
    with pytest.raises(InputError):
        assert channel_messages(boyu_dict['token'], channel_1['channel_id'], 10)


#test channel message user is not a member
def test_channel_messages_user_not_member():
    boyu_dict, wenyao_dict, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    with pytest.raises(AccessError):
        assert channel_messages(wenyao_dict['token'], channel_1['channel_id'], 0)


# test channel messages is pass
def test_channel_messages():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    id_1 = message_send(boyu_dict['token'], channel_1['channel_id'], 'hello1')
    sleep(1)
    id_2 = message_send(boyu_dict['token'], channel_1['channel_id'], 'hello2')
    sleep(1)
    id_3 = message_send(boyu_dict['token'], channel_1['channel_id'], 'hello3')
    sleep(1)
    show_message = channel_messages(boyu_dict["token"], channel_1["channel_id"], 0)
    # check if it returns correctly
    assert len(show_message.keys()) == 3
    assert len(show_message['messages'][0].keys()) == 7
    assert show_message['start'] == 0
    assert show_message['end'] == -1
    assert show_message['messages'][0]['message'] == 'hello3'

    # print (show_message['messages'][0]['message'])
    assert show_message['messages'][0]['message_id'] == id_3['message_id']
    assert show_message['messages'][0]['u_id'] == boyu_dict['u_id']
    assert show_message['messages'][0]['is_pinned'] is False
    assert show_message['messages'][0]['reacts'][0] == {
        'is_this_user_reacted': False,
        'react_id': 1,
        'u_ids': []}
    assert show_message['messages'][1]['message'] == 'hello2'
    assert show_message['messages'][1]['message_id'] == id_2['message_id']
    assert show_message['messages'][1]['u_id'] == boyu_dict['u_id']
    assert show_message['messages'][1]['reacts'][0] == {
        'is_this_user_reacted': False,
        'react_id': 1,
        'u_ids': []}
    assert show_message['messages'][2]['message'] == 'hello1'
    assert show_message['messages'][2]['message_id'] == id_1['message_id']
    assert show_message['messages'][2]['u_id'] == boyu_dict['u_id']
    assert show_message['messages'][2]['reacts'][0] == {
        'is_this_user_reacted': False,
        'react_id': 1,
        'u_ids': []}


#test channel messages is out of range
def test_channel_messages_greater_than_50():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    for _ in range(60):
        message_send(boyu_dict['token'], channel_1['channel_id'], 'hello')
    show_message = channel_messages(boyu_dict['token'], channel_1['channel_id'], 0)
    assert show_message["end"] == 50


#test channel messages is begin at 9
def test_channel_messages_begin_at_9():
    boyu_dict, _, _, _, _ = initialise_data()
    channel_1 = channels_create(boyu_dict['token'], 'channel_1', True)
    for _ in range(60):
        message_send(boyu_dict['token'], channel_1['channel_id'], 'hello')
    show_message = channel_messages(boyu_dict['token'], channel_1['channel_id'], 9)
    assert show_message["end"] == 59
