import os

from setuptools import setup, find_packages

import exportdb


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


readme = read_file('README.rst')
requirements = [
    'Django',
    'django-appconf',
    'django-import-export',
    'celery',
    'django-celery',
    'rules',
]
test_requirements = [
    'mock',
    'factory-boy',
    'coverage'
]

setup(
    name='django-exportdb',
    version=exportdb.get_version(),
    license='MIT',

    # Packaging
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'test': test_requirements,
    },
    zip_safe=False,
    tests_require=test_requirements,
    test_suite='tests.runtests.runtests',

    # PyPI metadata
    description='Dump the entire database to xlsx workbook with a sheet per model',
    long_description='\n\n'.join([readme]),
    author='Maykin Media, Sergei Maertens',
    author_email='sergei@maykinmedia.nl',
    platforms=['any'],
    url='https://github.com/maykinmedia/django-exportdb',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
)
