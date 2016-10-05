import django

try:
    from django.utils.module_loading import import_string  # noqa
except ImportError:  # noqa
    from django.utils.module_loading import import_by_path as import_string  # noqa


try:
    # django >= 1.7
    from django.apps import apps
    get_model = apps.get_model
    get_models = apps.get_models
except ImportError:  # noqa
    # django < 1.7
    from django.db.models import get_model, get_models


def jquery_in_vendor():
    return django.VERSION >= (1, 9, 0)
