# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.template import RequestContext
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
from exception import QiniuUploadFileError
from models import Resource
from models import User
from models import Resource_Comment
from models import Group
from models import Group_Topic
from models import Topic_Comment
from utils import image
from utils import video
from utils import prettydate
from utils import common
from utils import config
import json
import math
import urllib
import os
import forms
import cache

# 分类页面
def classify(request, tag):
    page_size = 10
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    rl = Resource.objects.filter(type=tag, status='enabled')[offset: offset + page_size]
    res_count = Resource.objects.filter(type=tag, status='enabled').count()
    pages = int(math.ceil(res_count / (page_size * 1.0)))

    res_list = []
    for r in rl:
        res = {
            'id': r.id,
            'create_date': prettydate.convert(r.gmt_create),
            'user_id': r.user_id,
            'nickname': cache.get_user_nickname(r.user_id),
            'avatar': cache.get_user_avatar(r.user_id),
            'title': r.title,
            'type': r.type,
            'thumbnail': json.loads(r.thumbnail),  # json
            'comments': r.comments
        }
        res_list.append(res)
    # side bar
    group_list = cache.get_group_list()

    context = RequestContext(request, {'tag': tag,
                                       'resList': res_list,
                                       'groups': group_list,
                                       'curPage': page,
                                       'pages': pages})
    return render_to_response('tag.htm', context)


# 首页: 获取最新发布的20个资源
def index(request):
    rl = Resource.objects.filter(status='enabled').order_by('-gmt_create')[0:20]
    # 分发资源到瀑布中
    resListArray = [[], [], [], []]
    for i, r in enumerate(rl):
        res = {
            'id': r.id,
            'create_date': prettydate.convert(r.gmt_create),
            'user_id': r.user_id,
            'nickname': cache.get_user_nickname(r.user_id),
            'title': r.title,
            'type': r.type,
            'thumbnail': json.loads(r.thumbnail),
            'comments': r.comments
        }
        # 标题过长
        if len(res['title']) > 36:  #  TODO 优化
            res['title'] = res['title'][:36] + '...'
        resListArray[i % 4].append(res)

    context = RequestContext(request, {'resListArray': resListArray})
    return render_to_response('index.htm', context)


# 资源详情页面
def detail(request, tag, res_id):
    try:
        r = Resource.objects.get(id=res_id, status='enabled')
    except Resource.DoesNotExist:
        return render_to_response('miss/resource.htm', RequestContext(request))

    # 资源信息
    res = {
        'id': r.id,
        'create_date': r.gmt_create.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': r.user_id,
        'nickname': cache.get_user_nickname(r.user_id),
        'avatar': cache.get_user_avatar(r.user_id),
        'title': r.title,
        'type': r.type,
        'content': json.loads(r.content),
        'comments': r.comments
    }
    # 评论信息
    comment_list = []
    cl = Resource_Comment.objects.filter(res_id=res_id, status='enabled')
    for comment in cl:
        comment_list.append({
            'comment_id': comment.id,
            'create_date': prettydate.convert(comment.gmt_create),
            'user_id': comment.user_id,
            'nickname': cache.get_user_nickname(comment.user_id),
            'avatar': cache.get_user_avatar(comment.user_id),
            'content': comment.content})

    # 上一个/下一个
    prev = not _first_resource_id(res_id)
    next = not _last_resource_id(res_id)

    context = RequestContext(request, {
        'res': res,
        'commentList': comment_list,
        'next': next,
        'prev': prev,
        'groups': cache.get_group_list()})
    return render_to_response('detail.htm', context)


# 下一个/上一个资源
def another(request, tag, res_id, order):
    if order == 'next':
        rl = Resource.objects.filter(id__gt=res_id)[:1]
    else:
        rl = Resource.objects.filter(id__lt=res_id).order_by('-id')[:1]

    if len(rl) > 0:
        return detail(request, tag, rl[0].id)
    else:
        return render_to_response('miss/resource.htm', RequestContext(request))


# 发表新资源(require_login)
def new_resource(request):
    return render_to_response('new_resources.htm', RequestContext(request))


