from django.conf.urls import patterns, url

from .views import ExportView, ExportPendingView


urlpatterns = patterns(
    '',
    url(r'^$', ExportView.as_view(), name='exportdb_export'),
    url(r'^progress/$', ExportPendingView.as_view(), name='exportdb_progress')
)
