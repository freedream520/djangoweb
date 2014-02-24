# -*- coding: utf-8 -*-
import yaml
import os

_config_path = ''.join([os.path.dirname(__file__), '/../config/config.yaml'])

# if config file not exist, it will raise exception
with open(_config_path, 'r') as f:
    _config = yaml.load(f)

if not _config:
    raise Exception("加载配置内容失败!")

def get_config(key, default=None):
    return _config.get(key, default)




