from django.conf.urls.defaults import patterns , url
from djangoweb.sharehp import views
from djangoweb.sharehp.views import require_login

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^index/$', views.index),

    url(r'^tag/(video|image)/$', views.classify),

    url(r'^detail/(video|image)/(\d+)/$', views.detail),
    url(r'^detail/(video|image)/(\d+)/(next|prev)/$', views.another),

    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^loginout/$', views.loginout),

    url(r'^groups/$', views.groups),
    url(r'^group/(\d+)/$', views.group, {'order': 'default'}),
    # url(r'^group/(\d+)/(hot)/$', views.group),
    url(r'^group/(\d+)/new_topic/$', require_login(views.new_topic)),
    url(r'^group/topic/(\d+)/$', views.group_topic),

    url(r'^api/group/(\d+)/add_new_topic/$', views.add_new_topic),
    url(r'^api/group/topic/(\d+)/add_new_comment/$', views.add_new_comment),
    url(r'^api/upload_image/$', views.upload_image),
    url(r'^api/comment/$', views.comment),
)



