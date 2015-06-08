from django.contrib import admin
from django.db.models import get_model
from django.core.exceptions import ImproperlyConfigured

from import_export import resources, fields
from tablib import Databook

try:  # 1.7 and higher
    from django.apps.apps import get_models
except ImportError:
    from django.db.models import get_models

from .settings import EXPORT_CONF


def modelresource_factory(model, **meta_kwargs):
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

    all_fields = model._meta.get_all_field_names()
    for field in field_names:
        if field in all_fields:  # it's a real field, the meta class deals with this
            continue
        # explicitly add the field
        label = field_labels.get(field, field)
        class_attrs[field] = fields.Field(attribute=field, column_name=label, readonly=True)

    metaclass = resources.ModelDeclarativeMetaclass
    return metaclass(class_name, (resources.ModelResource,), class_attrs)


def get_export_models(admin_only=False):
    """
    Gets a list of models that can be exported.
    """
    export_conf = EXPORT_CONF.get('models')
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


def get_resource_for_model(model):
    """
    Finds or generates the resource to use for :param:`model`.
    """
    # TODO: settings to map model to resource

    model_name = u'{app_label}.{name}'.format(
        app_label=model._meta.app_label,
        name=model.__name__
    )
    export_conf = EXPORT_CONF.get('models')
    if export_conf is not None:
        fields = export_conf.get(model_name)
        if fields is not None:
            # use own factory
            return modelresource_factory(model, fields=fields)()
    return resources.modelresource_factory(model)()


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

        if task is not None:
            total = sum([resource.get_queryset().count() for resource in self.resources])
            progress = 0
            task.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'model': None}
            )

        num_done = 0
        for resource in self.resources:
            model = resource.Meta.model
            dataset = resource.export()  # takes optional queryset argument (select related)
            dataset.title = u'{name} ({app}.{model})'.format(
                name=model._meta.verbose_name_plural,
                app=model._meta.app_label,
                model=model.__name__
            )[:31]  # maximum of 31 chars int title
            book.add_sheet(dataset)

            if task is not None:
                num_done += resource.get_queryset().count()
                progress = float(num_done) / total
                task.update_state(
                    state='PROGRESS',
                    meta={'progress': progress, 'model': dataset.title}
                )
        return book
