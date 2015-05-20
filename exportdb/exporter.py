from django.contrib import admin

from import_export import resources
from tablib import Databook

try:  # 1.7 and higher
    from django.apps.apps import get_models
except ImportError:
    from django.db.models import get_models


def get_export_models(admin_only=False):
    """
    Gets a list of models that can be exported.
    """
    if admin_only:
        if admin.site._registry == {}:
            admin.autodiscover()
        return admin.site._registry.keys()
    return get_models()


def get_resource_for_model(model):
    """
    Finds or generates the resource to use for :param:`model`.
    """
    # TODO: settings to map model to resource
    return resources.modelresource_factory(model)()


class Exporter(object):

    def __init__(self, resources):
        self.resources = resources

    def export(self):
        book = Databook()

        for resource in self.resources:
            dataset = resource.export()
            model = resource.Meta.model
            dataset.title = u'{name} ({app}.{model})'.format(
                name=model._meta.verbose_name_plural,
                app=model._meta.app_label,
                model=model.__name__
            )[:31]  # maximum of 31 chars int title
            book.add_sheet(dataset)
        return book
