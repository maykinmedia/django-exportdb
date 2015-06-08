import os

from django.conf import settings


DEFAULT_EXPORT_ROOT = os.path.join(settings.MEDIA_ROOT, 'exports')
EXPORT_ROOT = getattr(settings, 'EXPORTDB_EXPORT_ROOT', DEFAULT_EXPORT_ROOT)

EXPORT_CONF = getattr(settings, 'EXPORTDB_EXPORT_CONF', {})
