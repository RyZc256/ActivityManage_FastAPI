#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: TeaInfoCrud
# @ Time: 30/3/2023 下午6:53
# @ Author: hz157
# @ Github: https://github.com/hz157
from sqlalchemy.orm import Session

from db_app.models import TeaInfo


# 获取教师用户信息
def getTeaInfo(db: Session, user_id: str):
    return db.query(TeaInfo).filter(TeaInfo.id == user_id).first()


# 编辑用户资料
def editTeaInfo(db: Session, teaInfo: TeaInfo):
    db.add(teaInfo)
    db.commit()
    db.refresh(teaInfo)
    return teaInfo
