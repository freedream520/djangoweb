# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.template import RequestContext
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
from models import Resource
from models import User
from models import Resource_Comment
from models import Group
from models import Group_Topic
from models import Topic_Comment
import json
import math
import forms
import cache
import uuid
import urllib
import qiniu_helper


# 分类页面
def classify(request, tag):
    page_size = 10

    if tag and tag.strip() in ('video', 'image'):
        page = _get_page(request)
        offset = (int(page) - 1) * page_size

        rl = Resource.objects.filter(type=tag.strip())[offset: offset + page_size]  # FIXME
        resCount = Resource.objects.filter(type=tag.strip()).count()
        pages = int(math.ceil(resCount / (page_size * 1.0)))

        resList = []
        for r in rl:
            res = {
                'id': r.id,
                'date': r.gmt_create,
                'userid': r.user_id,
                'nickname': cache.get_user_nickname(r.user_id),
                'title': r.title,
                'type': r.type,
                'thumbnail': r.thumbnail,
                'good': r.good,
                'bad': r.bad,
                'comments': r.comments
            }
            resList.append(res)

        context = RequestContext(request, {'tag': tag.strip(), 'resList': resList, 'curPage': page, 'pages': pages})
        return render_to_response('tag.htm', context)


# 首页
def index(request):
    page_size = 20
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    rl = Resource.objects.all()[offset: offset + page_size]  # FIXME
    #resCount = Resource.objects.all().count()
    #pages = int(math.ceil(resCount / (page_size * 1.0)))
    # 分发资源到瀑布中
    resListArray = [[], [], [], []]
    for i, r in enumerate(rl):
        res = {
            'id': r.id,
            'date': r.gmt_create,
            'userid': r.user_id,
            'nickname': cache.get_user_nickname(r.user_id),
            'title': r.title,
            'type': r.type,
            'thumbnail': r.thumbnail,
            'good': r.good,
            'bad': r.bad,
            'comments': r.comments
        }
        # 标题过长
        if len(res['title']) > 36:
            res['title'] = res['title'][:36] + '...'
        resListArray[i % 4].append(res)

    context = RequestContext(request, {
        'resListArray': resListArray})

    return render_to_response('index.htm', context)


# 资源详情页面
def detail(request, tag, resid):
    if (tag.strip() in ('video', 'image')):
        # FIXME exception
        r = Resource.objects.get(id=resid)

        # 资源信息
        res = {
            'id': r.id,
            'date': r.gmt_create,
            'userid': r.user_id,
            'nickname': cache.get_user_nickname(r.user_id),
            'title': r.title,
            'type': r.type,
            'content': json.loads(r.content)[0],
            'good': r.good,
            'bad': r.bad
        }

        # 上一个/下一个 FIXME
        hasNext = True
        hasPrev = True
        if res['id'] == 1:
            hasPrev = False
        if res['id'] == 126:
            hasNext = False

        # 评论信息
        commentList = []
        cl = Resource_Comment.objects.filter(res_id=resid)
        for comment in cl:
            commentList.append({
                'comment_id': comment.id,
                'date': comment.gmt_create,
                'user_id': comment.user_id,
                'username': cache.get_user_nickname(comment.user_id),
                'content': comment.content})

        context = RequestContext(request, {
            'res': res,
            'commentList': commentList,
            'next': hasNext,
            'prev': hasPrev})
        return render_to_response('detail.htm', context)
    else:
        # TODO
        pass


# 下一个/上一个资源
def another(request, tag, resid, order):
    # TODO 分页优化
    if order == 'next':
        rl = Resource.objects.filter(id__gt=resid)[:1]
    else:
        rl = Resource.objects.filter(id__lt=resid).order_by('-id')[:1]

    if len(rl) > 0:
        return detail(request, tag, rl[0].id)
    else:
        pass


# 群组列表页面
def groups(request):
    # groups = Group.objects.filter(status='enabled')
    groups = Group.objects.all()
    context = RequestContext(request, {'groups': groups})
    return render_to_response('groups.htm', context)


