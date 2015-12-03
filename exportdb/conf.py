import os
import posixpath

from django.conf import settings

import rules
from appconf import AppConf


EXPORT_SUBDIR = 'exports'


class ExportDBConf(AppConf):
    EXPORT_ROOT = os.path.join(settings.MEDIA_ROOT, EXPORT_SUBDIR)
    EXPORT_MEDIA_URL = posixpath.join(settings.MEDIA_URL, EXPORT_SUBDIR)
    EXPORT_CONF = {}

    # form used in admin view to confirm export
    CONFIRM_FORM = 'django.forms.Form'

    # Who can perform the export
    PERMISSION = rules.is_superuser
