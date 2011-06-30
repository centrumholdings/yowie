from os import path

from django import VERSION

DEBUG = False
TEMPLATE_DEBUG = DEBUG

if VERSION[:2] >= (1, 3):
    DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }
else:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = ':memory:'

ROOT_URLCONF = 'test_project.urls'

TEMPLATE_DIRS = (
    path.join(path.dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'test_fileutils',
)

EXAMPLE_RSS_FEED = path.join(path.dirname(__file__), "data", "example.rss")