# 群组列表页面
def groups(request):
    groups = Group.objects.all()
    for group in groups:
        group_desc = group.group_desc
        # 群组描述过长
        if group_desc and len(group_desc) > 13:  #  TODO 优化
            group.group_desc = group_desc[:13] + '...'

    context = RequestContext(request, {'groups': groups})
    return render_to_response('groups.htm', context)


# 群组页面(帖子列表)
def group(request, group_id, order):
    is_exist = Group.objects.filter(id=group_id).exists()
    if not is_exist:
        return render_to_response('miss/group.htm', RequestContext(request))

    # 每页显示10条
    page_size = 10
    page = _get_page(request)
    offset = (int(page) - 1) * page_size
    # 排序
    if order == 'hot':
        # FIXME 最热排序逻辑
        gts = []
    else:
        gts = Group_Topic.objects.filter(group_id=group_id, status='enabled').order_by('-gmt_create')[
              offset: offset + page_size]
    topics = []
    for t in gts:
        topic = {
            'id': t.id,
            'topic_name': t.topic_name,
            'user_id': t.user_id,
            'nickname': cache.get_user_nickname(t.user_id),
            'avatar': cache.get_user_avatar(t.user_id),
            'comments': t.comments,
            'publish_date': prettydate.convert(t.gmt_create),
            'last_comment_date': prettydate.convert(t.gmt_modify)
        }
        topics.append(topic)
    group = cache.get_group_info(group_id)
    topic_count = Group_Topic.objects.filter(group_id=group_id, status='enabled').count()
    pages = int(math.ceil(topic_count / (page_size * 1.0)))

    context = RequestContext(request, {'group': group, 'topics': topics, 'curPage': page, 'pages': pages})
    return render_to_response('group.htm', context)


# 帖子页面
def group_topic(request, topic_id):
    is_exist = Group_Topic.objects.filter(id=topic_id).exists()
    if not is_exist:
        return render_to_response('miss/topic.htm', RequestContext(request))

    # 每页显示20楼
    page_size = 20
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    comment_count = Topic_Comment.objects.filter(topic_id=topic_id).count()
    pages = int(math.ceil(comment_count / (page_size * 1.0)))

    tcs = Topic_Comment.objects.filter(topic_id=topic_id)[offset: offset + page_size]
    topic_comments = []
    for floor, tc in enumerate(tcs):
        content = json.loads(tc.content)
        topic_comment = {
            'floor': floor + 1,
            'create_date': tc.gmt_create.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': tc.user_id,
            'nickname': cache.get_user_nickname(tc.user_id),
            'avatar': cache.get_user_avatar(tc.user_id),
            'text': content['text'],
            'attachment': content['attachment'],
        }
        topic_comments.append(topic_comment)
    topic = cache.get_topic_info(topic_id)
    group = cache.get_group_info_by_topicid(topic['id'])

    context = RequestContext(request, {'group': group,
                                       'topic': topic,
                                       'topicComments': topic_comments,
                                       'curPage': page,
                                       'pages': pages})
    return render_to_response('group_topic.htm', context)


# 发布新帖(require_login)
def new_topic(request, group_id):
    group = cache.get_group_info(group_id)
    context = RequestContext(request, {'group': group})
    return render_to_response('new_topic.htm', context)


# 注册会员
def register(request):
    if request.method == 'POST':
        # 提交表单
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            register_date = datetime.now()
            default_avatar =  {
                'big': 'user/avater/default.big',
                'mid': 'user/avater/default.mid',
                'small': 'user/avater/default.small'
            }
            # 保存用户信息
            user = User(
                gmt_create=register_date,
                gmt_modify=register_date,
                email=form.cleaned_data['email'].strip(),
                nickname=form.cleaned_data['nickname'].strip(),
                password=common.encode_password(form.cleaned_data['password'].strip()),  # encode passowrd
                avatar=json.dumps(default_avatar),
                status='enabled')
            user.save()
            # 写登录session
            session_id = _do_login(user.email)
            return_url = _get_return_url(request)
            response = HttpResponseRedirect(return_url)
            response.set_cookie('id', session_id)
            return response
        else:
            return render_to_response('register.htm', {'form': form})

    else:
        # 渲染页面
        return_url = urllib.urlencode({'return_url': _get_return_url(request)})
        register_action_url = '/register/?' + return_url
        return render_to_response('register.htm', {'register_action_url': register_action_url})


