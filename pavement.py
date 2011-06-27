# -*- coding: utf-8 -*-
from __future__ import with_statement
from os import walk, chmod
from os.path import join, pardir, abspath, dirname, split

from paver.easy import *
from paver.setuputils import setup

from setuptools import find_packages

# must be in sync with yowie.VERSION
VERSION = (2, 1, 0, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


setup(
    name = 'yowie',
    version = __versionstr__,
    description = 'django yowie project',
    long_description = '\n'.join((
        'django yowie project',
        '',
        'user customizing pages',
    )),
    author = 'centrum holdings s.r.o',
    author_email='devel@centrumholdings.com',
    license = 'commercial',
    url='http://git.netcentrum.cz/projects/content/GIT/yowie.git/',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),
    include_package_data = True,

    buildbot_meta_master = {
        'host' : 'rlyeh.cnt-cthulhubot.dev.chservices.cz',
        'port' : 12034,
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
    ],
    install_requires = [
#        'django',
#        'simplejson',
#        'lxml',
        'setuptools>=0.6b1',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
)



options(
    citools = Bunch(
        rootdir = abspath(dirname(__file__)),
        doc_use_branch_dir = True,
    ),
    sphinx=Bunch(
        builddir="build",
        sourcedir=""
    ),
)

try:
    from citools.pavement import *
except ImportError:
    pass

@task
def install_dependencies():
    sh('pip install --upgrade -r requirements.txt')

@task
def bootstrap():
    options.virtualenv = {'packages_to_install' : ['pip']}
    call_task('paver.virtual.bootstrap')
    sh("python bootstrap.py")
    path('bootstrap.py').remove()


    print '*'*80
    if sys.platform in ('win32', 'winnt'):
        print "* Before running other commands, You now *must* run %s" % os.path.join("bin", "activate.bat")
    else:
        print "* Before running other commands, You now *must* run source %s" % os.path.join("bin", "activate")
    print '*'*80

@task
def generate_example_local_for_tests():
    """ Generate example local.py for settings. By coincidence, those are runnable on our BuildBot intstance. """
    from datetime import datetime
    curry = str(datetime.now().second*10000+datetime.now().microsecond)
    local = """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yowie',
        'TEST_NAME': 'test_yowie_%s',
        'USER': 'buildbot',
        'PASSWORD': 'xxx',
        'HOST': '',
        'PORT': '',
    },
}
""" % curry

    with open(join("tests", "example_project", "settings", "local.py"), 'w') as f:
        f.write(local)

@task
@needs('install_dependencies', 'generate_example_local_for_tests')
def prepare():
    """ Prepare complete environment """


def get_storage_plugin():
    from nose.plugins import Plugin
    class StoragesPurgePlugin(Plugin):
        name = 'test-storages'
        score = 78

        def options(self, parser, env=os.environ):
            Plugin.options(self, parser, env)

        def configure(self, options, config):
            Plugin.configure(self, options, config)

        def _clear(self):
            pass

        def begin(self):
            self._clear()

        def stopTest(self, test):
            self._clear()

    return StoragesPurgePlugin()

@task
@consume_args
def unit(args, nose_run_kwargs=None):
    """ Run unittests """
    nose_run_kwargs = nose_run_kwargs or {}

    args.append('--with-test-storages')

    nose_run_kwargs.update({'addplugins' : [get_storage_plugin()]})

    from citools.pavement import run_tests
    run_tests(test_project_module="unit_project", nose_args=args, nose_run_kwargs=nose_run_kwargs)

@task
@consume_args
def integrate(args, nose_run_kwargs=None):
    """ Run integration tests """
    nose_run_kwargs = nose_run_kwargs or {}

    args.extend(["--with-selenium", "--with-djangoliveserver", '--with-test-storages'])

    nose_run_kwargs.update({'addplugins' : [get_storage_plugin()]})

    from citools.pavement import run_tests
    run_tests(test_project_module="example_project", nose_args=args, nose_run_kwargs=nose_run_kwargs)
