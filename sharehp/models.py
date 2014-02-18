# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class User(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    email = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    avatar = models.CharField(max_length=1024) # jsonstr
    status = models.CharField(max_length=32)


class Resource(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    user_id = models.IntegerField()
    title = models.CharField(max_length=10240)
    type = models.CharField(max_length=32)
    nums = models.IntegerField() # Deprecated
    thumbnail = models.CharField(max_length=255)
    content = models.CharField(max_length=10240)
    good = models.IntegerField()
    bad = models.IntegerField()
    comments = models.IntegerField()
    status = models.CharField(max_length=32)


class Resource_Comment(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    res_id = models.IntegerField()
    user_id = models.IntegerField()
    content = models.CharField(max_length=10240)
    have_reply = models.CharField(max_length=1)
    status = models.CharField(max_length=32)


class Group(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    group_name = models.CharField(max_length=256)
    group_desc = models.CharField(max_length=512)
    # status = models.CharField(max_length=16)


class Group_Topic(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    group_id = models.IntegerField()
    user_id = models.IntegerField()
    topic_name = models.CharField(max_length=256)
    content = models.CharField(max_length=10240)  # not used
    comments = models.IntegerField()
    status = models.CharField(max_length=16)


class Topic_Comment(models.Model):
    gmt_create = models.DateTimeField()
    gmt_modify = models.DateTimeField()
    user_id = models.IntegerField()
    topic_id = models.IntegerField()
    content = models.CharField(max_length=10240)
    status = models.CharField(max_length=16)


#  爬取资源
class Spide_Resource(models.Model):
    gmt_create = models.DateTimeField()
    title = models.CharField(max_length=1024)
    type = models.CharField(max_length=32)
    content = models.CharField(max_length=1024)
    origin =  models.CharField(max_length=1024)
    md5 = models.CharField(max_length=256)
    status = models.CharField(max_length=32)

