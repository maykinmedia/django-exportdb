import os
import sys


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def runtests():
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',

            'import_export',
            'exportdb',

            'app',
        ],
        ROOT_URLCONF='urls',
        DEBUG=True,
        STATIC_URL='/static/',
        SECRET_KEY='&t=qu_de!+ih0gq9a+v3bjd^f@ulb7ioy_!o=gi^k12aebt7+i',

        MEDIA_ROOT=os.path.join(BASE_DIR, 'test_media'),

        TEMPLATES = [{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }],

        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),

        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.path.dirname(__file__), 'database.db'),
            }
        }
    )

    test_dir = os.path.dirname(__file__)
    sys.path.insert(0, test_dir)

    import django
    from django.test.utils import get_runner

    try:
        django.setup()  # 1.7 and upwards
    except AttributeError:
        pass

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['app'])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
