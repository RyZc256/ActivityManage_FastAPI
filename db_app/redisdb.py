import redis

from config import config

HOST = config.getYaml()['redis']['host']
PASSWORD = config.getYaml()['redis']['password']
PORT = int(config.getYaml()['redis']['port'])
DATABASE = int(config.getYaml()['redis']['database'])


def redisConnect():
    redis_pool = redis.ConnectionPool(host=HOST, port=PORT, password=PASSWORD, db=DATABASE)
    redis_conn = redis.Redis(connection_pool=redis_pool)
    return redis_conn


