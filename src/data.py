
USER_DATA = []
'''
    {
        'email': '123@gmail.com',
        'password': 'boyupass',
        'name_first': 'Boyu',
        'name_last': 'Cai',
        'u_id': 1,
        'token': "00001",
        'handle': "bcai"
    },
    {
        'email': '427@gmail.com',
        'password': 'wenyaopass',
        'name_first': 'Wenyao',
        'name_last': 'Chen',
        'u_id': 2,
        'token': "00002",
        'handle': "wchen"
    },
    {
        'email': '234@gmail.com',
        'password': 'weiqiangpass',
        'name_first': 'Weiqiang',
        'name_last': 'Zhuang',
        'u_id': 3,
        'token': "00003",
        'handle': "wzhuang"
    },
    {
        'email': '517@gmail.com',
        'password': 'yixuanpass',
        'name_first': 'Yixuan',
        'name_last': 'Chen',
        'u_id': 4,
        'token': "00004",
        'handle': "ychen"
    },
    {
        'email': '1021@gmail.com',
        'password': 'yuhanpass',
        'name_first': 'Yuhan',
        'name_last': 'Liang',
        'u_id': 5,
        'token': "00005",
        'handle': "yliang"
    }
]
'''
'''
{
    email
    password
    name_first
    name_last
    u_id
}
'''
LOGIN_DATA = []


FLOCKR_DATA = {
    'owner': [],
    'member': []
}


'''
'owner': [1],
'member': [1, 2, 3, 4, 5]
'''

CHANNEL_DATA = []
'''
{
    channel_id:
    name
    member(list of uid)
    owner(list of uid)
    is_public(true/false) <- channel_join
}
'''



MESSAGES_DATA = {}
'''
channel_id: [
    {
        'message_id'
        'u_id'
        'message'
        'time_created'
        'is_pinned'
        'reacts'
    }
]
'''
TOTAL_MESS_NUM = 0

MESSAGE_IDS = {}
'''
channel_id: [],
'''


RESET_CODE_LIST = []

ACTIVE_DATA = []

'''
{
    'channel_id':
    'time_finish':
}

'''