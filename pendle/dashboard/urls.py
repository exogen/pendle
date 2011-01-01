from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.dashboard.views',
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^dashboard/options/activity$', 'activity_options',
        name='activity-options'),
)
