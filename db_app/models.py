#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: models
# @ Time: 29/3/2023 下午2:46
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
from sqlalchemy import Column, DateTime, ForeignKey, String, text, Date
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, VARCHAR, LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Activity(Base):
    __tablename__ = 'activity'

    id = Column(BIGINT(20), primary_key=True)
    introduce = Column(VARCHAR(255), nullable=False, comment='介绍')
    detail = Column(LONGTEXT, comment='细节')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    location = Column(VARCHAR(255), comment='位置')
    numbers = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='人数')
    visible = Column(INTEGER(1), nullable=False, server_default=text("'1'"), comment='可见状态')
    open_time = Column(DateTime, nullable=False, comment='开放时间')
    teachear = Column(BIGINT(20), nullable=False, comment='负责人')
    student = Column(BIGINT(20), comment='负责用户')
    poster = Column(VARCHAR(255), comment='宣传图')

    def to_json(self):
        return {
            'id': self.id,
            'introduce': self.introduce,
            'detail': self.detail,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'location': self.location,
            'numbers': self.numbers,
            'visible': self.visible,
            'open_time': str(self.open_time),
            'teachear': self.teachear,
            'student': self.student,
            'poster': self.poster
        }


class College(Base):
    __tablename__ = 'college'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(VARCHAR(255), comment='学院名称')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class User(Base):
    __tablename__ = 'user'

    id = Column(BIGINT(20), primary_key=True, index=True)
    password = Column(VARCHAR(255), nullable=False, comment='密码')
    openid = Column(VARCHAR(255), comment='用户唯一标识')
    unionid = Column(VARCHAR(255), comment='用户在开放平台的唯一标识符')
    enable = Column(INTEGER(1), server_default=text("'1'"), comment='启用状态')
    role = Column(VARCHAR(255), comment='用户角色')

    def to_json(self):
        return {
            'id': self.id,
            'password': self.password,
            'openid': self.openid,
            'unionid': self.unionid,
            'enable': self.enable,
            'role': self.role
        }


class TeaInfo(User):
    __tablename__ = 'tea_info'

    id = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    name = Column(VARCHAR(255), comment='姓名')
    sex = Column(VARCHAR(255), comment='性别')
    idcard = Column(VARCHAR(255), comment='身份证')
    entrance_time = Column(Date, comment='加入时间')
    address = Column(VARCHAR(255), comment='住址')
    tel = Column(VARCHAR(255), comment='联系电话')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sex': self.sex,
            'idcard': self.idcard,
            'entrance_time': str(self.entrance_time),
            'address': self.address,
            'tel': self.tel
        }


class StuInfo(User):
    __tablename__ = 'stu_info'

    id = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    name = Column(VARCHAR(255), comment='姓名')
    sex = Column(VARCHAR(255), comment='性别')
    idcard = Column(VARCHAR(255), nullable=False, comment='身份证')
    _class = Column('class', ForeignKey('class.id', ondelete='CASCADE', onupdate='CASCADE'), index=True, comment='班级')
    entrance_time = Column(Date, comment='入学时间')
    address = Column(VARCHAR(255), comment='住址')
    tel = Column(VARCHAR(255), comment='电话')

    clas = relationship('Clas')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sex': self.sex,
            'idcard': self.idcard,
            'class': {
                    'id': self.clas.id,
                    'college': {
                        'id': self.clas.college1.id,
                        'name': self.clas.college1.name,
                    },
                    'year': self.clas.year,
                    'name': self.clas.name,
                    'teacher': self.clas.teacher
                },
            'entrance_time': str(self.entrance_time),
            'address': self.address,
            'tel': self.tel
        }


class ActivityRecord(Base):
    __tablename__ = 'activity_record'

    id = Column(BIGINT(20), primary_key=True)
    activity = Column(ForeignKey('activity.id', ondelete='CASCADE', onupdate='CASCADE'), index=True, comment='活动编号')
    user = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), index=True, comment='用户编号')
    application_time = Column(DateTime, comment='申请时间')
    status = Column(INTEGER(1), comment='状态')

    activity1 = relationship('Activity')
    user1 = relationship('User')

    def to_json(self):
        return {
            'id': self.id,
            'activity': self.activity,
            'user': self.user,
            'idcard': self.idcard,
            'application_time': self.application_time,
            'status': self.status
        }


class Clas(Base):
    __tablename__ = 'class'

    id = Column(BIGINT(20), primary_key=True)
    college = Column(ForeignKey('college.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = Column(VARCHAR(255), nullable=False)
    year = Column(VARCHAR(255), nullable=False)
    teacher = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)

    college1 = relationship('College')
    user = relationship('User')

    def to_json(self):
        return {
            'id': self.id,
            'college': {
                'id': self.college1.id,
                'name': self.college1.name,
            },
            'year': self.year,
            'name': self.name,
            'teacher': self.teacher
        }


class FileTask(Base):
    __tablename__ = 'file_task'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(VARCHAR(255), comment='文件收集任务名')
    type = Column(VARCHAR(255), nullable=False, comment='文件格式')
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='截止时间')
    teacher = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    user = relationship('User')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'teacher': self.teacher,
        }



class FileUploadRecord(Base):
    __tablename__ = 'file_upload_record'

    id = Column(BIGINT(20), primary_key=True)
    file_task = Column(ForeignKey('file_task.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                       index=True, comment='文件任务编号')
    path = Column(VARCHAR(255), nullable=False, comment='路径')
    user = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                  index=True, comment='上传路径')
    upload_time = Column(DateTime, nullable=False, comment='上传时间')

    file_task1 = relationship('FileTask')
    user1 = relationship('User')

    def to_json(self):
        return {
            'id': self.id,
            'file_task': self.file_task,
            'path': self.path,
            'user': self.user,
            'upload_time': self.upload_time
        }
