# -*- coding: utf-8 -*-
import redis
from models import User
from models import Group_Topic
from models import Group

# FIXME config hardcode
_redisIns = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


def _get(key):
    return _redisIns.get(key)


def _set(key, value):
    return _redisIns.set(key, value)


def _hmset(key, mapping):
    return _redisIns.hmset(key, mapping)


def _hgetall(key):
    return _redisIns.hgetall(key)


# 设置用户登录session
def set_login_session(id, data):
    key = 'login-session-' + str(id)
    return _set(key, data)


# 获取用户登录session
def get_login_session(id):
    key = 'login-session-' + str(id)
    return _get(key)


# 获取用户信息
# 缓存字段： nickname
def get_user_info(user_id):
    if not user_id:
        pass  # todo throw exception

    key = 'user-' + str(user_id)
    user_info = _hgetall(key)
    if not user_info:
        user = User.objects.get(id=user_id)
        user_info = {
            'id': user.id,
            'nickname': user.nickname
        }
        _hmset(key, user_info)

    return user_info


def get_user_nickname(user_id):
    user_info = get_user_info(user_id)
    return user_info['nickname']


# 获取话题信息
# 缓存字段： topic_name, group_id
def get_topic_info(topic_id):
    if not topic_id:
        pass  # TODO throw exception

    key = 'topic-' + str(topic_id)
    topic_info = _hgetall(key)
    if not topic_info:
        topic = Group_Topic.objects.get(id=topic_id)
        topic_info = {
            'id': topic.id,
            'topic_name': topic.topic_name,
            'group_id': topic.group_id
        }
        _hmset(key, topic_info)

    return topic_info


# 获取小组信息
# 缓存字段： gmt_create, group_name, group_desc
def get_group_info(group_id):
    if not group_id:
        pass  # TODO throw exception

    key = 'group-' + str(group_id)
    group_info = _hgetall(key)
    if not group_info:
        group = Group.objects.get(id=group_id)
        group_info = {
            'id': group.id,
            'create_date': group.gmt_create.strftime('%Y-%m-%d'),
            'group_name': group.group_name,
            'group_desc': group.group_desc
        }
        _hmset(key, group_info)

    return group_info


# 获取小组信息
def get_group_info_by_topicid(topic_id):
    topic_info = get_topic_info(topic_id)
    return get_group_info(topic_info['group_id'])

