#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: ActivityManagement
# @ File: config
# @ Time: 29/3/2023 下午8:34
# @ Author: hz157
# @ Github: https://github.com/hz157
import yaml

from utils.logger import logger

CONFIG_PATH = 'config/config.yml'


def getYaml():
    """
    获取YAML文件内容
    :return: YAML文件内容
    """
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    return result


def setYaml(key: str, value: str, title: str = None):
    """
    YAML 配置文件写入
    :param key: 键
    :param value: 值
    :param title: 标题
    :return: 设置结果
    """
    try:
        oldYaml = getYaml()  # 读取文件数据
        if title:
            oldYaml[title][key] = value
        else:
            oldYaml[key] = value
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(oldYaml, f)
        return True
    except Exception as e:
        logger.error(e)
        return False
