#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: userinfo
# @ Time: 29/3/2023 下午2:13
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime
import time
from typing import Union, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.db.db import getMysql
# from security.dataencry import encodeAES
from security.token import check_jwt_token
from db_app import models
from db_app.crud import UserCrud, StuInfoCrud, TeaInfoCrud, ClassCrud, CollegeCrud
from db_app.mysql import engine
from db_app.models import StuInfo, TeaInfo

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/get", tags=["获取用户信息"])
def getInfo(id: str = None, db: Session = Depends(getMysql),
            token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])

    if id:
        selectUser = UserCrud.getUser(db, user_id=id)
        if selectUser is None:
            return JSONResponse(content={'status': 'error',
                                         'msg': 'user does not exist',
                                         'datetime': str(datetime.datetime.now())})
        if user.role == 'stu':
            # 访问非本人信息，返回401错误
            raise HTTPException(status_code=403, detail='this user has no permission')
        elif user.role == 'tea':
            # 访问教师信息
            if selectUser.role == 'tea':
                userInfo = TeaInfoCrud.getTeaInfo(db, user_id=id).to_json()
            # 访问学生信息
            elif selectUser.role == 'stu':
                userInfo = StuInfoCrud.getStuInfo(db, user_id=id)
                # 非管理班级用户，返回403权限错误
                if str(user.id) != str(userInfo.clas.teacher):
                    raise HTTPException(status_code=403, detail='this user has no permission')
                userInfo = userInfo.to_json()
        # 超级管理员
        elif user.role == 'admin':
            user = UserCrud.getUser(db, user_id=id)
            if user.role == 'tea':
                userInfo = TeaInfoCrud.getTeaInfo(db, user_id=id).to_json()
            elif user.role == 'stu':
                userInfo = StuInfoCrud.getStuInfo(db, user_id=id).to_json()
    else:
        if user.role == 'tea':
            userInfo = TeaInfoCrud.getTeaInfo(db, user_id=user.id).to_json()
        elif user.role == 'stu':
            userInfo = StuInfoCrud.getStuInfo(db, user_id=user.id).to_json()
        elif user.role == 'admin':
            userInfo = {'name': 'Super Admin', 'tel': '10000'}
    # if user.role != 'admin':
    #     userInfo['idcard'] = userInfo['idcard'][0:3] + '*************' + userInfo['idcard'][15:17]
    return JSONResponse(content={'status': 'success',
                                 'detail': idcd(userInfo),
                                 'datetime': str(datetime.datetime.now())})


class userInfoItem(BaseModel):
    id: str
    name: str
    sex: str
    clas: str = None
    idcard: str
    end_time: str
    address: str
    tel: str


@router.post("/edit", tags=["编辑用户信息"])
def editInfo(data: userInfoItem, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    # 请求用户
    user = UserCrud.getUser(db, token_data['uid'])
    # 更改资料用户
    selectUser = UserCrud.getUser(db, data.id)
    if user.id != selectUser.id:
        # 学生
        if user.role == 'stu':
            if data.id != token_data['uid']:
                # 限制访问他人数据
                raise HTTPException(status_code=403, detail='this user has no permission')
        # 教师
        elif user.role == 'tea':
            # 非教师管理的班级，禁止访问
            if selectUser.role == 'stu' and StuInfoCrud.getStuInfo(db, selectUser.id).clas.teacher != user.id:
                raise HTTPException(status_code=403, detail='this user has no permission')

    if selectUser.role == 'tea':
        # 获取用户信息
        userInfo = TeaInfoCrud.getTeaInfo(db, user_id=data.id)
    elif selectUser.role == 'stu':
        # 获取用户信息
        userInfo = StuInfoCrud.getStuInfo(db, user_id=data.id)
    else:
        raise HTTPException(status_code=403, detail='this user has no permission')

    if userInfo is not None:
        userInfo.sex = data.sex
        userInfo.address = data.address
        userInfo.tel = data.tel
    print(userInfo.to_json())
    result = []
    if selectUser.role == 'tea':
        result = TeaInfoCrud.editTeaInfo(db, userInfo)
    elif selectUser.role == 'stu':
        result = StuInfoCrud.editStuInfo(db, userInfo)
    if result:
        return JSONResponse(content={'status': 'success',
                                     'detail': idcd(result.to_json()),
                                     'datetime': str(datetime.datetime.now())})
    return JSONResponse(content={'status': 'error',
                                 'msg': 'edit appear error',
                                 'datetime': str(datetime.datetime.now())})


def idcd(info: dict):
    """
    身份证脱敏
    :param info:
    :return:
    """
    info['idcard'] = info['idcard'][0:3] + '*************' + info['idcard'][15:17]
    return info