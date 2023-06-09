#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    version='0.23.8',
    long_description=readme + '\n\n' + history,
    packages=[
        'cotede',
        'cotede.qctests',
        'cotede.utils',
        'cotede.humanqc',
        'cotede.anomaly_detection',
        'cotede.fuzzy',
    ],
    package_dir = {'cotede':
                   'cotede'},
    license='3-clause BSD',
    include_package_data=True,
    zip_safe=False,
)
