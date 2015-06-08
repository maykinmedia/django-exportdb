import logging
import os

from django.conf import settings
from django.utils import timezone

from celery import shared_task, current_task

from .exporter import get_export_models, get_resource_for_model
from .settings import EXPORT_ROOT

logger = logging.getLogger(__name__)


@shared_task
def export(exporter_class, format='xlsx', **kwargs):
    """
    Generates the export.

    Support for django-tenant-schemas is built in.
    """
    tenant = kwargs.get('tenant')
    if tenant is not None:
        logger.debug('Settings tenant to %s' % tenant)
        from django.db import connection
        connection.set_tenant(tenant)

    filename = u'export-{timestamp}.{ext}'.format(
        timestamp=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        ext=format
    )

    models = get_export_models()
    resources = [get_resource_for_model(model) for model in models]
    exporter = exporter_class(resources)

    logger.info('Exporting resources: %s' % resources)
    databook = exporter.export(task=current_task)
    export_to = os.path.join(EXPORT_ROOT, filename)
    with open(export_to, 'wb') as outfile:
        outfile.write(getattr(databook, format))
    rel_path = os.path.join(settings.MEDIA_URL, 'exports')
    return os.path.join(rel_path, filename)
