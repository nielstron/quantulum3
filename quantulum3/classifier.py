# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classifier functions.
"""

# Standard library
import json
import logging
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

# Quantulum
from . import load
from .load import cached
from . import language


def _get_classifier(lang='en_US'):
    return language.get('classifier', lang)


################################################################################
def ambiguous_units(lang='en_US'):  # pragma: no cover
    """
    Determine ambiguous units
    :return: list ( tuple( key, list (Unit) ) )
    """
    ambiguous = [
        i for i in list(load.units(lang).surfaces_all.items()) if len(i[1]) > 1
    ]
    ambiguous += [
        i for i in list(load.units(lang).symbols.items()) if len(i[1]) > 1
    ]
    ambiguous += [
        i for i in list(load.units(lang).derived.items()) if len(i[1]) > 1
    ]
    return ambiguous


################################################################################
def download_wiki(store=True, lang='en_US'):  # pragma: no cover
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

        obj = {
            '_id': page[1],
            'url': 'https://{}.wikipedia.org/wiki/{}'.format(
                lang[:2], page[1]),
            'clean': page[1].replace('_', ' ')
        }

        print('---> Downloading %s (%d of %d)' % (obj['clean'], num + 1,
                                                  len(pages)))

        obj['text'] = wikipedia.page(obj['clean']).content
        obj['unit'] = page[0]
        objs.append(obj)

    path = language.topdir(lang).joinpath('wiki.json')
    if store:
        with path.open('w') as wiki_file:
            json.dump(objs, wiki_file, indent=4, sort_keys=True)

    print('\n---> All done.\n')
    return objs


################################################################################
def clean_text(text, lang='en_US'):
    """
    Clean text for TFIDF
    """
    return _get_classifier(lang).clean_text(text)


################################################################################
def train_classifier(parameters=None,
                     ngram_range=(1, 1),
                     store=True,
                     lang='en_US'):
    """
    Train the intent classifier
    TODO auto invoke if sklearn version is new or first install or sth
    @:param store (bool) store classifier in clf.joblib
    """
    training_set = load.training_set(lang)
    target_names = list(set([i['unit'] for i in training_set]))

    train_data, train_target = [], []
    for example in training_set:
        train_data.append(clean_text(example['text'], lang))
        train_target.append(target_names.index(example['unit']))

    tfidf_model = TfidfVectorizer(
        sublinear_tf=True,
        ngram_range=ngram_range,
        stop_words=_get_classifier(lang).stop_words())

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
        path = language.topdir(lang).joinpath('clf.joblib')
        with path.open('wb') as file:
            joblib.dump(obj, file)
    return obj


################################################################################
class Classifier(object):
    def __init__(self, obj=None, lang='en_US'):
        """
        Load the intent classifier
        """
        self.tfidf_model = None
        self.classifier = None
        self.target_names = None

        if not USE_CLF:
            return

        if not obj:
            path = language.topdir(lang).joinpath('clf.joblib')
            with path.open('rb') as file:
                obj = joblib.load(file)

        cur_scipy_version = pkg_resources.get_distribution(
            'scikit-learn').version
        if cur_scipy_version != obj.get(
                'scikit-learn_version'):  # pragma: no cover
            logging.warning(
                "The classifier was built using a different scikit-learn version (={}, !={}). The disambiguation tool could behave unexpectedly. Consider running classifier.train_classfier()"
                .format(obj.get('scikit-learn_version'), cur_scipy_version))

        self.tfidf_model = obj['tfidf_model']
        self.classifier = obj['clf']
        self.target_names = obj['target_names']


@cached
def classifier(lang='en_US'):
    """
    Cached classifier object
    :param lang:
    :return:
    """
    return Classifier(lang=lang)


################################################################################
def disambiguate_entity(key, text, lang='en_US'):
    """
    Resolve ambiguity between entities with same dimensionality.
    """

    if len(load.entities().derived[key]) > 1:
        transformed = classifier(lang).tfidf_model.transform(
            [clean_text(text)])
        scores = classifier(lang).classifier.predict_proba(
            transformed).tolist()[0]
        scores = zip(scores, classifier(lang).target_names)

        # Filter for possible names
        names = [i.name for i in load.entities(lang).derived[key]]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            new_ent = load.entities(lang).names[scores[0][1]]
        except IndexError:
            logging.debug('\tAmbiguity not resolved for "%s"', str(key))
    else:
        new_ent = next(iter(load.entities(lang).derived[key]))

    return new_ent


################################################################################
def disambiguate_unit(unit, text, lang='en_US'):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    """

    new_unit = (load.units(lang).symbols.get(unit)
                or load.units(lang).surfaces.get(unit)
                or load.units(lang).surfaces_lower.get(unit.lower())
                or load.units(lang).symbols_lower.get(unit.lower()))
    if not new_unit:
        raise KeyError('Could not find unit "%s" from "%s"' % (unit, text))

    if len(new_unit) > 1:
        transformed = classifier(lang).tfidf_model.transform(
            [clean_text(text)])
        scores = classifier(lang).classifier.predict_proba(
            transformed).tolist()[0]
        scores = zip(scores, classifier(lang).target_names)

        # Filter for possible names
        names = [i.name for i in new_unit]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            final = load.units(lang).names[scores[0][1]]
            logging.debug(
                '\tAmbiguity resolved for "%s" (%s)' % (unit, scores))
        except IndexError:
            logging.debug('\tAmbiguity not resolved for "%s"' % unit)
            final = next(iter(new_unit))
    else:
        final = next(iter(new_unit))

    return final
