#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:mod:`Quantulum` classifier functions.
'''

# Standard library
import re
import os
import json
import pickle
import logging

# Dependences
import wikipedia
from stemming.porter2 import stem
try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    USE_CLF = True
except ImportError:
    USE_CLF = False

# Quantulum
from . import load as l

################################################################################
def download_wiki():

    '''
    Download WikiPedia pages of ambiguous units.
    '''

    ambiguous = [i for i in l.UNITS.items() if len(i[1]) > 1]
    ambiguous += [i for i in l.DERIVED_ENT.items() if len(i[1]) > 1]
    pages = set([(j.name, j.uri) for i in ambiguous for j in i[1]])

    print
    objs = []
    for num, page in enumerate(pages):

        obj = {'url': page[1]}
        obj['_id'] = obj['url'].replace('https://en.wikipedia.org/wiki/', '')
        obj['clean'] = obj['_id'].replace('_', ' ')

        print '---> Downloading %s (%d of %d)' % \
              (obj['clean'], num + 1, len(pages))

        obj['text'] = wikipedia.page(obj['clean']).content
        obj['unit'] = page[0]
        objs.append(obj)

    path = os.path.join(l.TOPDIR, 'wiki.json')
    os.remove(path)
    json.dump(objs, open(path, 'w'), indent=4, sort_keys=True)

    print '\n---> All done.\n'


################################################################################
def clean_text(text):

    '''
    Clean text for TFIDF
    '''

    new_text = re.sub(ur'\p{P}+', ' ', text)

    new_text = [stem(i) for i in new_text.lower().split() if not \
                re.findall(r'[0-9]', i)]

    new_text = ' '.join(new_text)

    return new_text


################################################################################
def train_classifier(download=True, parameters=None, ngram_range=(1, 1)):

    '''
    Train the intent classifier
    '''

    if download:
        download_wiki()

    path = os.path.join(l.TOPDIR, 'train.json')
    training_set = json.load(open(path))
    path = os.path.join(l.TOPDIR, 'wiki.json')
    wiki_set = json.load(open(path))

    target_names = list(set([i['unit'] for i in training_set + wiki_set]))
    train_data, train_target = [], []
    for example in training_set + wiki_set:
        train_data.append(clean_text(example['text']))
        train_target.append(target_names.index(example['unit']))

    tfidf_model = TfidfVectorizer(sublinear_tf=True,
                                  ngram_range=ngram_range,
                                  stop_words='english')

    matrix = tfidf_model.fit_transform(train_data)

    if parameters is None:
        parameters = {'loss': 'log', 'penalty': 'l2', 'n_iter': 50,
                      'alpha': 0.00001, 'fit_intercept': True}

    clf = SGDClassifier(**parameters).fit(matrix, train_target)
    obj = {'tfidf_model': tfidf_model, 'clf': clf, 'target_names': target_names}
    path = os.path.join(l.TOPDIR, 'clf.pickle')
    pickle.dump(obj, open(path, 'w'))


################################################################################
def load_classifier():

    '''
    Train the intent classifier
    '''

    path = os.path.join(l.TOPDIR, 'clf.pickle')
    obj = pickle.load(open(path, 'r'))

    return obj['tfidf_model'], obj['clf'], obj['target_names']

if USE_CLF:
    TFIDF_MODEL, CLF, TARGET_NAMES = load_classifier()
else:
    TFIDF_MODEL, CLF, TARGET_NAMES = None, None, None

################################################################################
def disambiguate_entity(key, text):

    '''
    Resolve ambiguity between entities with same dimensionality.
    '''

    new_ent = l.DERIVED_ENT[key][0]

    if len(l.DERIVED_ENT[key]) > 1:
        transformed = TFIDF_MODEL.transform([text])
        scores = CLF.predict_proba(transformed).tolist()[0]
        scores = sorted(zip(scores, TARGET_NAMES), key=lambda x: x[0],
                        reverse=True)
        names = [i.name for i in l.DERIVED_ENT[key]]
        scores = [i for i in scores if i[1] in names]
        try:
            new_ent = l.ENTITIES[scores[0][1]]
        except IndexError:
            logging.debug('\tAmbiguity not resolved for "%s"', str(key))

    return new_ent


################################################################################
def disambiguate_unit(unit, text):

    '''
    Resolve ambiguity between units with same names, symbols or abbreviations.
    '''

    new_unit = l.UNITS[unit]
    if not new_unit:
        new_unit = l.LOWER_UNITS[unit.lower()]
        if not new_unit:
            raise KeyError('Could not find unit "%s"' % unit)

    if len(new_unit) > 1:
        transformed = TFIDF_MODEL.transform([clean_text(text)])
        scores = CLF.predict_proba(transformed).tolist()[0]
        scores = sorted(zip(scores, TARGET_NAMES), key=lambda x: x[0],
                        reverse=True)
        names = [i.name for i in new_unit]
        scores = [i for i in scores if i[1] in names]
        try:
            final = l.UNITS[scores[0][1]][0]
            logging.debug('\tAmbiguity resolved for "%s" (%s)', unit, scores)
        except IndexError:
            logging.debug('\tAmbiguity not resolved for "%s"', unit)
            final = new_unit[0]
    else:
        final = new_unit[0]

    return final

