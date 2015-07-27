from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ExportDBConfig(AppConfig):
    name = 'exportdb'
    verbose_name = _('Export db')

    def ready(self):
        from . import conf  # noqa
