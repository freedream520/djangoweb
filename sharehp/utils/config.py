# -*- coding: utf-8 -*-
import yaml

# if config file not exist, it will raise exception
# FIXME
with open('sharehp/config/config.yaml', 'r') as f:
    _config = yaml.load(f)

if not _config:
    raise Exception("加载配置内容失败!")

def get_config(key, default=None):
    return _config.get(key, default)


