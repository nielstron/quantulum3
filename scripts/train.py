#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Train the disambiguator """

from quantulum3.classifier import train_classifier

import argparse
arguments = [
    {
        'dest': 'store',
        'help': 'store resulting classifier in quantulum3 project folder',
        'type': bool,
        'default': True
    },
    {
        'dest': 'lang',
        'help': 'language in which to train the classifier, default \'en_US\'',
        'type': str,
        'default': 'en_US'
    },
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'train',
        description='Train unit disambiguator based on data in quantulum '
        'project folder')
    for arg in arguments:
        parser.add_argument('--{}'.format(arg['dest']), **arg)
    args = parser.parse_args()
    print('Start training for language {}, {} storing the classifier'.format(
        args.lang, '' if args.store else 'not'))
    train_classifier(store=args.store, lang=args.lang)
    print('Done')
