from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^admin/exportdb/', include('exportdb.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns()
