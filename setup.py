#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

install_requires = [
    'numpy>=1.1',
    'seabird>=0.6.3',
    'scipy',
    ]

version = '0.14.2'

setup(
    name='cotede',
    version=version,
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
    ],
    package_dir = {'cotede':
                   'cotede'},
    license='3-clause BSD',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: BSD License',
        ],
    keywords='CTD TSG SeaBird ARGO Quality Control oceanography hydrography',
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
    scripts=["bin/ctdqc"],
)
