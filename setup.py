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
    version='0.19.0',
    description='Quality Control of Temperature and Salinity profiles',
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
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
        ],
    keywords='CTD TSG SeaBird ARGO Quality Control oceanography hydrography',
    include_package_data=True,
    zip_safe=False,
    scripts=["bin/ctdqc"],
    extras_require = {
        'GSW': ["gsw>=3.0.6"],
        'manualqc': ["matplotlib"]
    }
)
