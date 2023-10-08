#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: file_upload
# @ Time: 29/3/2023 下午2:18
# @ Author: ryan.zhang
# @ Github: https://github.com/hz157
import datetime
import os
import uuid
from typing import Union, Any

from fastapi import APIRouter, UploadFile, File, Depends
from starlette.responses import JSONResponse


from config import config
from security.token import check_jwt_token

router = APIRouter()


@router.post('/image', tags=['上传图片'])
async def uploadImage(file: UploadFile = File(...), token_data: Union[str, Any] = Depends(check_jwt_token)) -> Any:
    filename = str(uuid.uuid1()) + '.jpg'
    image_root_path = config.getYaml()['path']['image_root_path']
    if not os.path.exists(image_root_path):
        os.mkdir(image_root_path)
    save_file = os.path.join(image_root_path, filename)
    f = open(save_file, 'wb')
    data = await file.read()
    f.write(data)
    f.close()
    return JSONResponse(content={'status': 'success',
                                 'detail': {
                                     'path': filename
                                 },
                                 'datetime': str(datetime.datetime.now())})