# 群组页面(帖子列表)
def group(request, group_id, order):
    is_exist = Group.objects.filter(id=group_id).exists()
    if not is_exist:
        return Http404()

    # 每页显示15条
    page_size = 15
    page = _get_page(request)
    offset = (int(page) - 1) * page_size
    # 排序
    if order == 'hot':
        # FIXME 最热排序逻辑
        ts = Group_Topic.objects.filter(group_id=group_id, status='enabled').order_by('-gmt_create', '-comments')[
             offset: offset + page_size]
    else:
        ts = Group_Topic.objects.filter(group_id=group_id, status='enabled').order_by('-gmt_create')[
             offset: offset + page_size]
    # 生成模板变量
    # TODO cache
    topic_count = Group_Topic.objects.filter(group_id=group_id, status='enabled').count()
    pages = int(math.ceil(topic_count / (page_size * 1.0)))

    topics = []
    for t in ts:
        topic = {
            'id': t.id,
            'topic_name': t.topic_name,
            'user_id': t.user_id,
            'nickname': cache.get_user_nickname(t.user_id),
            'comments': t.comments,
            'last_comment_date': t.gmt_modify.strftime('%Y-%m-%d %H:%M:%S')
        }
        topics.append(topic)
    group = cache.get_group_info(group_id)
    context = RequestContext(request, {'group': group, 'topics': topics, 'curPage': page, 'pages': pages})
    return render_to_response('group.htm', context)


# 帖子页面
def group_topic(request, topic_id):
    is_exist = Group_Topic.objects.filter(id=topic_id).exists()
    if not is_exist:
        pass
        # return error page TODO

    # 每页显示20楼
    page_size = 20
    page = _get_page(request)
    offset = (int(page) - 1) * page_size

    tcs = Topic_Comment.objects.filter(topic_id=topic_id)[offset: offset + page_size]
    topic_comments = []
    for floor, tc in enumerate(tcs):
        content = json.loads(tc.content)
        topic_comment = {
            'floor': floor + 1,
            'date': tc.gmt_create.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': tc.user_id,
            'nickname': cache.get_user_nickname(tc.user_id),
            'text': content['text'],
            'attachment': content['attachment'],
        }
        topic_comments.append(topic_comment)
    topic = cache.get_topic_info(topic_id)
    group = cache.get_group_info_by_topicid(topic['id'])

    # TODO cache
    comment_count = Topic_Comment.objects.filter(id=topic_id, status='enabled').count()
    pages = int(math.ceil(comment_count / (page_size * 1.0)))

    context = RequestContext(request, {'group': group, 'topic': topic, 'topicComments': topic_comments, 'curPage': page,
                                       'pages': pages})
    return render_to_response('group_topic.htm', context)


# 发布新帖
def new_topic(request, group_id):
    group = cache.get_group_info(group_id)
    context = RequestContext(request, {'group': group})
    return render_to_response('new_topic.htm', context)


# 注册会员
def register(request):
    if request.method == 'POST':  # 提交表单
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            register_date = datetime.now()
            # 保存用户信息
            user = User(
                gmt_create=register_date,
                gmt_modify=register_date,
                email=form.cleaned_data['email'].strip(),
                nickname=form.cleaned_data['nickname'].strip(),
                password=form.cleaned_data['password'].strip(),
                status='enabled')
            user.save()
            # 写登录session
            session_id = _do_login(user.id)
            return_url = _get_return_url(request)
            response = HttpResponseRedirect(return_url)
            response.set_cookie('id', session_id)
            return response
        else:
            return render_to_response('register.htm', {'form': form})

    else:  # 渲染页面
        return_url = urllib.urlencode({'return_url': _get_return_url(request)})
        register_action_url = '/register/?' + return_url
        return render_to_response('register.htm', {'register_action_url': register_action_url})


# 登录
def login(request):
    if request.method == 'POST':  # 提交表单
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
    else:  # 渲染页面
        return_url = urllib.urlencode({'return_url': _get_return_url(request)})
        login_action_url = '/login/?' + return_url
        return render_to_response('login.htm', {'login_action_url': login_action_url})


# 包装器
def require_login(view):
    def new_view(request, *args, **kwargs):
        if not request.xmanuser['login']:
            return_url = urllib.urlencode({'return_url': 'http://127.0.0.1:8000' + request.get_full_path()})
            return HttpResponseRedirect('/login/?' + return_url)
        else:
            return view(request, *args, **kwargs)

    return new_view


# 登出
def loginout(request):
    return_url = _get_return_url(request)
    response = HttpResponseRedirect(return_url)
    response.set_cookie('id', '', 0)  # del cookie
    return response


#-------------------------------------------
# API 接口, 供前端JS调用
# 调用成功： {'success': 0, 'data': {...}}
# 调用失败： {'success': -1, error_msg: {...}}
#-------------------------------------------

