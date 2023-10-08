#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: activity_manage
# @ Time: 29/3/2023 下午2:15
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime
import uuid

import pandas as pd

from typing import Union, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, FileResponse

from api.db.db import getMysql
from config import config
from db_app import models
from db_app.crud import UserCrud, ActivityCrud, ActivityRecordCrud, StuInfoCrud
from db_app.crud.ActivityRecordCrud import getActivityRecordByActivityId
from db_app.models import Activity

from security.token import check_jwt_token

router = APIRouter()


class activityItem(BaseModel):
    id: str
    introduce: str
    detail: str
    start_time: str
    end_time: str
    localtion: str
    numbers: int = 0
    visible: int = 1
    open_time: str
    teacher: str = None
    student: str = None
    poster: str = None


@router.post("/publish", tags=["发布活动"])
def publishActivity(data: activityItem, db: Session = Depends(getMysql),
                    token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')

    # 构造
    activity = Activity()
    activity.introduce = data.introduce
    activity.detail = data.detail
    activity.start_time = data.start_time
    activity.end_time = data.end_time
    activity.location = data.localtion
    activity.numbers = data.numbers
    activity.visible = data.visible
    activity.open_time = data.open_time
    activity.poster = data.poster
    if data.teacher is None:
        activity.teachear = user.id
    else:
        activity.teachear = data.teacher
    if data.student is None or data.student == "":
        activity.student = None
    else:
        activity.student = data.student
    if ActivityCrud.addActivity(db, activity):
        return JSONResponse(content={'status': 'success',
                                     'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'publish activity error',
                                     'datetime': str(datetime.datetime.now())})


@router.post("/edit", tags=["编辑活动"])
def editActivity(data: activityItem, db: Session = Depends(getMysql),
                token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    activity = ActivityCrud.getActivitybyId(db, int(data.id))
    activity.introduce = data.introduce
    activity.detail = data.detail
    activity.start_time = data.start_time
    activity.end_time = data.end_time
    activity.location = data.localtion
    activity.numbers = data.numbers
    activity.visible = data.visible
    activity.open_time = data.open_time
    activity.poster = data.poster
    if ActivityCrud.editActivity(db, activity):
        return JSONResponse(content={'status': 'success',
                                     'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': 'edit activity error',
                                     'datetime': str(datetime.datetime.now())})


@router.get("/getActivity", tags=["获取活动"])
def getActivity(id: str, db: Session = Depends(getMysql), token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    activity = ActivityCrud.getActivitybyId(db, id).to_json()
    print(activity)
    return JSONResponse(content={'status': 'success',
                                 'detail': activity,
                                 'datetime': str(datetime.datetime.now())})


@router.post("/del", tags=["删除活动"])
def delActivity(id: str, db: Session = Depends(getMysql), token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    activityItem = ActivityCrud.getActivitybyId(db, id=id)
    result = ActivityCrud.deleteActivity(db, activity=activityItem)
    return JSONResponse(content={'status': 'success',
                                 'datetime': str(datetime.datetime.now())})


@router.get("/getYearMonth", tags=["获取活动年份日期"])
def getYearMonth(db: Session = Depends(getMysql), token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    activityItem = ActivityCrud.getActivityAll(db)
    years = []
    for item in activityItem:
        startTime = str(item.start_time)
        temp = {'text': startTime[0:4], "value": startTime[0:4], "children": []}
        for i in range(1, 13):
            temp['children'].append({'text': i, 'value': str(startTime[0:4]) + "-" + str(i)})
        if temp not in years:
            years.append(temp)
    return JSONResponse(content={'status': 'success',
                                 'detail': years,
                                 'datetime': str(datetime.datetime.now())})


@router.get("/getActivityByDate", tags=["按时间获取活动"])
def getActivityByDate(year: str, month: str, db: Session = Depends(getMysql),
                      token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    activityItem = ActivityCrud.getActivityByDate(db, int(year), int(month))
    result = []
    for item in activityItem:
        result.append(item.to_json())
    return JSONResponse(content={'status': 'success',
                                 'detail': result,
                                 'datetime': str(datetime.datetime.now())})


@router.get("/getActivityRecord", tags=["导出活动记录"])
def exportRecord(id: str, db: Session = Depends(getMysql),
                      token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, token_data['uid'])
    if user.role == 'stu':
        raise HTTPException(status_code=403, detail='this user has no permission')
    recordList = ActivityRecordCrud.getActivityRecordByActivityId(db=db, id=id)
    studentList = []
    for item in recordList:
        studentList.append(StuInfoCrud.getStuInfo(db=db, user_id=item.user))
    file = createEXCEL(recordList=recordList, stuInfo=studentList)
    activity = ActivityCrud.getActivitybyId(db=db, id=id)
    headers = {'Content-Disposition': 'attachment; filename=' + str(activity.id) + "_" + str(datetime.datetime.now()) +'.xlsx"'}
    return FileResponse(file, headers=headers)


def createEXCEL(recordList, stuInfo):
    df = pd.DataFrame()
    excel_root_path = config.getYaml()['path']['excel_root_path']
    path = excel_root_path + str(uuid.uuid1()) + ".xlsx"
    df.to_excel(path)
    nameList = []
    idList = []
    classList = []
    application_time = []
    signStatus = []
    for item in stuInfo:
        nameList.append(item.name)
        idList.append(item.id)
        classList.append(item.clas.college1.name + " / " + item.clas.name)
    for item in recordList:
        application_time.append(item.application_time)
        signStatus.append("未签到" if item.status == 0 else "已签到")
    df1 = pd.DataFrame({'学号': idList, '班级': classList, '姓名': nameList , '报名时间': application_time, "签到状态": signStatus })
    df1 = df1.set_index('学号')
    df1.to_excel(path)  # 将数据框转为Excel并保存
    return path

