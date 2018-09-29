#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Download new WikiPedia pages """

from quantulum3.classifier import download_wiki

import argparse
arguments = [
    {
        'dest': 'store',
        'help': 'store resulting classifier in quantulum3 project folder',
        'type': bool,
        'default': True
    },
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'download_wiki', description='Download and store new wikipedia pages')
    for arg in arguments:
        parser.add_argument('--{}'.format(arg['dest']), **arg)
    args = parser.parse_args()
    download_wiki(store=args.store)
