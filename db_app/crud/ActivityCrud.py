#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: ActivityCurd
# @ Time: 30/3/2023 下午6:54
# @ Author: hz157
# @ Github: https://github.com/hz157
import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import schemas
from dateutil.relativedelta import relativedelta


from db_app.models import Activity


# 发布活动
def addActivity(db: Session, activity: Activity):
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


# 获取活动信息
def getActivitybyId(db: Session, id):
    activity = db.query(Activity).filter(Activity.id == id).first()
    return activity


# 获取活动信息
def getActivityAll(db: Session):
    activity = db.query(Activity).filter().all()
    return activity


def getTodayActivityList(db: Session, now, today):
    activity = db.query(Activity).filter(and_(Activity.start_time >= now, Activity.start_time < today, Activity.end_time > now)).all()
    return activity

def getExistActivity(db: Session, now, skip: int = 1, limit: int = 100):
    count = db.query(Activity).filter(and_(Activity.start_time >= now, Activity.end_time > now)).count()
    page = int(count / limit) + 1
    return skip, page, db.query(Activity).filter(and_(Activity.start_time >= now, Activity.end_time > now)).offset(skip-1).limit(limit).all()


# 编辑活动
def editActivity(db: Session, activity: Activity):
    db.add(activity)
    db.commit()
    db.flush(activity)
    return activity

# 删除活动
def deleteActivity(db: Session, activity: Activity=None, id: str=None):
    if Activity is None:
        activity = db.query(Activity).filter(Activity.id == id).first()
    db.delete(activity)
    db.commit()
    db.flush(activity)
    return activity

def getActivityByDate(db: Session, year: str, month: str=None):
    if month is None:
        date_start = datetime.datetime(year=year, month=1, day=1)
        date_end = date_start + relativedelta(years=+1)
        activity = db.query(Activity).filter(and_(Activity.start_time > str(date_start), Activity.start_time < str(date_end))).all()
    else:
        date_start = datetime.datetime(year=year, month=month, day=1)
        date_end = date_start + relativedelta(months=+1)
        relativedelta(months=+1)
        activity = db.query(Activity).filter(
            and_(Activity.start_time > str(date_start), Activity.start_time < str(date_end))).all()
    return activity
