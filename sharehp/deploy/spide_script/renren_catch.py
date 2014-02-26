#!/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import db
import urllib
import json
import re
import image

_GRAP_URL = 'http://zhan.renren.com/fengzimen?from=template'
_SPIDE_RESOURCE_DIR = "/home/diaocow/workspace/djangoweb/sharehp/static/sharehp/tmp/"
_IMAGE_CNT = 1
_VIDEO_CNT = 1


def _deal_resource(image_url):
    # 保存原图
    normal_image_info = image.save_img(image_url, _SPIDE_RESOURCE_DIR)
    # 保存缩略图
    thumbnail_image_info = image.thumbnail_img(normal_image_info['name'], _SPIDE_RESOURCE_DIR)
    return {
        'normal_path': normal_image_info['path'],
        'normal_name': normal_image_info['name'],
        'thumbnail_path': thumbnail_image_info['path'],
        'thumbnail_name': thumbnail_image_info['name']
    }

def _get_video_id(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)

def _get_video_info(video_id):
    return urllib.urlopen('http://vxml.56.com/json/%s/?src=site' % video_id).read()

# ============================================================
# 开始采集
# ============================================================
def main(pages):
    global  _IMAGE_CNT, _VIDEO_CNT # FIXME
    for i in range(pages):
        url = _GRAP_URL + '&page=' + str(i)
        html_doc = urllib.urlopen(url).read()
        if html_doc:
            soup = BeautifulSoup(html_doc)
            try:
                # ============================================================
                # 采集视频
                # ============================================================
                target_divs = soup.find_all('article', {'class': 'post-video'})
                if target_divs and len(target_divs):
                    for td in target_divs:
                        # 资源标题
                        title = td.find('h2')['title']
                        # 获取视频信息
                        video_src = td.find('embed')['src'].strip()
                        video_id = _get_video_id('http://player.56.com/renrenshare_(.*).swf/1030_.*.swf', video_src)
                        video_img = json.loads(_get_video_info(video_id))['info']['bimg']
                        # 不抓取重复资源
                        if db.exists(video_src):
                            continue

                        resource_info = _deal_resource(video_img)
                        resource_info['url'] = video_src
                        resource = db.SpideResource(title, 'video', json.dumps(resource_info), video_src)
                        db.save(resource)
                        print '成功爬取视频资源!'
                        _VIDEO_CNT = _VIDEO_CNT + 1

            except Exception, err:
                print '[VideoError] ' + str(err)

            try:
                # ============================================================
                # 采集图片
                # ============================================================
                target_divs = soup.find_all('article', {'class': ['post-photo', 'post-article']})
                if target_divs and len(target_divs):
                    for td in target_divs:
                        post_content = td.find('div', {'class': 'post-content'})
                        # 资源标题
                        title = post_content.find('h2')['title']
                        images = post_content.find_all('img')
                        # 抓取只有一副图片的资源
                        if images and len(images) == 1:
                            image = images[0]
                            if image.get('data-src', None):
                                image_src = image['data-src'].strip()
                            else:
                                image_src = image['src'].strip()
                            # 不抓取重复资源
                            if db.exists(image_src):
                                continue

                            resource_info = _deal_resource(image_src)
                            resource = db.SpideResource(title, 'image', json.dumps(resource_info), image_src)
                            db.save(resource)
                            print '成功爬取图片资源!'
                            _IMAGE_CNT = _IMAGE_CNT + 1

            except Exception, err:
                print '[ImageError] ' + str(err)
        else:
            print '[Error] No data for dealing ...'
    else:
        print '爬取资源结束，共抓取图片资源%d个， 视频资源%d个...!' %(_IMAGE_CNT, _VIDEO_CNT)




main(1)
