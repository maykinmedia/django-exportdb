import logging

from django.conf import settings
from django.contrib import admin
from django.db import connection
from django.db.models.query import QuerySet
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text

from import_export import resources, fields
from tablib import Databook, Dataset

from .compat import get_model, get_models, import_string


logger = logging.getLogger(__name__)


class ExportModelResource(resources.ModelResource):
    """
    Resource class that ties in better with Celery and progress reporting.
    """

    num_done = 0
    title = None

    def __init__(self, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs.pop('title')

        self.kwargs = kwargs  # by default, silently accept all kwargs

    def export(self, queryset=None, task_meta=None):
        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data = Dataset(headers=headers)

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset

        if task_meta is not None:  # initialize the total amount accross multiple resources
            self.num_done = task_meta['done']

        for obj in iterable:
            data.append(self.export_resource(obj))

            if task_meta is not None:
                self._update_task_state(task_meta)

            logger.debug('Num done: %d' % self.num_done)

        return data

    def _update_task_state(self, task_meta):
        total = task_meta['total']
        self.num_done += 1
        progress = float(self.num_done) / total
        task_meta['task'].update_state(
            state='PROGRESS',
            meta={'progress': progress, 'model': self.__class__.__name__}
        )


def modelresource_factory(model, resource_class=ExportModelResource, **meta_kwargs):
    attrs = {'model': model}

    field_names = []
    field_labels = {}
    if 'fields' in meta_kwargs:
        for field in meta_kwargs['fields']:
            if isinstance(field, tuple):
                field_names.append(field[0])
                field_labels[field[0]] = field[1]
            else:
                field_names.append(field)
        attrs['fields'] = field_names
        attrs['export_order'] = field_names
        del meta_kwargs['fields']

    attrs.update(**meta_kwargs)

    Meta = type(str('Meta'), (object,), attrs)
    class_name = model.__name__ + str('Resource')
    class_attrs = {'Meta': Meta}

    all_fields = [f.name for f in model._meta.get_fields()]
    for field in field_names:
        # it's a real field, the meta class deals with this
        if field in all_fields and field not in field_labels:
            continue
        # explicitly add the field
        label = field_labels.get(field, field)
        class_attrs[field] = fields.Field(attribute=field, column_name=label, readonly=True)

    metaclass = resources.ModelDeclarativeMetaclass
    return metaclass(class_name, (resource_class,), class_attrs)


def get_export_models(admin_only=False):
    """
    Gets a list of models that can be exported.
    """
    export_conf = settings.EXPORTDB_EXPORT_CONF.get('models')
    if export_conf is None:
        if admin_only:
            if admin.site._registry == {}:
                admin.autodiscover()
            return admin.site._registry.keys()
        return get_models()
    else:
        models = []
        not_installed = []
        for model, _ in export_conf.items():
            app_label, model_class_name = model.split('.')
            model_class = get_model(app_label, model_class_name)
            if model_class is not None:
                models.append(model_class)
            else:
                not_installed.append(model)

        if not_installed:
            raise ImproperlyConfigured(
                'The following models can\'t be exported because they haven\'t '
                'been installed: %s' % u', '.join(not_installed)
            )
        return models


def get_resource_for_model(model, **kwargs):
    """
    Finds or generates the resource to use for :param:`model`.
    """
    # TODO: settings to map model to resource

    model_name = u'{app_label}.{name}'.format(
        app_label=model._meta.app_label,
        name=model.__name__
    )
    resource_class = ExportModelResource
    export_conf = settings.EXPORTDB_EXPORT_CONF.get('models')
    if export_conf is not None:
        model_conf = export_conf.get(model_name)
        if model_conf is not None:

            # support custom resource titles
            kwargs['title'] = model_conf.get('title')

            # support custom resource classes
            if 'resource_class' in model_conf:
                resource_class = import_string(model_conf['resource_class'])

            # specify fields to be exported
            fields = model_conf.get('fields')
            if fields is not None:
                # use own factory
                return modelresource_factory(model, resource_class=resource_class, fields=fields)(**kwargs)
    return resources.modelresource_factory(model, resource_class=resource_class)(**kwargs)


class Exporter(object):

    def __init__(self, resources):
        self.resources = resources

    def export(self, task=None):
        """
        Export the resources to a file.

        :param task: optional celery task. If given, the task state will be
                     updated.
        """
        book = Databook()

        export_kwargs = {}
        if task is not None:
            total = sum([resource.get_queryset().count() for resource in self.resources])
            export_kwargs['task_meta'] = {'task': task, 'total': total, 'done': 0}

        num_queries_start = len(connection.queries)

        for resource in self.resources:
            model = resource.Meta.model
            logger.debug('Export kwargs: %s' % export_kwargs)
            dataset = resource.export(**export_kwargs)  # takes optional queryset argument (select related)

            len_queries = len(connection.queries)
            queries = len_queries - num_queries_start
            logger.info('Number of objects: %d' % resource.get_queryset().count())
            logger.info('Executed %d queries' % queries)
            num_queries_start = len_queries

            if task is not None:
                export_kwargs['task_meta']['done'] += dataset.height

            if resource.title is not None:
                dataset.title = force_text(resource.title)[:31]  # maximum of 31 chars int title
            else:
                dataset.title = u'{name} ({app}.{model})'.format(
                    name=model._meta.verbose_name_plural,
                    app=model._meta.app_label,
                    model=model.__name__
                )[:31]  # maximum of 31 chars int title

            book.add_sheet(dataset)
        return book
