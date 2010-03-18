from django.conf.urls.defaults import *


urlpatterns = patterns('listinline.views',
    url(r'^search/(?P<app_label>\w+)/(?P<module_name>\w+)/$', 'search',
        name='search'),
)
