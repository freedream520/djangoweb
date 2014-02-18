# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.db.models import Max
from django.template import RequestContext
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
from models import Spide_Resource
from models import Resource
from utils import prettydate
import json
import math
import image
import exceptions


def classify(request):
    page_size = 10
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    rl = Spide_Resource.objects.filter(status='process').order_by('-gmt_create')[offset: offset + page_size]
    res_count = Spide_Resource.objects.filter(status='process').count()
    pages = int(math.ceil(res_count / (page_size * 1.0)))

    res_list = []
    for r in rl:
        content = json.loads(r.content)
        res = {
            'id': r.id,
            # 'date': prettydate.convert(r.gmt_create),
            'title': r.title,
            'type': r.type,
            'thumbnail': content['name'],
        }
        res_list.append(res)

    context = RequestContext(request, {'resList': res_list, 'curPage': page, 'pages': pages})
    return render_to_response('bops/tag.htm', context)


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
        name = content['name']
        normal_path = content['normal_path']
        thumbnail_path = content['thumbnail_path']
        url = content.get('url', '')

        if type == "image":
            thumbnail_url = 'resource/thumbnail/' + name
            image.qiniu_upload(thumbnail_path, thumbnail_url)

            normal_url = 'resource/normal/' + name
            image.qiniu_upload(normal_path, normal_url)

            content = json.dumps({
                'size': image.get_pic_size(normal_path),  # only image_used
                'url': normal_url
            })
            thumbnail = json.dumps({
                'size': image.get_pic_size(thumbnail_path),
                'url': thumbnail_url
            })
        else:
            thumbnail_url = 'resource/thumbnail/' + name
            image.qiniu_upload(thumbnail_path, thumbnail_url)

            content = json.dumps({
                'size': '',
                'url': url
            })
            thumbnail = json.dumps({
                'size': image.get_pic_size(thumbnail_path),
                'url': thumbnail_url
            })

        # 保存资源
        current_date = datetime.now()
        resource = Resource(
            gmt_create=current_date,
            gmt_modify=current_date,
            user_id=2,
            title=title,
            type=type,
            nums=1, # Depreated
            thumbnail=thumbnail,
            content=content,
            good=0,
            bad=0,
            comments=0,
            status='enabled'
        )
        resource.save()

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