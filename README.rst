Django Export DB
================

Export the entire database to an Excel workbook with a sheet per model.

.. image:: https://travis-ci.org/maykinmedia/django-exportdb.svg?branch=master
  :target: https://travis-ci.org/maykinmedia/django-exportdb

.. image:: https://codecov.io/github/maykinmedia/django-exportdb/coverage.svg?branch=master
  :target: https://codecov.io/github/maykinmedia/django-exportdb?branch=master

.. image:: https://coveralls.io/repos/maykinmedia/django-exportdb/badge.svg
  :target: https://coveralls.io/r/maykinmedia/django-exportdb

.. image:: https://img.shields.io/pypi/v/django-exportdb.svg
  :target: https://pypi.python.org/pypi/django-exportdb

Installation
------------

    $ pip install django-exportdb

Add `exportdb` to INSTALLED_APPS, and make sure that django.contrib.admin is in there as well.

Add

    url(r'^admin/exportdb/', include('exportdb.urls'))

to your urls.py, make sure that it comes before url(r'^admin/', ...) if you hook
it into the admin.

Configuration
-------------

EXPORTDB_EXPORT_CONF
    Configures what models and fields are exported. Example::

         EXPORT_CONF = {
            'models': {
                'auth.User': {
                    'fields': ('username',),
                    'resource_class': 'app.tests.utils.UserResource'
                },
                'auth.Group': {
                    'resource_class': 'app.tests.utils.GroupResource'
                },
                'auth.Permission': {
                    'fields': ('name',)
                }
            }
        }
EXPORTDB_CONFIRM_FORM
    Form shown to confirm the export
EXPORTDB_EXPORT_ROOT
    The filesystem path where the exports are stored
EXPORTDB_PERMISSION
    Who can access the export. By default only superusers have access.

    To allow all `staff` users to use the export add the following to your settings::

        EXPORTDB_PERMISSION = rules.is_staff
