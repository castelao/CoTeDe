from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='ctdqc',
    version='0.1',
    author='Guilherme Castelão',
    author_email='guilherme@castelao.net',
    packages=['ctdqc'],
    url='http://ctdqc.castelao.net',
    license='See LICENSE.txt',
    description='Quality Control of CTD profiles',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 2',
        ],
    keywords='CTD SeaBird QualityControl Oceanography Hydrography',
)
