#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: database
# @ Time: 29/3/2023 下午2:46
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import config

HOST = config.getYaml()['mysql']['host']
USERNAME = config.getYaml()['mysql']['username']
PASSWORD = config.getYaml()['mysql']['password']
PORT = int(config.getYaml()['mysql']['port'])
DATABASE = config.getYaml()['mysql']['database']

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8'
# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)

# SQLAlchemy中，CRUD是通过会话进行管理的，所以需要先创建会话，
# 每一个SessionLocal实例就是一个数据库session
# flush指发送到数据库语句到数据库，但数据库不一定执行写入磁盘
# commit是指提交事务，将变更保存到数据库文件中
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基本映射类
Base = declarative_base()


