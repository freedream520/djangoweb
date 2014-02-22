# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from models import Spide_Resource
from models import Resource
from datetime import datetime
from utils import image
from utils import prettydate
import exceptions
import json
import math
import cache


#==========================================================
# 后台系统 TODO 剥离
#==========================================================

# 分页显示待审核的资源
def classify(request):
    page_size = 10
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    # status == 'process' 待审核
    rl = Spide_Resource.objects.filter(status='process').order_by('-gmt_create')[offset: offset + page_size]
    res_count = Spide_Resource.objects.filter(status='process').count()
    pages = int(math.ceil(res_count / (page_size * 1.0)))

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

    context = RequestContext(request, {'resList': res_list, 'curPage': page, 'pages': pages})
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
def process(request, result):
    if result == 'reject':
        res_id = request.POST.get('resid')
        Spide_Resource.objects.filter(id=res_id).update(status='reject')
    else:
        res_id = request.POST.get('resid')
        Spide_Resource.objects.filter(id=res_id).update(status='pass')
        r = Spide_Resource.objects.get(id=res_id)

        type = r.type
        title = r.title
        content = json.loads(r.content)

        normal_name = content['normal_name']
        normal_path = content['normal_path']
        thumbnail_name = content['thumbnail_name']
        thumbnail_path = content['thumbnail_path']
        url = content.get('url', '') # only video resource has this property

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
            user_id=2, # FIXME
            title=title,
            type=type,
            thumbnail=thumbnail,
            content=content,
            good=0,
            bad=0,
            comments=0,
            status='enabled'
        )
        resource.save()
        cache.set_last_resource_id(resource.id)


    # upload
    return HttpResponseRedirect('/bops/tag/')


def _get_page(request):
    p = request.GET.get('page', 1)
    try:
        page = int(p)
    except exceptions.ValueError:
        page = 1
    if not page or page <= 0:
        page = 1
    return page