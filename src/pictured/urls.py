from django.conf.urls.defaults import *
from settings import MEDIA_ROOT,MEDIA_URL,DEBUG
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^piclogin/$', 'pictures.views.picture_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^register/$', 'pictures.views.picture_register'),

    (r'^$', 'pictures.views.take'),
    (r'^users/(?P<username>\w+)', 'pictures.views.show'),
    (r'^lookslike/(?P<username>\w+)', 'pictures.views.lookalike'),
    (r'^savepic/$', 'pictures.views.save_picture'),
    (r'^pictures/(?P<path>.*)$', 'pictures.views.show_picture'),
    (r'^identify/$', 'pictures.views.identify'),
    (r'^me/$', 'pictures.views.me'),
)

if DEBUG:
    urlpatterns += patterns('',
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT, 'show_indexes': True}),
            )
