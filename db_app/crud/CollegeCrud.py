#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: CollegeCrud
# @ Time: 30/3/2023 下午6:53
# @ Author: hz157
# @ Github: https://github.com/hz157
from sqlalchemy.orm import Session

from db_app.models import Clas, College


# 获取所有学院
def getAllCollege(db: Session):
    return db.query(College).all()

# 获取所有学院
def getCollegeById(db: Session, college_id: str):
    return db.query(College).filter(College.id == college_id).first()