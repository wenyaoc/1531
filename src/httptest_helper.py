import json
import re
import signal
from subprocess import Popen, PIPE
from time import sleep
import pytest
import requests


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


class creatData:
    def __init__(self, url):
        self.url = url

    def register_wenyao(self):
        dict_wenyao = {
            'email': 'wenyaochen427@gmail.com',
            'password': 'wenyaopass',
            'name_first': 'Wenyao',
            'name_last': 'Chen',
        }
        resp_wenyao = requests.post(self.url + 'auth/register', json=dict_wenyao)
        return json.loads(resp_wenyao.text)

    def register_boyu(self):
        dict_boyu = {
            'email': 'cbyisaac@gmail.com',
            'password': 'boyupass',
            'name_first': 'Boyu',
            'name_last': 'Cai',
        }
        resp_boyu = requests.post(self.url + 'auth/register', json=dict_boyu)
        return json.loads(resp_boyu.text)

    def register_weiqiang(self):
        dict_weiqiang = {
            'email': 'weiqiangzhuang24@gmail.com',
            'password': 'weiqiangpass',
            'name_first': 'Weiqiang',
            'name_last': 'Zhuang',
        }
        resp_weiqiang = requests.post(self.url + 'auth/register', json=dict_weiqiang)
        return json.loads(resp_weiqiang.text)

    def register_user(self, email, password, name_first, name_last):
        dict_user = {
            'email': email,
            'password': password,
            'name_first': name_first,
            'name_last': name_last,
        }
        resp_user = requests.post(self.url + 'auth/register', json=dict_user)
        return json.loads(resp_user.text)

    def creat_channel(self, token, name, is_public):
        dict_channel = {
            'token': token,
            'name': name,
            'is_public': is_public
        }
        resp_channel = requests.post(self.url + 'channels/create', json=dict_channel)
        return json.loads(resp_channel.text)
