#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""quantulum3 setup file."""

import sys

try:
    from setuptools import setup
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)

import quantulum3

setup(
    name='quantulum3',
    packages=['quantulum3'],
    package_data={
        'quantulum3': [
            'clf.pickle', 'units.json', 'entities.json', 'train.json',
            'wiki.json', 'common-words.json', 'tests/expand.json',
            'tests/quantities.json', 'tests/quantities.ambiguity.json'
        ]
    },
    description='Extract quantities from unstructured text.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    download_url='https://github.com/marcolagi/quantulum3/tarball/0.1',
    version=quantulum3.__version__,
    url=quantulum3.__url__,
    author=quantulum3.__author__,
    author_email=quantulum3.__author_email__,
    license=quantulum3.__license__,
    test_suite='quantulum3.tests',
    keywords=[
        'information extraction', 'quantities', 'units', 'measurements', 'nlp',
        'natural language processing', 'text mining', 'text processing'
    ],
    install_requires=['inflect', 'num2words'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX', 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha', 'Natural Language :: English',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering'
    ])
