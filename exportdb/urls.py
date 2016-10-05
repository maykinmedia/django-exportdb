from django.conf.urls import url

from .views import ExportView, ExportPendingView


urlpatterns = [
    url(r'^$', ExportView.as_view(), name='exportdb_export'),
    url(r'^progress/$', ExportPendingView.as_view(), name='exportdb_progress')
]
