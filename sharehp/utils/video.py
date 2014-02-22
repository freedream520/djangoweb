# -*- coding: utf-8 -*-
from ..exception import IllegalArgumentError
import json
import re
import urllib

# 检测是否支持该视频连接
def support(video_url):
    if not video_url:
        raise IllegalArgumentError("video_url can't be None!")

    if video_url.startswith('http://www.56.com/'):
        return True
    else:
        return False

# 获取视频信息
def video_info(video_url):
    if not video_url:
        raise IllegalArgumentError("video_url can't be None!")

    # 56
    if video_url.startswith('http://www.56.com/'):
        return _56_video_info(video_url)
    else:
        pass


def _56_vid(video_url):
    match = re.search(r'.+(vid-|v_)(.+).html.*$', video_url)
    if match:
        return match.group(2)


def _56_video_info(video_url):
    video_id = _56_vid(video_url)
    video_info = {
        'success': False
    }

    if not video_id:
        pass # return defalut
    else:
        result = urllib.urlopen('http://vxml.56.com/json/%s/?src=site' % video_id).read()
        if result:
            result = json.loads(result)
            if result.get('info', None):
                video_info['success'] = True
                video_info['bimg'] = result['info']['bimg']
                video_info['img'] = result['info']['img']
                video_info['title'] = result['info']['Subject']
                video_info['swf'] = 'http://player.56.com/v_' + video_id + '.swf'
                video_info['url'] = video_url

    return video_info

