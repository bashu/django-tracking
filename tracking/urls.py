from django.conf.urls.defaults import *
from tracking.views import update_active_users

urlpatterns = patterns('',
    url(r'^refresh/$', update_active_users, name='tracking-refresh-active-users'),
)