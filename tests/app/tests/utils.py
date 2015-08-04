from exportdb.exporter import ExportModelResource


class UserResource(ExportModelResource):
    custom_attr = 1

    def __init__(self, **kwargs):
        super(UserResource, self).__init__(**kwargs)
        self.foo = kwargs.get('foo')


class GroupResource(ExportModelResource):
    custom_attr = 1
