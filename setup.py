# -*- coding: utf-8 -*-

#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup

install_requires = ['numpy>=1.1', 'seabird']

setup(
    name='cotede',
    version='0.4.4',
    author='Guilherme Castelão',
    author_email='guilherme@castelao.net',
    packages=['cotede'],
    url='http://cotede.castelao.net',
    license='See LICENSE.txt',
    description='Quality Control of CTD profiles',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2',
        ],
    keywords='CTD SeaBird QualityControl oceanography hydrography',
    #package_dir = {'': './'},
    include_package_data=True,
)
