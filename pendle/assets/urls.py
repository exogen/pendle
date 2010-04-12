from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.assets.views',
    url(r'^scan/(?P<transaction_key>\w+)/asset$', 'scan_asset',
        name='scan-asset'),
    url(r'^scan/(?P<transaction_key>\w+)/asset/browse$', 'browse_assets',
        name='browse-assets'),
    url(r'^assets/asset/bundled/add$', 'add_bundled_asset',
        name='add_bundled'),
)

