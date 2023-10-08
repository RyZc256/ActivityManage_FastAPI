#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: user
# @ Time: 29/3/2023 下午2:13
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime
import json
import os
import time
import uuid
from typing import Union, Any

import pandas as pd
import requests as requests
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, FileResponse

from api.db.db import getMysql
from config import config
from db_app.models import User, StuInfo
from security.dataencry import encodeMD5
from security.token import create_access_token, check_jwt_token
from db_app import models
from db_app.crud import UserCrud, StuInfoCrud
from db_app.mysql import engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()



class loginItem(BaseModel):
    id: str
    password: str


@router.post("/login", tags=["用户登录"])
async def login(data: loginItem, db: Session = Depends(getMysql)):
    """
    用户登录接口
    :param data: loginItem实体类
    :param db: 数据库实例
    :return: 接口响应
    """

    # 傻逼需求
    if sb_command(data):
        return JSONResponse(content={'status': 'success',
                                     'detail': {'token': create_access_token(10000)},
                                     'datetime': str(datetime.datetime.now())
                                     })

    # 检索用户id是否存在
    user = UserCrud.login(db, user_id=data.id)
    if user:
        if user.password == encodeMD5(data.password):
            # 判断是否绑定微信
            if user.openid is None:
                return JSONResponse(content={'status': 'success',
                                             'msg': 'please timely binding wechat',
                                             'datetime': str(datetime.datetime.now())})
            return JSONResponse(content={'status': 'error',
                                         'msg': 'please use wechat to login',
                                         'datetime': str(datetime.datetime.now())})  # 限制微信登录
    # 默认返回，账号密码有误
    return JSONResponse(content={'status': 'error',
                                 'msg': 'wrong account number or password',
                                 'datetime': str(datetime.datetime.now())})  # 账号密码有误


@router.get("/login/wx", tags=["微信登录"])
async def wechatLogin(code: str, db: Session = Depends(getMysql)):
    result = wechatLoginApi(code)
    if 'openid' in result:
        user = UserCrud.wxLogin(db, open_id=result['openid'])
    else:
        result['datetime'] = str(datetime.datetime.now())
        return JSONResponse(content=result)
    # 判断openid用户是否存在
    if user:
        # 登录token 只存放了user.id
        return JSONResponse(content={'status': 'success',
                                     'detail': {'token': create_access_token(user.id), 'id': user.id,
                                                'role': user.role},
                                     'datetime': str(datetime.datetime.now())
                                     })
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': '该微信未绑定',
                                     'datetime': str(datetime.datetime.now())})


def wechatLoginApi(code):
    """
    微信登录API
    参见：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
    :param code: JS_Code
    :return: 微信服务器返回结果
    """
    conf = config.getYaml()
    host = conf['wechat']['login_host']
    appid = conf['wechat']['appid']
    secret = conf['wechat']['secret']
    url = f"{host}?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
    header = {'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/111.0.0.0 Safari/537.36'}
    wechat_api = json.loads(requests.get(url=url, headers=header).text)
    print(wechat_api)
    if 'errcode' in wechat_api:
        # 无效 JS_Code
        if wechat_api['errcode'] == 40029:
            return {'status': 'error',
                    'msg': 'code invalid'}
        # API 调用太频繁
        elif wechat_api['errcode'] == 45011:
            return {'status': 'error',
                    'msg': 'api minute-quota reach limit mustslower retry next minute'}
        # 高风险等级用户
        elif wechat_api['errcode'] == 40226:
            return {'status': 'error',
                    'msg': 'code blocked'}
        # 系统繁忙
        elif wechat_api['errcode'] == -1:
            return {'status': 'error',
                    'msg': 'system error'}
    return wechat_api


class bindWechatItem(BaseModel):
    id: str
    password: str
    code: str


@router.post("/bind/wx", tags=["微信绑定"])
async def bindWechat(data: bindWechatItem, db: Session = Depends(getMysql)):
    """
    用户微信绑定
    :param data: bindWechatItem实体类
    :param db: 数据库实例
    :return: 接口响应
    """
    # 请求用户表
    user = UserCrud.getUser(db, user_id=data.id)
    print(encodeMD5(data.password) + '\n')
    # 判断用户账号密码是否匹配
    print('user_id', user.id)
    print('user_id', data.id)
    print("password", user.password)
    print('password1', encodeMD5(data.password))
    if str(user.id) == str(data.id) and str(user.password) == str(encodeMD5(data.password)):
        openid = wechatLoginApi(data.code)
        if 'openid' in openid:
            if UserCrud.userBandWechat(db, user=user, openid=openid['openid']):
                return JSONResponse(content={'status': 'success',
                                             'datetime': str(datetime.datetime.now())})
        else:
            return JSONResponse(content={'status': 'error',
                                         'msg': 'wechat id error',
                                         'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'wrong id or password',
                                     'datetime': str(datetime.datetime.now())})


@router.get("/unbind/wx", tags=["解除微信绑定"])
async def unbindWechat(id: str, db: Session = Depends(getMysql)):
    """
    解除用户微信绑定
    :param id: 用户id
    :param db: 数据库实例
    :return: 接口响应
    """
    # 请求用户表
    user = UserCrud.getUser(db, user_id=id)
    # 判断是否存在用户
    if user:
        # 执行修改
        if UserCrud.userUnbandWechat(db, user):
            return JSONResponse(content={'status': 'success',
                                         'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'uid does not exist',
                                     'datetime': str(datetime.datetime.now())})


class userItem(BaseModel):
    id: str
    password: str
    enable: int = 1
    role: str = 'stu'


