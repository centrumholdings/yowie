#!/usr/bin/env python

import os
import sys

from os.path import join, pardir, abspath, dirname

from django.core.management import execute_from_command_line


sys.path.insert(0, abspath(join(dirname(__file__), pardir, pardir)))
sys.path.insert(0, abspath(join(dirname(__file__), pardir)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'unit_project.settings'

if __name__ == "__main__":
    execute_from_command_line()
