from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.reservations.views',
    url(r'^scan/$', 'scan', name='scan'),
    url(r'^scan/(?P<transaction_key>\w+)$', 'new_transaction', name='new'),
    url(r'^reservations/transaction/(?P<transaction_id>\d+)/receipt/$',
        'receipt', name='receipt'),
)
