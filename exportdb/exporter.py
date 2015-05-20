from django.contrib import admin

from import_export import resources
from tablib import Databook
from tempfile import NamedTemporaryFile

try:  # 1.7 and higher
    from django.apps.apps import get_models
except ImportError:
    from django.db.models import get_models


def get_export_models(admin_only=False):
    """
    Gets a list of models that can be exported.
    """

    # FIXME, dev only
    from bluebottle.payouts.models import OrganizationPayout
    from django.contrib.auth.models import Group
    return [OrganizationPayout, Group]

    if admin_only:
        return admin.site._registry.keys()
    return get_models()


def get_resources():
    """
    Gets the resources of models to export.
    """
    models = get_export_models()
    return [resources.modelresource_factory(model) for model in models]


def get_resource_for_model(model):
    """
    Finds or generates the resource to use for :param:`model`.
    """
    # TODO: settings to map model to resource
    return resources.modelresource_factory(model)()


class Exporter(object):

    def __init__(self, resources, export_to=None):
        self.resources = resources
        self.export_to = export_to

    def export(self, format='xlsx'):
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

        try:
            if self.export_to is not None:
                outfile = open(self.export_to, 'wb')
            else:
                outfile = NamedTemporaryFile(delete=False)
            outfile.write(getattr(book, format))
        except:
            raise
        finally:
            outfile.close()

        return outfile
