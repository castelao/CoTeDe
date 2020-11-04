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

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()
    if sys.version_info[0] == 2:
        requirements.replace('gsw>=3.0.6', 'gsw==3.0.6')


setup(
    name='cotede',
    version='0.23.2',
    description='Quality Control of Oceanographic Data',
    long_description=readme + '\n\n' + history,
    author='Guilherme Castelão',
    author_email='guilherme@castelao.net',
    url='http://cotede.castelao.net',
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
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License',
        ],
    keywords='CTD TSG SeaBird ARGO Quality Control oceanography hydrography',
    include_package_data=True,
    zip_safe=False,
    extras_require = {
        'GSW': ["gsw>=3.0.6"],
        'OceansDB': ["oceansdb>=0.8.6"],
        'manualqc': ["matplotlib"],
        'regional': ["Shapely>=1.6.4"]
    }
)
