#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: file
# @ Time: 29/3/2023 下午2:33
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime
import os
from typing import Union, Any

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse, FileResponse

from config import config
from security.token import check_jwt_token

router = APIRouter()


@router.get("/image", tags=['显示图片'])
async def returnImage(filename: str):
    image_root_path = config.getYaml()['path']['image_root_path']
    filepath = os.path.join(image_root_path, filename)
    file_like = open(filepath, mode="rb")
    return StreamingResponse(file_like, media_type="image/jpg")

@router.get("/downloadStuTemplate", tags=['下载学生名单模板'])
async def downloadStuTemplate():
    excel_root_path = config.getYaml()['path']['excel_root_path']
    headers = {'Content-Disposition': 'attachment; filename=' + str(datetime.datetime.now()) +'.xlsx"'}
    return FileResponse(os.path.join(excel_root_path, 'StuInfoTemplate.xlsx'), headers=headers)
