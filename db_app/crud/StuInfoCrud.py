#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: StuInfoCrud
# @ Time: 30/3/2023 下午6:53
# @ Author: hz157
# @ Github: https://github.com/hz157

from sqlalchemy.orm import Session

from db_app.models import StuInfo


# 获取学生用户信息
def getStuInfo(db: Session, user_id: str):
    return db.query(StuInfo).filter(StuInfo.id == user_id).first()


# 编辑学生信息
def editStuInfo(db: Session, stuInfo: StuInfo):
    db.add(stuInfo)
    db.commit()
    db.refresh(stuInfo)
    return stuInfo


# 获取班级学生
def getStuByClass(db: Session, class_id: str):
    return db.query(StuInfo).filter(StuInfo._class == class_id).all()

def createStuInfo(db: Session, stuInfo: StuInfo):
    db.add(stuInfo)
    db.commit()
    db.refresh(stuInfo)
    return stuInfo