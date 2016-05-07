#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:
    reload(sys).setdefaultencoding('UTF-8')
except:
    pass

try:
    from setuptools import setup
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)

import codecs
import quantulum

setup(
    name='quantulum',
    packages=['quantulum'],
    package_data={'quantulum': ['clf.pickle', 'units.json', 'entities.json', 'tests.json', 'train.json', 'wiki.json']},
    description='Extract quantities from unstructured text.',
    long_description=open('README.rst').read(),
    download_url='https://github.com/marcolagi/quantulum/tarball/0.1',
    version=quantulum.__version__,
    url=quantulum.__url__,
    author=quantulum.__author__,
    author_email=quantulum.__author_email__,
    license=quantulum.__license__,
    test_suite='quantulum.tests.EndToEndTests',
    keywords=['information extraction', 'quantities', 'units', 'measurements',
              'nlp', 'natural language processing', 'text mining',
              'text processing'],
    install_requires=[
          'inflect', 'stemming', 'numpy', 'scipy', 'wikipedia', 'sklearn'
      ],
    classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Development Status :: 3 - Alpha',
          'Natural Language :: English',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Linguistic',
          'Topic :: Scientific/Engineering'
    ]
)
