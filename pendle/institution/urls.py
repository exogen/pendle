from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.institution.views',
    url(r'^scan/(?P<transaction_key>\w+)/customer$', 'scan_customer',
        name='scan-customer'),
)
