#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: activity
# @ Time: 29/3/2023 下午2:18
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Union, Any

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.db.db import getMysql
from db_app.crud import UserCrud, ActivityCrud, ActivityRecordCrud
from db_app.models import ActivityRecord
from security.token import check_jwt_token

router = APIRouter()


@router.get("/today", tags=['获取今日活动'])
def todayActivity(db: Session = Depends(getMysql),
                  token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    activityList = ActivityCrud.getTodayActivityList(db, now=str(datetime.datetime.now()),
                                                     today=datetime.datetime.today().strftime("%Y-%m-%d") + "00:00:00")
    result = []
    for item in activityList:
        temp = item.to_json()
        if temp['detail'] is None or len(temp['detail']) < 100:
            temp['simplify_detail'] = ''
        else:
            temp['simplify_detail'] = temp['detail'][0:80] + '......'
        result.append(temp)
    print(result)
    return JSONResponse(content={'status': 'success',
                                 'detail': result,
                                 'datetime': str(datetime.datetime.now())})


@router.get("/exist", tags=["存活活动"])
def existActivity(db: Session = Depends(getMysql)):
    result = []
    current, page, activity = ActivityCrud.getExistActivity(db,
                                                 now=str(datetime.datetime.now()))
    for i in activity:
        result.append(i.to_json())
    return JSONResponse(content={'status': 'SUCCESS',
                                 'detail': {
                                     'page': page,
                                     'current': current,
                                     'data': result,
                                 },
                                 'datetime': str(datetime.datetime.now())})

@router.get("/join", tags=["参加活动"])
def joinActivity(id:str, db: Session = Depends(getMysql),
                 token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role != 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    activity = ActivityCrud.getActivitybyId(db, id)
    if activity is None:
        return JSONResponse(content={'status': 'error',
                                     'msg': '没有该活动',
                                     'datetime': str(datetime.datetime.now())})
    activityRecode = ActivityRecordCrud.getActivityRecordByUserAcitivity(db, uid=user.id, aid=id)
    if activityRecode is not None:
        return JSONResponse(content={'status': 'error',
                                     'msg': '您已参加',
                                     'datetime': str(datetime.datetime.now())})
    activityRecord = ActivityRecord()
    activityRecord.user = user.id
    activityRecord.activity = id
    activityRecord.application_time = str(datetime.datetime.now())
    activityRecord.status = 0
    if ActivityRecordCrud.addActivityRecord(db, activityRecord) is not None:
        return JSONResponse(content={'status': 'success',
                                     'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': '参加失败',
                                     'datetime': str(datetime.datetime.now())})