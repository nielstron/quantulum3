# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classifier functions.
"""

# Standard library
import os
import json
import logging
import re
import string
import pkg_resources

# Semi-dependencies
try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.externals import joblib
    USE_CLF = True
except ImportError:
    SGDClassifier, TfidfVectorizer = None, None
    USE_CLF = False

try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    from stemming.porter2 import stem
except ImportError:
    stem = None

# Quantulum
from . import load


################################################################################
def ambiguous_units():  # pragma: no cover
    """
    Determine ambiguous units
    :return: list ( tuple( key, list (Unit) ) )
    """
    ambiguous = [i for i in list(load.ALL_UNITS.items()) if len(i[1]) > 1]
    ambiguous += [i for i in list(load.UNIT_SYMBOLS.items()) if len(i[1]) > 1]
    ambiguous += [i for i in list(load.DERIVED_ENT.items()) if len(i[1]) > 1]
    return ambiguous


################################################################################
def download_wiki(store=True):  # pragma: no cover
    """
    Download WikiPedia pages of ambiguous units.
    @:param store (bool) store wikipedia data in wiki.json file
    """
    if not wikipedia:
        print(
            "Cannot download wikipedia pages. Install package wikipedia first."
        )
        return

    ambiguous = ambiguous_units()
    pages = set([(j.name, j.uri) for i in ambiguous for j in i[1]])

    print()
    objs = []
    for num, page in enumerate(pages):

        obj = {'url': page[1]}
        obj['_id'] = obj['url'].replace('https://en.wikipedia.org/wiki/', '')
        obj['clean'] = obj['_id'].replace('_', ' ')

        print('---> Downloading %s (%d of %d)' % (obj['clean'], num + 1,
                                                  len(pages)))

        obj['text'] = wikipedia.page(obj['clean']).content
        obj['unit'] = page[0]
        objs.append(obj)

    path = os.path.join(load.TOPDIR, 'wiki.json')
    os.remove(path)
    if store:
        with open(path, 'w') as wiki_file:
            json.dump(objs, wiki_file, indent=4, sort_keys=True)

    print('\n---> All done.\n')
    return objs


################################################################################
def clean_text(text):
    """
    Clean text for TFIDF
    """
    if not stem:
        raise ImportError("Module stemming is not installed.")

    my_regex = re.compile(r'[%s]' % re.escape(string.punctuation))
    new_text = my_regex.sub(' ', text)

    new_text = [
        stem(i) for i in new_text.lower().split()
        if not re.findall(r'[0-9]', i)
    ]

    new_text = ' '.join(new_text)

    return new_text


################################################################################
def train_classifier(download=True,
                     parameters=None,
                     ngram_range=(1, 1),
                     store=True):
    """
    Train the intent classifier
    TODO auto invoke if sklearn version is new or first install or sth
    @:param store (bool) store classifier in clf.joblib
    """
    path = os.path.join(load.TOPDIR, 'train.json')
    with open(path, 'r', encoding='utf-8') as train_file:
        training_set = json.load(train_file)

    wiki_set = download_wiki(store) if download else None
    if not wiki_set:
        path = os.path.join(load.TOPDIR, 'wiki.json')
        with open(path, 'r', encoding='utf-8') as wiki_file:
            wiki_set = json.load(wiki_file)

    with open(
            os.path.join(load.TOPDIR, 'similars.json'), 'r',
            encoding='utf-8') as similar_file:
        similar_set = json.load(similar_file)

    target_names = list(
        set([i['unit'] for i in training_set + wiki_set + similar_set]))
    train_data, train_target = [], []
    for example in training_set + wiki_set + similar_set:
        train_data.append(clean_text(example['text']))
        train_target.append(target_names.index(example['unit']))

    tfidf_model = TfidfVectorizer(
        sublinear_tf=True, ngram_range=ngram_range, stop_words='english')

    matrix = tfidf_model.fit_transform(train_data)

    if parameters is None:
        parameters = {
            'loss': 'log',
            'penalty': 'l2',
            'max_iter': 50,
            'alpha': 0.00001,
            'fit_intercept': True
        }

    clf = SGDClassifier(**parameters).fit(matrix, train_target)
    obj = {
        'scikit-learn_version':
        pkg_resources.get_distribution('scikit-learn').version,
        'tfidf_model':
        tfidf_model,
        'clf':
        clf,
        'target_names':
        target_names
    }
    if store:  # pragma: no cover
        path = os.path.join(load.TOPDIR, 'clf.joblib')
        with open(path, 'wb') as file:
            joblib.dump(obj, file)
    return obj


################################################################################
def load_classifier():
    """
    Load the intent classifier
    """

    path = os.path.join(load.TOPDIR, 'clf.joblib')
    with open(path, 'rb') as file:
        obj = joblib.load(file)

    cur_scipy_version = pkg_resources.get_distribution('scikit-learn').version
    if cur_scipy_version != obj.get(
            'scikit-learn_version'):  # pragma: no cover
        logging.warning(
            "The classifier was built using a different scikit-learn version (={}, !={}). The disambiguation tool could behave unexpectedly. Consider running classifier.train_classfier()"
            .format(obj.get('scikit-learn_version'), cur_scipy_version))

    return obj['tfidf_model'], obj['clf'], obj['target_names']


if USE_CLF:
    TFIDF_MODEL, CLF, TARGET_NAMES = load_classifier()
else:
    TFIDF_MODEL, CLF, TARGET_NAMES = None, None, None


################################################################################
def disambiguate_entity(key, text):
    """
    Resolve ambiguity between entities with same dimensionality.
    """

    if len(load.DERIVED_ENT[key]) > 1:
        transformed = TFIDF_MODEL.transform([text])
        scores = CLF.predict_proba(transformed).tolist()[0]
        scores = zip(scores, TARGET_NAMES)

        # Filter for possible names
        names = [i.name for i in load.DERIVED_ENT[key]]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            new_ent = load.ENTITIES[scores[0][1]]
        except IndexError:
            logging.debug('\tAmbiguity not resolved for "%s"', str(key))
    else:
        new_ent = next(iter(load.DERIVED_ENT[key]))

    return new_ent


################################################################################
def disambiguate_unit(unit, text):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    """

    new_unit = load.UNIT_SYMBOLS.get(unit) or load.UNITS.get(unit)
    if not new_unit:
        new_unit = load.LOWER_UNITS.get(
            unit.lower()) or load.UNIT_SYMBOLS_LOWER.get(unit.lower())
        if not new_unit:
            raise KeyError('Could not find unit "%s" from "%s"' % (unit, text))

    if len(new_unit) > 1:
        transformed = TFIDF_MODEL.transform([clean_text(text)])
        scores = CLF.predict_proba(transformed).tolist()[0]
        scores = zip(scores, TARGET_NAMES)

        # Filter for possible names
        names = [i.name for i in new_unit]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            final = next(iter(load.UNITS[scores[0][1]]))
            logging.debug(
                '\tAmbiguity resolved for "%s" (%s)' % (unit, scores))
        except (StopIteration, IndexError):
            logging.debug('\tAmbiguity not resolved for "%s"' % unit)
            final = next(iter(new_unit))
    else:
        final = next(iter(new_unit))

    return final
