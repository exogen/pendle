from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.institution.views',
    url(r'^scan/(?P<transaction_key>\w+)/customer$', 'scan_customer',
        name='scan-customer'),
    url(r'^scan/(?P<transaction_key>\w+)/customer/add$',
        'scan_customer_add', name='scan-customer-add'),
    url(r'^scan/(?P<transaction_key>\w+)/customer/browse$',
        'browse_customers', name='browse-customers'),
)
