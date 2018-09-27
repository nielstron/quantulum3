#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert a downloaded glove file into a word2vec file
"""

import sys
import os

from gensim.scripts.glove2word2vec import glove2word2vec

TOPDIR = os.path.dirname(__file__) or '.'
try:
    glove_input_file = sys.argv[1]
except IndexError:
    glove_input_file = 'glove.6B.100d.txt'

word2vec_output_file = 'word2vec.txt'
glove2word2vec(
    os.path.join(TOPDIR, glove_input_file),
    os.path.join(TOPDIR, word2vec_output_file))
