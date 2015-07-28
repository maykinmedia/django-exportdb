import os
import posixpath

from django.conf import settings

from appconf import AppConf


EXPORT_SUBDIR = 'exports'


class ExportDBConf(AppConf):
    EXPORT_ROOT = os.path.join(settings.MEDIA_ROOT, EXPORT_SUBDIR)
    EXPORT_MEDIA_URL = posixpath.join(settings.MEDIA_URL, EXPORT_SUBDIR)
    EXPORT_CONF = {}

    # form used in admin pview to confirm export
    CONFIRM_FORM = 'django.forms.Form'
