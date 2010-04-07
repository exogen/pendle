from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.reservations.views',
    url(r'^scan/$', 'scan', name='scan'),
    url(r'^scan/(?P<transaction_key>\w+)$', 'new_transaction', name='new'),
)
