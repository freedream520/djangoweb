# -*- coding: utf-8 -*-
from django import template
from  ..utils import config


def static_url(resource):
    return config.get_config('QINIU_STATIC_CDN') + resource

register = template.Library()
register.filter('static_url', static_url)
