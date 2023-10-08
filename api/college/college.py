#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: test_main.http
# @ File: college
# @ Time: 18/4/2023 下午4:50
# @ Author: hz157
# @ Github: https://github.com/hz157
import datetime
import json
from typing import Union, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.db.db import getMysql
from config import config
from security.token import check_jwt_token
from db_app import models
from db_app.crud import UserCrud, StuInfoCrud, ClassCrud, CollegeCrud
from db_app.mysql import engine
from db_app.models import Clas

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get('/class/get', tags=['获取管理班级'])
def getClass(id: str=None, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    # 判断是否是学生用户
    if user.role == 'stu':
        userInfo = StuInfoCrud.getStuInfo(db, user_id=id)
        clas = ClassCrud.getClass(db,clas_id=userInfo._class)
        return JSONResponse(content={'status': 'success',
                                     'detail': clas.to_json(),
                                     'datetime': str(datetime.datetime.now())})
    elif user.role == 'tea':
        classList = ClassCrud.getClassByTeacher(db, user.id)
        result = []
        for item in classList:
            result.append(item.to_json())
        return JSONResponse(content={'status': 'success',
                                     'detail': result,
                                     'datetime': str(datetime.datetime.now())})


@router.get('/get', tags=['获取学院'])
def getCollege(id: str = None, year: str = None, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    if id:
        college = CollegeCrud.getCollegeById(db, college_id=id)
        if year:
            classList = ClassCrud.getClassByCollegeAndYear(db, college=college.id, year=year)
        else:
            classList = ClassCrud.getClassByCollege(db, college=college.id)
        result = []
        # 序列化对象
        for item in classList:
            result.append(item.to_json())
    else:
        result = []
        if user:
            collegeList = CollegeCrud.getAllCollege(db)
            for item in collegeList:
                result.append(item.to_json())

    if result:
        return JSONResponse(content={'status': 'success',
                                     'detail': result,
                                     'datetime': str(datetime.datetime.now())})
    else:
        return JSONResponse(content={'status': 'error',
                                     'msg': "No Data",
                                     'datetime': str(datetime.datetime.now())})


@router.get('/getYear', tags=['获取学院班级年份'])
def getCollegeYear(id: str, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    years = []
    yearList = ClassCrud.getClassByCollege(db, college=id)
    for i in yearList:
        if str(i.year) not in years:
            years.append(str(i.year))
    return JSONResponse(content={'status': 'success',
                                 'detail': years,
                                 'datetime': str(datetime.datetime.now())})


@router.get('/getStudent', tags=['获取班级学生'])
def getStudent(id: str, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    result = []
    if user.role == 'stu':
        userInfo = StuInfoCrud.getStuInfo(db, user_id=user.id)
        if userInfo._class == id:
            classStus = StuInfoCrud.getStuByClass(db, class_id=id)
        else:
            raise HTTPException(status_code=403, detail='this user has no permission')
    else:
        classStus = StuInfoCrud.getStuByClass(db, class_id=id)
    for item in classStus:
        temp = item.to_json()
        temp['idcard'] = temp['idcard'][0:3] + '*************' + temp['idcard'][15:17]
        result.append(temp)
    return JSONResponse(content={'status': 'success',
                                 'detail': result,
                                 'datetime': str(datetime.datetime.now())})

class classItem(BaseModel):
    college_id: str
    class_name: str


@router.post('/add', tags=['添加班级'])
def getStudent(classItem: classItem, db: Session = Depends(getMysql),
             token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    user = UserCrud.getUser(db, user_id=token_data['uid'])
    result = None
    if user.role == 'admin' or user.role == 'tea':
        # 构建对象
        clas = Clas()
        clas.name = classItem.class_name
        clas.college = classItem.college_id
        clas.year = str(datetime.datetime.now().strftime("%Y"))
        clas_refresh = ClassCrud.addClass(db, clas)
        if clas_refresh:
            result = {'status': 'success','detail': clas_refresh.to_json(),'datetime': str(datetime.datetime.now())}
        else:
            result = {'status': 'error','msg': 'add error','datetime': str(datetime.datetime.now())}
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=403, detail='this user has no permission')



