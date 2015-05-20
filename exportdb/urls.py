from django.conf.urls import patterns, url

from .views import ExportView


urlpatterns = patterns(
    '',
    url(r'^$', ExportView.as_view(), name='export'),
)