# 登录
def login(request):
    if request.method == 'POST':
        # 提交表单
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            # 写登录session
            session_id = _do_login(form.cleaned_data['email'].strip())
            return_url = _get_return_url(request)
            response = HttpResponseRedirect(return_url)
            response.set_cookie('id', session_id)
            return response
        else:
            return render_to_response('login.htm', {'form': form})
    else:
        # 渲染页面
        return_url = urllib.urlencode({'return_url': _get_return_url(request)})
        login_action_url = '/login/?' + return_url
        return render_to_response('login.htm', {'login_action_url': login_action_url})


# login包装器
def require_login(view):
    def new_view(request, *args, **kwargs):
        if not request.xmanuser['login']:
            return_url = urllib.urlencode(
                {'return_url': config.get_config('SHAREHP_SERVER_HOST') + request.get_full_path()})  #FIXME
            return HttpResponseRedirect('/login/?' + return_url)
        else:
            return view(request, *args, **kwargs)

    return new_view


# 登出
def loginout(request):
    # del session
    session_id = request.COOKIES.get('id')
    if session_id:
        cache.del_login_session(session_id)

    return_url = _get_return_url(request)
    response = HttpResponseRedirect(return_url)
    # del cookie
    response.set_cookie('id', '', 0)
    return response


# 修改密码(require)
def change_password(request):
    if request.method == "POST":
        # 提交表单
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            user_id = _get_current_userid(request)
            password = common.encode_password(form.cleaned_data['password'].strip())
            old_password = User.objects.get(id=user_id).password
            if password != old_password:
                # 密码错误
                form._errors["password"] = ErrorList([u"密码不正确!"])
                context = RequestContext(request, {'form': form})
                return render_to_response('change_password.htm', context)
            else:
                # 修改密码成功
                new_password = common.encode_password(form.cleaned_data['new_password'].strip())
                User.objects.filter(id=user_id).update(gmt_modify=datetime.now(), password=new_password)
                context = RequestContext(request, {'success': True})
                return render_to_response('change_password.htm', context)
        else:
            context = RequestContext(request, {'form': form})
            return render_to_response('change_password.htm', context)
    else:
        # 渲染页面
        context = RequestContext(request)
        return render_to_response('change_password.htm', context)


# 修改头像
def change_avatar(request):
    if request.method == "POST":
        attach_name = request.POST.get('attach', '').strip()
        crop_x = request.POST.get('crop_x')
        crop_y = request.POST.get('crop_y')
        crop_width = request.POST.get('crop_width')
        crop_height = request.POST.get('crop_height')

        if not _check_login(request):
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
        if not default_storage.exists(os.path.join(config.get_config('SHAREHP_UPLOAD_DIR'), attach_name)):
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "图片丢失，请重新上传!"}))

        crop_result = image.crop_user_avatar(config.get_config('SHAREHP_UPLOAD_DIR'), attach_name,
                                             (int(crop_x),
                                              int(crop_y),
                                              int(crop_x) + int(crop_width),
                                              int(crop_y) + int(crop_height)))
        try:
            avatar_big_url = 'user/avater/' + crop_result['big']['name']
            image.qiniu_upload(crop_result['big']['path'], avatar_big_url)
            avatar_mid_url = 'user/avater/' + crop_result['mid']['name']
            image.qiniu_upload(crop_result['mid']['path'], avatar_mid_url)
            avatar_small_url = 'user/avater/' + crop_result['small']['name']
            image.qiniu_upload(crop_result['small']['path'], avatar_small_url)
        except QiniuUploadFileError: # FIXME
            # TODO Log error
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "服务器异常，请稍后再试!"}))

        avatar_info = {
            'big': avatar_big_url,
            'mid': avatar_mid_url,
            'small': avatar_small_url
        }
        User.objects.filter(id=_get_current_userid(request)).update(gmt_modify=datetime.now(),
                                                                    avatar=json.dumps(avatar_info))
        cache.del_user_info(_get_current_userid(request)) # important!

        return HttpResponse(json.dumps({'success': 0, 'data': {'src': avatar_big_url}}))

    else:
        avatar = json.loads(User.objects.get(id=_get_current_userid(request)).avatar)
        context = RequestContext(request, {'avatar': avatar})
        return render_to_response('change_avatar.htm', context)


