from django.conf.urls.defaults import *


urlpatterns = patterns('pendle.assets.views',
    url(r'^assets/asset/bundled/add$', 'add_bundled_asset',
        name='add_bundled'),
)

