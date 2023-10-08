#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: ActivityRecordCurd
# @ Time: 30/3/2023 下午6:54
# @ Author: hz157
# @ Github: https://github.com/hz157
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import schemas

from db_app.models import ActivityRecord


# 获取活动记录信息
def getActivityById(db: Session, id: str):
    activityRecord = db.query(ActivityRecord).filter(ActivityRecord.id == id).all()
    return activityRecord

# 增加活动记录信息
def addActivityRecord(db: Session, activityRecord: ActivityRecord):
    db.add(activityRecord)
    db.commit()
    db.flush(activityRecord)
    return activityRecord

# 获取活动记录信息
def getActivityRecordByUserAcitivity(db: Session, uid: str, aid: str):
    activityRecord = db.query(ActivityRecord).filter(and_(ActivityRecord.user == uid, ActivityRecord.activity == aid)).first()
    return activityRecord

# 更新数据
def updateActivityRecordByUserAcitivity(db: Session, activityRecord: ActivityRecord):
    db.add(activityRecord)
    db.commit()
    db.flush(activityRecord)
    return activityRecord

def getActivityRecordByActivityId(db: Session, id: str):
    activityRecord = db.query(ActivityRecord).filter(ActivityRecord.activity == id).all()
    return activityRecord