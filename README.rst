Django Export DB
================

Export the entire database to an Excel workbook with a sheet per model.

.. image:: https://travis-ci.org/maykinmedia/django-exportdb.svg?branch=master
    :target: https://travis-ci.org/maykinmedia/django-exportdb


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
