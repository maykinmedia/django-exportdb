import rules
# TODO: this should be parametrized via settings


@rules.predicate
def is_superuser(user):
    return user.is_superuser


rules.add_rule('exportdb.can_export', is_superuser)
