#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: db
# @ Time: 5/4/2023 下午2:24
# @ Author: hz157
# @ Github: https://github.com/hz157
from db_app.mysql import SessionLocal
from db_app.redisdb import redisConnect


# from db_app.redisdb import redis_conn


def getMysql():
    # 我们需要每个请求有一个独立的数据库会话/连接（SessionLocal），
    # 在所有请求中使用相同的会话，然后在请求完成后关闭它。
    db = SessionLocal()
    # 我们的依赖项将创建一个新的 SQLAlchemy SessionLocal，
    # 它将在单个请求中使用，然后在请求完成后关闭它。
    try:
        yield db
    finally:
        db.close()


def getRedis():
    db = redisConnect()
    return db