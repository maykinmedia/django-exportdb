try:
    from django.utils.module_loading import import_string  # noqa
except ImportError:  # noqa
    from django.utils.module_loading import import_by_path as import_string  # noqa