#-------------------------------------------
# API 接口, 供前端JS调用
# 调用成功： {'success': 0, 'data': {...}}
# 调用失败： {'success': -1, error_msg: {...}}
#-------------------------------------------

def _deal_image_resource(image_name):
    attach_info = {
        'name': image_name,
        'path': settings.MEDIA_ROOT + image_name,
        'size': image.get_pic_size(settings.MEDIA_ROOT + image_name)
    }
    # 生成缩略图图&上传
    thumbnail_info = image.thumbnail_img(attach_info['name'], settings.MEDIA_ROOT)
    thumbnail_url = 'resource/thumbnail/' + thumbnail_info['name']
    image.qiniu_upload(thumbnail_info['path'], thumbnail_url)

    # 上传原图
    attach_url = 'resource/normal/' + attach_info['name']
    image.qiniu_upload(attach_info['path'], attach_url)

    content = json.dumps({
        'size': attach_info['size'],  # only image_used
        'url': attach_url
    })
    thumbnail = json.dumps({
        'size': thumbnail_info['size'],
        'url': thumbnail_url
    })
    return (thumbnail, content)


def _deal_video_resource(video_info):
    img_info = image.save_img(video_info['img'], settings.MEDIA_ROOT)
    attach_info = {
        'name': img_info['name'],
        'path': img_info['path'],
        'size': img_info['size']
    }
    # 生成缩略图图&上传
    thumbnail_info = image.thumbnail_img(attach_info['name'], settings.MEDIA_ROOT)
    thumbnail_url = '/resource/thumbnail/' + thumbnail_info['name']
    image.qiniu_upload(thumbnail_info['path'], thumbnail_url)

    content = json.dumps({
        'size': '',  #  vidoe not used
        'url': video_info['url']
    })
    thumbnail = json.dumps({
        'size': thumbnail_info['size'],
        'url': thumbnail_url
    })
    return (thumbnail, content)


# FIXME
def add_new_resource(request):
    title = request.POST.get('title', '').strip()
    type = request.POST.get('type')
    attach = request.POST.get('attach', '').strip()

    # check params
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if len(title) <= 0:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "资源内容不能为空!"}))
    if type not in ('image', 'video'):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "资源类型不支持!"}))
    if len(attach) <= 0:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "资源无效!"}))

    if type == 'image' and not default_storage.exists(settings.MEDIA_ROOT + attach):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "图片丢失，请重新上传!"}))
    if type == 'video':
        video_info = cache.get_tmp_video_info(attach)
        if not video_info:
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "视频丢失，请重新上传!"}))

    # build filed data
    if type == 'image':
        thumbnail, content = _deal_image_resource(attach)
    else:
        thumbnail, content = _deal_video_resource(video_info)

    # 保存资源
    current_date = datetime.now()
    resource = Resource(
        gmt_create=current_date,
        gmt_modify=current_date,
        user_id=_get_current_userid(request),
        title=title,
        type=type,
        nums=1,  # Depreated
        thumbnail=thumbnail,
        content=content,
        good=0,
        bad=0,
        comments=0,
        status='enabled'
    )
    resource.save()
    return HttpResponse(json.dumps({'success': 0, 'error_msg': ""}))


# 对资源进行评论
def add_resource_comment(request, res_id):
    content = request.POST.get('content', '').strip()
    # check params
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not Resource.objects.filter(id=res_id, status='enabled').exists():
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "你评论的资源已经被删除，请刷新页面!"}))
    if not content:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "评论内容不能为空!"}))
    if len(content) >= 10240:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "评论内容过长，只能10240个字符!"}))

    # 插入资源评论 FIXME transcation
    current_time = datetime.now()
    comment = Resource_Comment(
        gmt_create=current_time,
        gmt_modify=current_time,
        res_id=res_id,
        user_id=_get_current_userid(request),
        content=content,
        status='enabled')
    comment.save()
    # 资源评论数递增1
    comments = Resource.objects.get(id=res_id, status='enabled').comments
    Resource.objects.filter(id=res_id, status='enabled').update(comments=comments + 1, gmt_modify=current_time)
    return HttpResponse(json.dumps({'success': 0, 'data': {}}))


