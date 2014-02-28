from django.conf.urls.defaults import patterns , url
from djangoweb.sharehp import views
from djangoweb.sharehp import bops_views
from djangoweb.sharehp.views import require_login
from djangoweb.sharehp.bops_views import require_admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^index/$', views.index),

    url(r'^tag/(video|image)/$', views.classify),

    url(r'^detail/(video|image)/(\d+)/$', views.detail),
    url(r'^detail/(video|image)/(\d+)/(next|prev)/$', views.another),

    url(r'^new_resource/$', require_login(views.new_resource)),

    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^loginout/$', views.loginout),

    url(r'^groups/$', views.groups),
    url(r'^group/(\d+)/$', views.group, {'order': 'default'}),
    # url(r'^group/(\d+)/(hot)/$', views.group),
    url(r'^group/(\d+)/new_topic/$', require_login(views.new_topic)),
    url(r'^group/topic/(\d+)/$', views.group_topic),

    url(r'^account/change_avatar/$', require_login(views.change_avatar)),
    url(r'^account/change_password/$', require_login(views.change_password)),

    url(r'user/(\d+)', views.user_info),

    url(r'^api/add_new_resource/$', views.add_new_resource),
    url(r'^api/group/(\d+)/add_new_topic/$', views.add_new_topic),
    url(r'^api/group/topic/(\d+)/add_new_comment/$', views.add_topic_comment),
    url(r'^api/upload_image/$', views.upload_image),
    url(r'^api/upload_video/$', views.upload_video),
    url(r'^api/detail/(\d+)/add_new_comment/$', views.add_resource_comment),
    url(r'^api/resource_vote/(\d+)/(up|down)/$', views.resource_vote),

    url(r'^bops/tag/$', require_admin(bops_views.classify)),
    url(r'^bops/detail/(\d+)/$', require_admin(bops_views.detail)),
    url(r'^bops/resource/(\d+)/(pass|reject)/$', bops_views.process),
)



