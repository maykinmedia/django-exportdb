import logging
import os
import posixpath

from django.conf import settings
from django.utils import timezone

from celery import shared_task, current_task

from .exporter import get_export_models, get_resource_for_model

logger = logging.getLogger(__name__)


@shared_task
def export(exporter_class, format='xlsx', **kwargs):
    """
    Generates the export.

    Support for django-tenant-schemas is built in.
    """
    tenant = kwargs.pop('tenant', None)
    if tenant is not None:
        logger.debug('Settings tenant to %s' % tenant)
        from django.db import connection
        connection.set_tenant(tenant)

        export_root = settings.EXPORTDB_EXPORT_ROOT % tenant.schema_name
    else:
        export_root = settings.EXPORTDB_EXPORT_ROOT

    filename = u'export-{timestamp}.{ext}'.format(
        timestamp=timezone.now().strftime('%Y-%m-%d_%H%M%S'),
        ext=format
    )

    models = get_export_models()
    resources = [get_resource_for_model(model, **kwargs) for model in models]
    exporter = exporter_class(resources)

    logger.info('Exporting resources: %s' % resources)
    databook = exporter.export(task=current_task)
    export_to = os.path.join(export_root, filename)
    if not os.path.exists(export_root):
        os.makedirs(export_root)
    with open(export_to, 'wb') as outfile:
        outfile.write(getattr(databook, format))
    return posixpath.join(settings.EXPORTDB_EXPORT_MEDIA_URL, filename)
