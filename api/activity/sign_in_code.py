#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: sign_in_code
# @ Time: 29/3/2023 下午2:17
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import base64
import datetime
import time

from io import BytesIO

import qrcode

from fastapi import APIRouter, Depends, HTTPException
from typing import Union, Any

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, StreamingResponse, FileResponse

from api.db.db import getMysql, getRedis
from security.token import check_jwt_token
from db_app.crud import UserCrud, ActivityCrud, ActivityRecordCrud
from db_app.models import Activity

router = APIRouter()


@router.get("/get", tags=["获取签到码"])
def getCode(id: str = None, db: Session = Depends(getMysql),
                    token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    if id is None:
        raise HTTPException(status_code=401, detail='param error')
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    activity = ActivityCrud.getActivitybyId(db, id)
    if activity is None:
        return JSONResponse(content={'status': 'error',
                                     'msg': '活动不存在',
                                     'datetime': str(datetime.datetime.now())})
    # 判断是否是管理用户
    if activity.teachear != user.id:
        raise HTTPException(status_code=403, detail='this user has no permission')
    redis = getRedis()
    signInCode = redis.get(id)
    if signInCode is None:
        signInCode = createCode(activity.id)
        redis.set(signInCode, id, ex=10)
    qrcodeImage = qrcode.make(signInCode)
    # 将图片数据保存到BytesIO对象中
    buffer = BytesIO()
    qrcodeImage.save(buffer, format="PNG")
    # 将BytesIO对象中的数据作为流返回
    buffer.seek(0)
    redis.close()
    return StreamingResponse(buffer, media_type="image/png")
    # return StreamingResponse(qrcode.make(createCode), media_type="image/jpg")


def createCode(activityId):
    now = time.mktime(datetime.datetime.now().timetuple())
    now_byte = bytes(str(now), encoding='utf-8')
    splitChat = '|'
    splitChat_byte = bytes(splitChat, encoding='utf-8')
    activityId_byte = bytes(str(activityId), encoding='utf-8')
    key = bytes(str("H6eIITcK26J&04cf=6QT^A%kd&?b#you2ku-eZX1c4j_^P8^K^79LE+Q#q@XMzIAFx~4v!kEG_C4UUXqbcZ#u9F&Vt&?Fk!y05ARwXqn0vvjLEcyfCOfw^K7M3uEzm?I"), encoding='utf-8')
    deCode = base64.b64encode(base64.b32encode(now_byte + splitChat_byte + activityId_byte + key))
    return str(deCode, encoding='utf-8')



@router.get("/verify", tags=["验证签到码"])
def verifyCode(code: str, db: Session = Depends(getMysql),
                    token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'admin' or user.role == 'tea':
        return JSONResponse(content={'status': 'error',
                                     'msg': '该账号无需签到',
                                     'datetime': str(datetime.datetime.now())})
    else:
        # 解码
        redis = getRedis()
        # 检索redis数据
        id = int(redis.get(code))
        redis.close()
        # 有值的情况
        if id is not None:
            # 匹配
            activityRecord = ActivityRecordCrud.getActivityRecordByUserAcitivity(db, uid=user.id, aid=id)
            activityRecord.status = 1
            if ActivityRecordCrud.updateActivityRecordByUserAcitivity(db, activityRecord) is not None:
                return JSONResponse(content={'status': 'success',
                                             'datetime': str(datetime.datetime.now())})
            return JSONResponse(content={'status': 'error',
                                         'msg': "签到失败",
                                         'datetime': str(datetime.datetime.now())})
        return JSONResponse(content={'status': 'error',
                                     'msg': "签到码错误",
                                     'datetime': str(datetime.datetime.now())})