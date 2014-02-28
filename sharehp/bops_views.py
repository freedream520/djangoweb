# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from models import Spide_Resource
from models import Resource
from datetime import datetime
from utils import image
from utils import prettydate
from utils import config
import exceptions
import json
import math
import cache
import urllib


#==========================================================
# 后台系统 TODO 剥离
#==========================================================

def require_admin(view):
    def new_view(request, *args, **kwargs):
        if not request.xmanuser['login']:
            return_url = urllib.urlencode(
                {'return_url': config.get_config('SHAREHP_SERVER_HOST') + request.get_full_path()})
            return HttpResponseRedirect('/login/?' + return_url)
        else:
            if not _is_admin(request):
                return render_to_response('bops/no_privilege.htm')
            else:
                return view(request, *args, **kwargs)
    return new_view


# 显示待审核的资源
def classify(request):
    # status == 'process' 待审核
    rl = Spide_Resource.objects.filter(status='process').order_by('-id')

    res_list = []
    for r in rl:
        content = json.loads(r.content)
        res = {
            'id': r.id,
            'create-date': prettydate.convert(r.gmt_create),
            'title': r.title,
            'type': r.type,
            'content': content
        }
        res_list.append(res)

    context = RequestContext(request, {'resList': res_list})
    return render_to_response('bops/tag.htm', context)


# 资源详情
def detail(request, res_id):
    # 资源信息
    r = Spide_Resource.objects.get(id=res_id)
    content = json.loads(r.content)
    res = {
        'id': r.id,
        'title': r.title,
        'type': r.type,
        'content': content
    }
    context = RequestContext(request, {'res': res})
    return render_to_response('bops/detail.htm', context)


# 处理资源（pass or reject）
def process(request, res_id, result):
    if not _is_admin(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请使用管理员账号登陆后操作!"}))
    if not Spide_Resource.objects.filter(id=res_id).exists():
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "你操作的资源可能已经被删除!"}))
    if not Spide_Resource.objects.get(id=res_id).status == 'process':
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "该资源已经被处理过，请刷新页面!"}))

    if result == 'reject':
        Spide_Resource.objects.filter(id=res_id).update(status='reject')
    else:
        r = Spide_Resource.objects.get(id=res_id)

        type = r.type
        title = r.title
        content = json.loads(r.content)

        normal_name = content['normal_name']
        normal_path = content['normal_path']
        thumbnail_name = content['thumbnail_name']
        thumbnail_path = content['thumbnail_path']
        url = content.get('url', '')  # only video resource has this property

        if type == "image":
            thumbnail_url = 'resource/thumbnail/' + thumbnail_name
            image.qiniu_upload(thumbnail_path, thumbnail_url)

            normal_url = 'resource/normal/' + normal_name
            image.qiniu_upload(normal_path, normal_url)

            content = json.dumps({
                'size': image.get_image_size(normal_path),  # only image_used
                'url': normal_url
            })
            thumbnail = json.dumps({
                'size': image.get_image_size(thumbnail_path),
                'url': thumbnail_url
            })
        else:
            thumbnail_url = 'resource/thumbnail/' + thumbnail_name
            image.qiniu_upload(thumbnail_path, thumbnail_url)

            content = json.dumps({
                'size': '',
                'url': url
            })
            thumbnail = json.dumps({
                'size': image.get_image_size(thumbnail_path),
                'url': thumbnail_url
            })

        # 保存资源
        current_date = datetime.now()
        resource = Resource(
            gmt_create=current_date,
            gmt_modify=current_date,
            user_id=_get_current_userid(request),
            title=title,
            type=type,
            thumbnail=thumbnail,
            content=content,
            up=0,
            down=0,
            comments=0,
            status='enabled'
        )
        resource.save()
        cache.set_last_resource_id(resource.id)
        Spide_Resource.objects.filter(id=res_id).update(status='pass')

    return HttpResponse(json.dumps({'success': 0, 'data': {}}))


def _get_page(request):
    p = request.GET.get('page', 1)
    try:
        page = int(p)
    except exceptions.ValueError:
        page = 1
    if not page or page <= 0:
        page = 1
    return page


def _get_page_url(server_host, path):
    return ''.join([server_host, path, '?page='])


# 获取当前登录用户的user_id(没有登录返回None)
def _get_current_userid(request):
    if request.xmanuser['login']:
        return request.xmanuser['id']

def _is_admin(request):
    if request.xmanuser['login']:
        return 'diaocow@qq.com' == request.xmanuser['email']  # FIXME hard code