@router.post('/create', tags=['新建用户'])
async def createUser(data: userItem, db: Session = Depends(getMysql),
                     token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    print(user.id)
    print(user.role)
    # 鉴定权限
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    # 构造对象
    newUser = models.User()
    newUser.id = data.id
    newUser.password = encodeMD5(data.password)
    newUser.enable = data.enable

    # 用户角色判断
    if data.role == 'tea':
        newUser.role = 'tea'
    elif data.role == 'stu':
        newUser.role = 'stu'
    elif data.role == 'admin':
        if user.role == 'tea':
            raise HTTPException(status_code=403, detail='this user has no permission')
        newUser.role = 'admin'
    # 不存在的用户角色
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'no such role',
                                     'datetime': str(datetime.datetime.now())})

    # 判断数据库是否插入成功
    if UserCrud.createUser(db, newUser):
        return JSONResponse(content={'status': 'success',
                                     'datetime': str(datetime.datetime.now())})
    # 数据库报错
    return JSONResponse(content={'status': 'error',
                                 'msg': 'create user appear error',
                                 'datetime': str(datetime.datetime.now())})


def sb_command(data):
    if data.id == 'admin' and data.password == 'admin':
        return True


@router.post('/token/update', tags=['更新Token'])
def tokenUpdate(db: Session = Depends(getMysql),
                token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    # 判断openid用户是否存在
    return JSONResponse(content={'status': 'success',
                                 'detail': {'token': create_access_token(user.id)},
                                 'datetime': str(datetime.datetime.now())})

@router.post("/createusers", tags=['创建用户'])
async def createUsers(file: UploadFile = File(...),
                      db: Session = Depends(getMysql),
                      cid: str = Form(...),
                      token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    result = [[], [], [], [], [], [], [], [], []]
    contents = await file.read()
    data = pd.read_excel(contents)
    stuList = []

    # 读取文件
    try:
        for index, row in data.iterrows():
            row_dict = row.to_dict()
            stuList.append(row_dict)
    except:
        raise Exception('File Error')

        # 循环
    for i in stuList:

        userErrorCon = None
        stuInfoErrorCon = None
        newStu = User()
        newStu.id = int(i['学号'])
        newStu.password = encodeMD5(str(i['密码']))
        newStu.openid = None
        newStu.unionid = None
        newStu.role = 'stu'
        newStu.enable = 1
        try:
            UserCrud.createUser(db, newStu)
        except IntegrityError as e:
            # 捕获IntegrityError异常
            if 'Duplicate entry' in str(e):
                userErrorCon = {'uid': i['学号'], 'error_type': '主键重复', 'error': str(e)}
            else:
                # 处理其他的IntegrityError异常
                userErrorCon = {'uid': i['学号'], 'error_type': 'IntegrityError异常', 'error': str(e)}
        except Exception as e:
            userErrorCon = {'uid': i['学号'], 'error_type': '其他异常', 'error': str(e)}

        result[0].append(i['学号'])
        result[1].append(str(i['密码']))

    for i in stuList:
        print(f"{int(i['学号'])}, {i['姓名']}, {str(i['身份证'])}, {'女' if int(str(i['身份证'])[16]) % 2 == 0 else '男'},"
              f" {int(cid)}, {str(datetime.datetime.now())}, {i['地址']}, {i['联系电话']}")
        # 学生表
        newStuInfo = StuInfo()
        newStuInfo.id = int(i['学号'])
        newStuInfo.name = i['姓名']
        newStuInfo.idcard = str(i['身份证'])
        newStuInfo.sex = '女' if int(newStuInfo.idcard[16]) % 2 == 0 else '男'
        newStuInfo._class = int(cid)
        newStuInfo.entrance_time = str(datetime.datetime.now())
        newStuInfo.address = i['地址']
        newStuInfo.tel = i['联系电话']
        try:
            StuInfoCrud.createStuInfo(db, newStuInfo)
        except IntegrityError as e:
            # 捕获IntegrityError异常
            if 'Duplicate entry' in str(e):
                stuInfoErrorCon = {'uid': i['学号'], 'error_type': '主键重复', 'error': str(e)}
            else:
                # 处理其他的IntegrityError异常
                stuInfoErrorCon = {'uid': i['学号'], 'error_type': 'IntegrityError异常', 'error': str(e)}
        except Exception as e:
            stuInfoErrorCon = {'uid': i['学号'], 'error_type': '其他异常', 'error': str(e)}

        result[2].append(i['姓名'])
        result[3].append(i['身份证'])
        result[4].append(i['地址'])
        result[5].append(i['联系电话'])
        result[6].append(userErrorCon) if userErrorCon is not None else result[6].append("Success")
        print('RESULT[6]: ' + str(userErrorCon))
        result[7].append(stuInfoErrorCon) if stuInfoErrorCon is not None else result[7].append("Success")
        print('RESULT[7]: ' + str(stuInfoErrorCon))

    df1 = pd.DataFrame(
        {'学号': result[0],
         '姓名': result[2],
         '身份证': result[3],
         '地址': result[4],
         '联系方式': result[5],
         'User': result[6],
         'StuInfo': result[7]})
    df1 = df1.set_index('学号')
    path = os.path.join(config.getYaml()['path']['excel_root_path'], str(uuid.uuid1()) + ".xlsx")
    df1.to_excel(path)  # 将数据框转为Excel并保存
    headers = {'Content-Disposition': 'attachment; filename=' + str(datetime.datetime.now()) + "_" + str(
        datetime.datetime.now()) + '.xlsx"'}
    return FileResponse(path, headers=headers)

