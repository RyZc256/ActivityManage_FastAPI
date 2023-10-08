#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: UserCrud
# @ Time: 30/3/2023 下午6:53
# @ Author: hz157
# @ Github: https://github.com/hz157
from sqlalchemy.orm import Session

from db_app.models import User


# 获取用户
def login(db: Session, user_id: str = None, openid: str = None):
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    else:
        return db.query(User).filter(User.openid == openid).first()


def getUser(db: Session, user_id: str = None):
    return db.query(User).filter(User.id == user_id).first()


def wxLogin(db: Session, open_id: str = None):
    return db.query(User).filter(User.openid == open_id).first()


# 新建用户
def createUser(db: Session, user: User):
    # 使用add来将该实例对象添加到您的数据库。
    # 使用commit来对数据库的事务提交（以便保存它们）。
    # db.commit()
    # 使用refresh来刷新您的数据库实例（以便它包含来自数据库的任何新数据，例如生成的 ID）。
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except:
        db.rollback()
    return user


# 用户绑定微信
def userBandWechat(db: Session, user: User, openid: str, unionid: str = None):
    user.openid = openid
    if unionid is not None:
        user.unionid = unionid
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 用户解绑定微信
def userUnbandWechat(db: Session, user: User):
    user.openid = None
    user.unionid = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
