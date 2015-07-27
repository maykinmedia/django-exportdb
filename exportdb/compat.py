try:
    from django.utils.module_loading import import_string
except ImportError:  # Django < 1.7
    from django.utils.module_loading import import_by_path as import_string  # noqa
