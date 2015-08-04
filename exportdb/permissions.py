import rules
from django.conf import settings

@rules.predicate
def permission(*args, **kwargs):
    predicate = getattr(settings, 'EXPORTDB_PERMISSION', rules.is_superuser)

    return predicate(*args, **kwargs)


rules.add_rule('exportdb.can_export', permission)
