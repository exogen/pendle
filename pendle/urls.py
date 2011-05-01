import re

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

from pendle.assets.admin import autocomplete


admin.autodiscover()

urlpatterns = patterns('',
    url('^$', 'pendle.views.home', name='home'),
    url('^admin/', include('pendle.dashboard.urls',
                           namespace='dashboard')),
    url('^admin/', include('pendle.institution.urls',
                           namespace='institution')),
    url('^admin/', include('pendle.assets.urls',
                           namespace='assets')),
    url('^admin/', include('pendle.reservations.urls',
                           namespace='reservations')),
    url('^admin/', include(admin.site.urls)),
    url('^autocomplete/', include(autocomplete.urls))
)

if settings.DEBUG:
    media_url = re.escape(settings.MEDIA_URL.lstrip('/'))
    urlpatterns += patterns('django.views.static',
        url(r'^%s(?P<path>.*)$' % media_url, 'serve',
            {'document_root': settings.MEDIA_ROOT}))

