from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.statistics.views',
    url(r'^stats/$', 'home', name='home')
)
