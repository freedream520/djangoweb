# -*- coding: utf-8 -*-
from models import User
from models import Group_Topic
from models import Group
from utils import config
from exception import IllegalArgumentError
import redis
import json

# 获取redis配置
_redis_server_ip = config.get_config('REDIS_SERVER_IP', )
_redis_server_port = config.get_config('REDIS_SERVER_PORT', )

if not _redis_server_ip or not _redis_server_port:
    raise IllegalArgumentError("redis config is invalid!")

# redis实例
_redisIns = redis.StrictRedis(host=_redis_server_ip, port=_redis_server_port, db=0)


def _get(key):
    return _redisIns.get(key)  # if key not exist, return None


def _set(key, value):
    return _redisIns.set(key, value)


def _del(key):
    return _redisIns.delete(key)


def _set_timeout(key, value, timeout):
    ret = _redisIns.set(key, value)
    _redisIns.expire(key, timeout)
    return ret


# hash type
def _hmset(key, mapping):
    return _redisIns.hmset(key, mapping)


def _hmset_timeout(key, mapping, timeout):
    ret = _redisIns.hmset(key, mapping)
    _redisIns.expire(key, timeout)
    return ret


# if key not exist, return empty dict {}
def _hgetall(key):
    return _redisIns.hgetall(key)


# if key not exist, return empty list []
def _lrange(key, start, end):
    return _redisIns.lrange(key, start, end)


# 设置用户登录session
def set_login_session(id, data):
    if not id:
        raise IllegalArgumentError("session_id can't be None!")

    key = 'login-session:' + str(id)
    return _hmset(key, data)


# 获取用户登录session
def get_login_session(id):
    if not id:
        raise IllegalArgumentError("session_id can't be None!")

    key = 'login-session:' + str(id)
    return _hgetall(key)


# 删除用户登录session
def del_login_session(id):
    if not id:
        return
    key = 'login-session:' + str(id)
    return _del(key)


# 获取用户信息
# 返回值: user_info(dict)|{}
def get_user_info(user_id):
    if not user_id:
        raise IllegalArgumentError("user_id can't be None!")

    key = 'user:' + str(user_id)
    user_info = _hgetall(key)
    if not user_info:
        try:
            user = User.objects.get(id=user_id)
            user_info = {
                'id': user.id,
                'nickname': user.nickname,
                'avatar': user.avatar  # jsonstr
            }
            _hmset(key, user_info)
        except User.DoesNotExist, e:
            # TODO log error
            user_info = {}
    return user_info


# 获取用户nickname
# 返回值: nickname(string)|''
def get_user_nickname(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        # TODO log error
        return ''
    else:
        return user_info.get('nickname', '')


# 获取用户头像
# 返回值: avatar(dict)|{}
def get_user_avatar(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        # TODO log error
        return {}
    else:
        avatar_info = user_info.get('avatar', None)
        if not avatar_info:
            return {}
        else:
            return json.loads(avatar_info)


# 获取用户的昵称和头像信息(naa -> nickname and avatar)
def get_user_naa(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        return '', {}
    else:
        avatar_info = user_info.get('avatar', None)
        if not avatar_info:
            return user_info.get('nickname', ''), {}
        else:
            return user_info.get('nickname', ''), json.loads(avatar_info)


# 获取小组列表信息
def get_group_list():
    key = 'group-list'
    group_list = _lrange(key, 0, -1)  # all group
    if not group_list:
        group_list = []
        groups = Group.objects.all()
        for group in groups:
            g = {
                'id': group.id,
                'create_date': group.gmt_create.strftime('%Y-%m-%d'),
                'group_name': group.group_name,
                'group_desc': group.group_desc
            }
            group_list.append(g)
    return group_list


# 获取某个小组信息
# 缓存字段： create_date, group_name, group_desc
def get_group_info(group_id):
    if not group_id:
        raise IllegalArgumentError("group_id can't be None!")

    key = 'group:' + str(group_id)
    group_info = _hgetall(key)
    if not group_info:
        try:
            group = Group.objects.get(id=group_id)
            group_info = {
                'id': group.id,
                'create_date': group.gmt_create.strftime('%Y-%m-%d'),
                'group_name': group.group_name,
                'group_desc': group.group_desc
            }
            _hmset(key, group_info)
        except Group.DoesNotExist, e:
            # TODO log eror
            group_info = {}
    return group_info


# 获取话题信息
# 缓存字段： topic_name, group_id
def get_topic_info(topic_id):
    if not topic_id:
        raise IllegalArgumentError("topic_id can't be None!")

    key = 'topic:' + str(topic_id)
    topic_info = _hgetall(key)
    if not topic_info:
        try:
            topic = Group_Topic.objects.get(id=topic_id)
            topic_info = {
                'id': topic.id,
                'topic_name': topic.topic_name,
                'group_id': topic.group_id
            }
            _hmset(key, topic_info)
        except Group_Topic.DoesNotExist, e:
            # TODO log eror
            topic_info = {}
    return topic_info


# 获取小组信息
def get_group_info_by_topicid(topic_id):
    topic_info = get_topic_info(topic_id)
    return get_group_info(topic_info['group_id'])


# 获取最新资源id
def get_last_resource_id():
    key = 'last-resource-id'
    return _get(key)


# FIXME
def set_last_resource_id(res_id):
    if not res_id:
        raise IllegalArgumentError("res_id can't be None!")
    if int(res_id) <= 0:
        pass  # TODO throw exception
    key = 'last-resource-id'
    return _set(key, res_id)


def set_tmp_video_info(id, value, timeout):
    if not id or not value or timeout < 0:
        pass  # TODO throw exception
    key = 'video-info:' + id
    return _hmset_timeout(key, value, timeout)


def get_tmp_video_info(id):
    if not id:
        pass  # TODO throw exception
    key = 'video-info:' + id
    return _hgetall(key)
