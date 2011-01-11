from os import path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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