# 对资源进行评论
def comment(request):
    resid = request.POST.get('resid', None)
    content = request.POST.get('content', None)
    userid = _get_current_userid(request)

    # check params
    if not resid or not Resource.objects.filter(id=resid).exists():
        return HttpResponse(json.dumps({'success': 1, 'error_msg': "resid参数不合法"}))
    if not userid or not User.objects.filter(id=userid).exists():
        return HttpResponse(json.dumps({'success': 1, 'error_msg': "userid参数不合法"}))
    if not content or len(content) > 10240:
        return HttpResponse(json.dumps({'success': 1, 'error_msg': "content参数不合法"}))

    # insert new comment
    comment = Resource_Comment(
        gmt_create=datetime.now(),
        gmt_modify=datetime.now(),
        res_id=resid,
        user_id=userid,
        content=content,
        status='enabled')
    comment.save()
    return HttpResponse(json.dumps({'success': 0, 'error_msg': ""}))


# 发表新话题
def add_new_topic(request, group_id):
    # 获取发帖的标题&内容
    title = request.POST.get('title', None)
    content = request.POST.get('content', None)
    # 获取attachment(可选)
    attach_name = request.POST.get('attachment', '')
    attach_type = request.POST.get('type', None)
    attach_path = settings.MEDIA_ROOT + attach_name

    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not title or not len(title.strip()):  #  TODO check max-len
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "帖子标题不能为空!"}))
    if not content or not len(content.strip()):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "帖子内容不能为空!"}))
    if attach_name and not default_storage.exists(attach_path):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "图片丢失，请重新上传!"}))

    #qiniu_helper.upload('group/' + group_id + '/topic/', '')

    attachment = _gen_attachment_info(attach_name, attach_type)
    current_date = datetime.now()
    # 保存新话题 # FIXME transcation
    new_topic = Group_Topic(
        gmt_create=current_date,
        gmt_modify=current_date,
        group_id=group_id,
        user_id=_get_current_userid(request),  # won't be None
        topic_name=title,
        content='',  # FIXME unused field
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
            'text': content
        }),
        status='enabled'
    )
    topic_comment.save()
    return HttpResponse(json.dumps({'success': 0, 'data': {}}))


# 评论话题
def add_new_comment(request, topic_id):
    content = request.POST.get('content', None)
    if not Group_Topic.objects.filter(id=topic_id).exists():
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "对不起你回复的话题已经不存在!"}))
    if not _check_login(request):
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "请登录后操作!"}))
    if not content or not len(content.strip()):  # TODO check max-len
        return HttpResponse(json.dumps({'success': -1, 'error_msg': "回复内容不能为空!"}))

    # attachment可选
    attachment = _gen_attachment_info(
        request.POST.get('attachment', None),
        request.POST.get('type', None)
    )
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
    topic = Group_Topic.objects.filter(id=topic_id)[0]
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
    filename = str(uuid.uuid1()).replace('-', '')
    default_storage.save(settings.MEDIA_ROOT + filename, ContentFile(upload_file.read()))
    return HttpResponse(json.dumps({'success': 0, 'data': {'src': filename}}))


#-------------------------------------------
# 内部接口
#-------------------------------------------

def _do_login(email):
    user = User.objects.get(email=email)
    data = {'id': user.id, 'nickname': user.nickname}
    id = uuid.uuid1()
    cache.set_login_session(id, json.dumps(data))
    return id


# 获取return_url(登录和注册时用到）
def _get_return_url(request):
    return_url = request.GET.get('return_url', None)
    referer = request.META.get('HTTP_REFERER', None)

    if not return_url and referer:
        return_url = referer
    if not return_url or not _safe_return_url(return_url):
        # default return url
        return_url = "http://127.0.0.1:8000/index/"  #FIXME
    return return_url


def _safe_return_url(return_url):
    if not return_url or not return_url.strip():
        return False
    elif return_url.find('login') != -1 or return_url.find('register') != -1:
        return False
    else:
        return True


def _check_login(request):
    return request.xmanuser['login']


def _get_current_userid(request):
    if request.xmanuser['login']:
        return request.xmanuser['id']


def _get_page(request):
    page = request.GET.get('page', None)
    if not page or int(page) <= 0:
        page = 1
    return page


def _gen_attachment_info(attach_name, type):
    # default value
    attachment = {
        'type': '',
        'size': '',
        'url': '',
        'exsit': False
    }

    if type == 'image':
        attachment['type'] = type
        attachment['size'] = ''  # TODO
        attachment['url'] = attach_name
        attachment['exsit'] = True
    elif type == 'video':
        pass
    return attachment

