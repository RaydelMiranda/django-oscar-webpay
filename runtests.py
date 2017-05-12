#!/usr/bin/env python
import os
import sys

from optparse import OptionParser

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests(*test_args):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    if not test_args:
        test_args = ['tests']

    failures = test_runner.run_tests(test_args)
    sys.exit(bool(failures))


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    run_tests(*args)