# 发表新话题
def add_new_topic(request, group_id):
    # 获取发帖的标题&内容
    topic_title = request.POST.get('title', '').strip()
    topic_content = request.POST.get('content', '').strip()
    # 获取attachment(可选)
    has_attach = request.POST.get('has_attach', 'false').strip()
    attach_name = request.POST.get('attach', '').strip()
    attach_type = request.POST.get('type', '').strip()  # image
    attach_path = os.path.join(config.get_config('SHAREHP_UPLOAD_DIR'), attach_name)
    attach_url = 'topic/' + attach_name  # FIXME

    # 校验参数
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not topic_title:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "话题不能为空!"}))
    if len(topic_title) >= 256:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "话题过长，只能256个字符!"}))
    if not topic_content:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "话题内容不能为空!"}))
    if len(topic_content) >= 10240:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "话题内容过长，只能10240个字符!"}))
    if has_attach == 'true' and not default_storage.exists(attach_path):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "服务器图片丢失，请重新上传!"}))

    # 上传图片至七牛
    if has_attach == 'true':
        try:
            image.qiniu_upload(attach_path, attach_url)
        except QiniuUploadFileError:
            # TODO log error
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "服务器异常，请稍后再试!"}))

    attachment = _gen_attachment_info(has_attach, attach_type, attach_path, attach_url)
    current_date = datetime.now()
    # 保存新话题 # FIXME transcation
    new_topic = Group_Topic(
        gmt_create=current_date,
        gmt_modify=current_date,
        group_id=group_id,
        user_id=_get_current_userid(request),  # won't be None
        topic_name=topic_title,
        content='',  # unused field FIXME
        comments=0,
        status='enabled'
    )
    new_topic.save()
    # 话题内容作为评论保存
    topic_comment = Topic_Comment(
        gmt_create=current_date,
        gmt_modify=current_date,
        topic_id=new_topic.id,
        user_id=_get_current_userid(request),  # won't be None
        content=json.dumps({
            'attachment': attachment,
            'text': topic_content
        }),
        status='enabled'
    )
    topic_comment.save()
    return HttpResponse(json.dumps({'success': 0, 'data': {}}))


# 评论话题
def add_topic_comment(request, topic_id):
    content = request.POST.get('content', '').strip()
    # 获取attachment(可选)
    has_attach = request.POST.get('has_attach', 'false').strip()
    attach_name = request.POST.get('attach', '').strip()
    attach_type = request.POST.get('type', '').strip()
    attach_path = os.path.join(config.get_config('SHAREHP_UPLOAD_DIR'), attach_name)
    attach_url = 'topic/' + attach_name  # FIXME

    if not Group_Topic.objects.filter(id=topic_id).exists():
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "对不起你回复的话题已经不存在!"}))
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not len(content.strip()):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "回复内容不能为空!"}))
    if len(content) >= 10240:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "回复内容过长，只能10240个字符!"}))
    if has_attach == 'true' and not default_storage.exists(attach_path):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "服务器图片丢失，请重新上传!"}))

    # 上传图片至七牛
    if has_attach == 'true':
        try:
            image.qiniu_upload(attach_path, attach_url)
        except QiniuUploadFileError:
            # TODO log error
            return HttpResponse(json.dumps({'success': -1, 'error_msg': "服务器异常，请稍后再试!"}))

    attachment = _gen_attachment_info(has_attach, attach_type, attach_path, attach_url)
    current_date = datetime.now()
    # 插入回复内容 FIXME transcation
    topic_comment = Topic_Comment(
        gmt_create=current_date,
        gmt_modify=current_date,
        topic_id=topic_id,
        user_id=_get_current_userid(request),  # won't be None
        content=json.dumps({
            'attachment': attachment,
            'text': content
        }),
        status='enabled'
    )
    topic_comment.save()

    # 更新topic相关信息
    topic = Group_Topic.objects.get(id=topic_id)
    Group_Topic.objects.filter(id=topic_id).update(gmt_modify=current_date, comments=topic.comments + 1)
    return HttpResponse(json.dumps({'success': 0, 'data': {}}))


