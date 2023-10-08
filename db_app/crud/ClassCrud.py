#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: ClassCrud
# @ Time: 30/3/2023 下午7:19
# @ Author: hz157
# @ Github: https://github.com/hz157
from sqlalchemy import and_, distinct
from sqlalchemy.orm import Session

from db_app.models import Clas


# 获取班级信息
def getClass(db: Session, clas_id: str):
    return db.query(Clas).filter(Clas.id == clas_id).first()

# 获取教师管理的班级
def getClassByTeacher(db: Session, teacher: str):
    return db.query(Clas).filter(Clas.teacher == teacher).all()

# 获取学院下属班级
def getClassByCollege(db: Session, college: str):
    return db.query(Clas).filter(Clas.college == college).all()

# 获取学院下属班级
def getClassByCollegeAndYear(db: Session, college: str, year: str):
    return db.query(Clas).filter(and_(Clas.college == college, Clas.year == year)).all()

# 获取学院班级
def getCollegeYear(db: Session, college: str):
    return db.query(Clas).filter(Clas.college == college).all()

# 添加班级
def addClass(db: Session, clas: Clas):
    db.add(clas)
    db.commit()
    db.refresh(clas)
    return clas