import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.college import college
from api.activity import activity_manage, sign_in_code, activity
from api.file import file_upload, file, file_manage
from api.user import user, userinfo

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.handlers.RotatingFileHandler("logs/api.log", mode="a", maxBytes=100 * 1024, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


# 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 用户模块蓝图注册
app.include_router(user.router, prefix='/user', tags=['用户'])
app.include_router(userinfo.router, prefix='/user/info', tags=['用户信息'])

# 活动模块蓝图注册
app.include_router(activity.router, prefix='/activity', tags=['活动'])
app.include_router(activity_manage.router, prefix='/activity/manage', tags=['活动管理'])
app.include_router(sign_in_code.router, prefix='/activity/sign_in_code', tags=['签到管理'])

# 文件模块蓝图注册
app.include_router(file.router, prefix='/file', tags=['文件'])
app.include_router(file_manage.router, prefix='/file/manage', tags=['文件管理'])
app.include_router(file_upload.router, prefix='/file/upload', tags=['文件上传'])

app.include_router(college.router, prefix='/college', tags=['学院'])

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

