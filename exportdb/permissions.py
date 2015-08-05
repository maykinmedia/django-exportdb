import rules
from django.conf import settings


@rules.predicate
def permission(*args, **kwargs):
    return settings.EXPORTDB_PERMISSION(*args, **kwargs)


rules.add_rule('exportdb.can_export', permission)
