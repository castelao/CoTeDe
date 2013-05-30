# -*- coding: utf-8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='cotede',
    version='0.2.1',
    author='Guilherme Castelão',
    author_email='guilherme@castelao.net',
    packages=['cotede'],
    url='http://cotede.castelao.net',
    license='See LICENSE.txt',
    description='Quality Control of CTD profiles',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2',
        ],
    keywords='CTD SeaBird QualityControl oceanography hydrography',
    #package_dir = {'': './'},
    include_package_data=True,
)
