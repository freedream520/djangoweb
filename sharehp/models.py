# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class User(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    email = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    avatar = models.CharField(max_length=1024)  # jsonstr
    status = models.CharField(max_length=32)


class Resource(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    user_id = models.IntegerField()
    # 资源标题
    title = models.CharField(max_length=10240)
    type = models.CharField(max_length=32)
    # 资源缩略图 {'url': ..., 'size': ...}
    thumbnail = models.CharField(max_length=255)
    # 资源内容 {'url': ..., 'size': ...}
    content = models.CharField(max_length=10240)
    up = models.IntegerField()
    down = models.IntegerField()
    comments = models.IntegerField()
    status = models.CharField(max_length=32)


class Resource_Comment(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    res_id = models.IntegerField()
    user_id = models.IntegerField()
    # 评论内容 plain text
    content = models.CharField(max_length=10240)
    have_reply = models.CharField(max_length=1)
    status = models.CharField(max_length=32)


class Group(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    group_name = models.CharField(max_length=256)
    group_desc = models.CharField(max_length=512)
    avatar = models.CharField(max_length=1024)  # jsonstr
    # status = models.CharField(max_length=16)


class Group_Topic(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    group_id = models.IntegerField()
    user_id = models.IntegerField()
    topic_name = models.CharField(max_length=256)
    comments = models.IntegerField()
    status = models.CharField(max_length=16)


class Topic_Comment(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    user_id = models.IntegerField()
    topic_id = models.IntegerField()
    # 话题内容
    content = models.CharField(max_length=10240)
    # 附件
    # {'attachment': {'type': ...,
    #                'size': ...,
    #                'url':...,
    #                'exist': ...},
    attachment = models.CharField(max_length=1024)
    status = models.CharField(max_length=16)


#  爬取资源
class Spide_Resource(models.Model):
    gmt_create = models.DateTimeField()
    title = models.CharField(max_length=1024)
    type = models.CharField(max_length=32)
    # 资源内容
    # {
    #   'thumbnail_path': ..., 缩略图路径
    #   'normal_path': ...,  原始图片路径(video unused)
    #   'url': ... 视频swf(image unused)
    # }
    content = models.CharField(max_length=1024)
    # 爬取资源的原始url
    origin = models.CharField(max_length=1024)
    # 原始url的md5值（防止重复爬取）
    md5 = models.CharField(max_length=256)
    status = models.CharField(max_length=32)

