# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
#from distutils.core import setup

import os
import sys


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

install_requires = [
    'numpy>=1.1',
    'seabird>=0.5.8',
    'scipy',
    ]

version = '0.12.6'

setup(
    name='cotede',
    version=version,
    author='Guilherme Castelão',
    author_email='guilherme@castelao.net',
    packages=['cotede', 'cotede.qctests', 'cotede.utils', 'cotede.humanqc'],
    url='http://cotede.castelao.net',
    license='License :: OSI Approved :: BSD License',
    description='Quality Control of Temperature and Salinity profiles',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        ],
    keywords='CTD SeaBird QualityControl oceanography hydrography',
    #package_dir = {'': './'},
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
    scripts=["bin/ctdqc"],
)
