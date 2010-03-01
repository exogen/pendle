import re

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^pendle/', include('pendle.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    media_url = re.escape(settings.MEDIA_URL.lstrip('/'))
    urlpatterns += patterns('django.views.static',
        url(r'^%s(?P<path>.*)$' % media_url, 'serve',
            {'document_root': settings.MEDIA_ROOT}))

