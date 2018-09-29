#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Train the disambiguator """

from quantulum3.classifier import train_classifier

import argparse
arguments = [
    {
        'dest': 'download',
        'help': 'download newest wikipedia pages for units',
        'type': bool,
        'default': False
    },
    {
        'dest': 'store',
        'help': 'store resulting classifier in quantulum3 project folder',
        'type': bool,
        'default': True
    },
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'train',
        description='Train unit disambiguator based on data in quantulum project folder')
    for arg in arguments:
        parser.add_argument('--{}'.format(arg['dest']), **arg)
    args = parser.parse_args()
    train_classifier(download=args.download, store=args.store)