# 上传图片
def upload_image(request):
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not request.FILES or not request.FILES['file']:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请选择一个图片!"}))

    upload_file = request.FILES['file']
    # 检查上传文件类型 TODO
    # 检查上传图片大小
    if upload_file.size >= 1024 * 1024:  # 1M
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请上传小于1M的图片!"}))
    # 保存临时文件
    filename = common.unique_filename()
    filepath = default_storage.save(os.path.join(config.get_config('SHAREHP_UPLOAD_DIR'), filename),
                                    ContentFile(upload_file.read()))
    width, height = image.get_image_size(filepath)
    return HttpResponse(json.dumps({'success': 0, 'data': {'src': filename, 'width': width, 'height': height}}))


# 上传视频
def upload_video(request):
    video_url = request.POST.get('url', '').strip()
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if len(video_url.strip()) <= 0:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请输入一个视频url!"}))
    if not video.support(video_url):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "对不起，你输入的视频链接暂时不支持!"}))
    # 获取视频信息
    video_info = video.video_info(video_url)
    if not video_info['success']:
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "无法获取视频信息，请确认视频链接的正确性!"}))

    data = {
        'id': common.unique_attach_id() ,
        'bimg': video_info['bimg'],
        'src': video_info['img'],
        'title': video_info['title'],
        'swf': video_info['swf'],
        'url': video_info['url']
    }
    cache.set_video_info(data['id'], data)  # cache 1h
    return HttpResponse(json.dumps({'success': 0, 'data': data}))


#-------------------------------------------
# 内部接口
#-------------------------------------------
# 写登录session
def _do_login(email):
    user = User.objects.get(email=email)  # ignore exception
    data = {'id': user.id, 'nickname': user.nickname, 'email': email}
    id = common.unique_session_id()
    cache.set_login_session(id, data)
    return id


# 获取return_url(登录和注册时用）
def _get_return_url(request):
    return_url = request.GET.get('return_url', None)
    referer = request.META.get('HTTP_REFERER', None)

    if not return_url and referer:
        return_url = referer
    if not return_url or not _safe_return_url(return_url):
        return_url = config.get_config('SHAREHP_DEFAULT_RETURN_URL')  # default return url
    return return_url


# 校验return_url安全性
# 1. 空的return_url
# 2. 非本域名url TODO
# 3. 含有login或者register的return_url(防止死循环)
def _safe_return_url(return_url):
    if not return_url or not return_url.strip():
        return False
    elif return_url.find('login') != -1 or return_url.find('register') != -1:
        return False
    else:
        return True


# 检查用户登录态
def _check_login(request):
    return request.xmanuser['login']


# 获取当前登录用户的user_id(没有登录返回None)
def _get_current_userid(request):
    if request.xmanuser['login']:
        return request.xmanuser['id']


# 获取当前分页，默认返回1
def _get_page(request):
    return common.safe_int(request.GET.get('page', 1), 1)


# 生成topic_comment表的content字段(json)中attachment信息
# add_new_topic/add_topic_comment 使用
def _gen_attachment_info(has_attach, attach_type, attach_path, attach_url):
    # default value
    attachment = {
        'type': '',
        'size': '',  # only image used
        'url': '',
        'exsit': False
    }
    if has_attach == 'false':
        pass  # do nothing
    elif attach_type == 'image':
        attachment['type'] = attach_type
        attachment['size'] = image.get_image_size(attach_path)
        attachment['url'] = attach_url
        attachment['exsit'] = True
    elif attach_type == 'video':
        pass  # not support now!
    else:
        pass  # error!

    return attachment


# 获取最新的资源ID
def _last_resource_id(res_id):
    last_res_id = cache.get_last_resource_id()
    if not last_res_id:
        last_res_id = Resource.objects.filter(status='enabled').aggregate(Max('id'))['id__max']
        cache.set_last_resource_id(last_res_id)
    return last_res_id == res_id


def _first_resource_id(res_id):
    return res_id == 1  # id为1的这条资源永远不会删除


