# -*- coding: utf-8 -*-
from django import template
from  ..utils import config
from django.utils.safestring import mark_safe


def white_space(str):
    if str:
        str = mark_safe(str.replace(' ', '&nbsp;'))
    return str

def static_url(resource):
    return config.get_config('QINIU_STATIC_CDN') + resource

def tmp_server_url(resource):
    return config.get_config('SHAREHP_SERVER_TMP_DIR') + resource


register = template.Library()
register.filter('white_space', white_space)
register.filter('static_url', static_url)
register.filter('tmp_server_url', tmp_server_url)
