VERSION = (0, 4, 7)


def get_version():
    return '.'.join([str(bit) for bit in VERSION])


__version__ = get_version()

default_app_config = 'exportdb.apps.ExportDBConfig'
