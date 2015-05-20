import os

from setuptools import setup, find_packages

import exportdb


def read_file(name, as_list=False):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        if as_list:
            return f.readlines()
        return f.read()


readme = read_file('README.rst')
requirements = read_file('requirements/base.txt', as_list=True)
test_requirements = read_file('requirements/test.txt', as_list=True)

setup(
    name='django-exportdb',
    version=exportdb.get_version(),
    license='MIT',

    # Packaging
    packages=find_packages(exclude=('tests', 'tests.*')),
    install_requires=requirements,
    include_package_data=True,
    extras_require={
        'test': test_requirements,
    },
    tests_require=test_requirements,
    test_suite='tests.runtests.runtests',

    # PyPI metadata
    description='Dump the entire database to xlsx workbook with a sheet per model',
    long_description='\n\n'.join([readme]),
    author='Maykin Media, Sergei Maertens',
    author_email='sergei@maykinmedia.nl',
    platforms=['any'],
    url='',  # TODO
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
