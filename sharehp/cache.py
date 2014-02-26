# -*- coding: utf-8 -*-
from models import User
from models import Group_Topic
from models import Group
from utils import config
from utils import common
from exception import IllegalArgumentError
import redis
import json
import logging

# 获取redis配置
_redis_server_ip = config.get_config('REDIS_SERVER_IP', )
_redis_server_port = config.get_config('REDIS_SERVER_PORT', )

if not _redis_server_ip or not _redis_server_port:
    raise IllegalArgumentError("redis config is invalid!")

# redis实例
_redisIns = redis.StrictRedis(host=_redis_server_ip, port=_redis_server_port, db=0)

logger = logging.getLogger('sharehp')


def _get(key):
    return _redisIns.get(key)  # if key not exist, return None


def _set(key, value, timeout=-1):
    ret = _redisIns.set(key, value)
    if timeout and timeout > 0:
        _redisIns.expire(key, timeout)
    return ret


# hash type
def _hmset(key, mapping, timeout=-1):
    ret = _redisIns.hmset(key, mapping)
    if timeout and timeout > 0:
        _redisIns.expire(key, timeout)
    return ret


# if key not exist, return empty dict {}
def _hgetall(key):
    return _redisIns.hgetall(key)


# set type
def _sadd(key, values, timeout=-1):
    ret = _redisIns.sadd(key, values)
    if timeout and timeout > 0:
        _redisIns.expire(key, timeout)
    return ret


def _sismember(key, value):
    return _redisIns.sismember(key, value)


# list type
def _lpush(key, values, timeout=-1):
    ret = _redisIns.lpush(key, values)
    if timeout and timeout > 0:
        _redisIns.expire(key, timeout)
    return ret


# if key not exist, return empty list []
def _lrange(key, start, end):
    return _redisIns.lrange(key, start, end)


def _del(key):
    return _redisIns.delete(key)


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
    if id:
        return _del('login-session:' + str(id))


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
            logger.error('Fail to find user by id: ' + str(user_id))
            user_info = {}
    return user_info


def del_user_info(user_id):
    if user_id:
        return _del('user:' + str(user_id))


# 获取用户nickname
# 返回值: nickname(string)|''
def get_user_nickname(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        logger.error('Fail to get user_info by id: ' + str(user_id))
        return ''
    else:
        return user_info.get('nickname', '')


# 获取用户头像
# 返回值: avatar(dict)|{}
def get_user_avatar(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        logger.error('Fail to get user_info by id: ' + str(user_id))
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
    # get all data
    group_list = _lrange(key, 0, -1)

    if not group_list:
        groups = Group.objects.all()
        for group in groups:
            avatar = json.loads(group.avatar)
            g = {
                'id': group.id,
                'create_date': group.gmt_create.strftime('%Y-%m-%d'),
                'group_name': group.group_name,
                'group_desc': _relength(group.group_desc, 13),
                'group_ori_desc': group.group_desc,
                'big_avatar': avatar['big'],
                'mid_avatar': avatar['mid'],
            }
            group_list.append(g)
            _lpush(key, json.dumps(g))
    else:
        for i, group in enumerate(group_list):
            group_list[i] = json.loads(group)  # jsonstr => dict

    return group_list


def _relength(str, length):
    retval = str
    if str and len(str) > length:  #  TODO 优化
        retval = str[:length] + '...'
    return retval


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
                'group_desc': group.group_desc,
                'avatar': group.avatar
            }
            _hmset(key, group_info)
        except Group.DoesNotExist, e:
            # TODO log eror
            group_info = {}

    if group_info:
        group_info['avatar'] = json.loads(group_info['avatar'])
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


# 设置最新的资源ID
def set_last_resource_id(res_id):
    key = 'last-resource-id'
    if not res_id or common.safe_int(res_id, 0):  # FIXME
        _del(key)
    return _set(key, res_id, 5 * 60)  # cache 5min


# 保存视频信息(defautl cache 1h)
def set_video_info(id, value, timeout=3600):
    if not id or not value or timeout < 0:
        raise IllegalArgumentError("video params illegal!")
    key = 'video-info:' + id
    return _hmset(key, value, timeout)


# 获取视频信息
def get_video_info(id):
    if not id:
        raise IllegalArgumentError("video id can't be None!")
    key = 'video-info:' + str(id)
    return _hgetall(key)


# 检测资源是否被赞/鄙过
def has_resource_voted(res_id, user_id):
    if not res_id or not user_id:
        raise IllegalArgumentError("res_id or user_id can't be None!")
    key = 'vote:' + str(res_id)
    return _sismember(key, user_id)


# 对资源进行赞/鄙,返回值True表示操作成功
def resource_vote(res_id, user_id, action):
    if action not in ('up', 'down'):
        raise IllegalArgumentError("action param is illegal!")
    if not user_id or not res_id:
        raise IllegalArgumentError("user_id or res_id can't be None!")

    if has_resource_voted(res_id, user_id):
        return False
    else:
        # TODO redis 事务接口
        return _sadd('vote:' + str(res_id), user_id) and _sadd('vote_' + str(action) + ':' + str(res_id), user_id)


# user_id can be None!!!
def resource_vote_type(res_id, user_id):
    if not res_id:
        raise IllegalArgumentError("res_id can't be None!")
    if not user_id or not has_resource_voted(res_id, user_id):
        return None

    vote_up_key = 'vote_up:' + str(res_id)
    if _sismember(vote_up_key, user_id):
        return 'up'
    else:
        return 'down'







