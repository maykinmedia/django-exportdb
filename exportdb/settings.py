import os
import posixpath

from django.conf import settings


EXPORT_SUBDIR = getattr(settings, 'EXPORTDB_EXPORTS_SUBDIR', 'exports')

DEFAULT_EXPORT_ROOT = os.path.join(settings.MEDIA_ROOT, EXPORT_SUBDIR)
EXPORT_ROOT = getattr(settings, 'EXPORTDB_EXPORT_ROOT', DEFAULT_EXPORT_ROOT)
EXPORT_MEDIA_URL = posixpath.join(settings.MEDIA_URL, EXPORT_SUBDIR)

EXPORT_CONF = getattr(settings, 'EXPORTDB_EXPORT_CONF', {})
