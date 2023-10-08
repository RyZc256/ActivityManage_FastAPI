#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: dataencry
# @ Time: 30/3/2023 上午11:33
# @ Author: hz157
# @ Github: https://github.com/hz157
import base64
import hashlib
import time

# from Crypto.Cipher import AES

iv = '#qGn@JXW!VdgA9fa'
MD5SALT = ''


# 将原始的明文用空格填充到16字节
def pad(data):
    pad_data = data
    for i in range(0, 16 - len(data)):
        pad_data = pad_data + ' '
    return pad_data


# 将明文用AES加密
# def encodeAES(key, data):
#     print('key', key)
#     print('data', data)
#     # 将长度不足16字节的字符串补齐
#     if len(data) < 16:
#         data = pad(data)
#     # 创建加密对象
#     AES_obj = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
#     # 完成加密
#     AES_en_str = AES_obj.encrypt(data.encode("utf-8"))
#     # 用base64编码一下
#     AES_en_str = base64.b64encode(AES_en_str)
#     # 最后将密文转化成字符串
#     AES_en_str = AES_en_str.decode("utf-8")
#     return AES_en_str


def encodeMD5(data):
    saltValue = str(data + MD5SALT).encode()
    m = hashlib.md5(saltValue)
    return m.hexdigest()
