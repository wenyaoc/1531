import jwt
from data import LOGIN_DATA, TOTAL_MESS_NUM
from db_connector import DbConnector


def check_valid(token):
    db_connect = DbConnector()
    db_connect.cursor()
    sql = "SELECT token FROM project.user_data WHERE token=(%s)"
    value = (token,)
    db_connect.execute(sql, value)
    ret = db_connect.fetchone()

    if ret is None:
        db_connect.close()
        return False
    else:
        db_connect.close()
        return True


class TokenJwt:
    def __init__(self):
        self.secret = 'team1'

    def encode_token(self, user_dict):
        token = jwt.encode(user_dict, self.secret, algorithm='HS256').decode('utf-8')
        return str(token)

    def get_uid(self, token):
        user_dict = jwt.decode(token, self.secret, algorithms=['HS256'])
        return user_dict["u_id"]


# def get_new_messageid():
#     global TOTAL_MESS_NUM
#     TOTAL_MESS_NUM += 1
#     return TOTAL_MESS_NUM
