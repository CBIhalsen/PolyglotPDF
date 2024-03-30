
# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import hashlib
import time
from importlib import reload

reload(sys)
# Note that Youdao does not support list translation, not recommended!
#注意有道不支持列表翻译不建议使用！
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = 'XXX'
APP_SECRET = 'XXXX'

def connect():
    qArray = ["待输入的文字1"]

    data = {}
    data['from'] = 'zh-CHS'
    data['to'] = 'en'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(''.join(qArray)) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = qArray
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"
    response = do_request(data)
    contentType = response.headers['Content-Type']
    print(contentType)
    print(response.content)


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


if __name__ == '__main__':
    connect()