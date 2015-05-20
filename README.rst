Django Export DB
================

Export the entire database to an Excel workbook with a sheet per model.

Installation
------------

    $ pip install django-exportdb

Add `exportdb` to INSTALLED_APPS, and make sure that django.contrib.admin is in there as well.

Add

    url(r'^admin/exportdb/', include('exportdb.urls'))

to your urls.py, make sure that it comes before url(r'^admin/', ...) if you hook
it into the admin.
