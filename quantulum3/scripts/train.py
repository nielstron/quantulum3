#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Train the disambiguator """

import argparse
import json
import logging
import time

from quantulum3.classifier import train_classifier

_LOGGER = logging.getLogger(__name__)


def main(args=None):
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        "train",
        description="Train unit disambiguator based on data in quantulum "
        "project folder",
    )
    parser.add_argument(
        "--store",
        "-s",
        help="store resulting classifier as a joblib file",
        action="store_true",
    )
    parser.add_argument(
        "--lang",
        "-l",
        help="language in which to train the classifier, default 'en_US'",
        type=str,
        default="en_US",
    )
    parser.add_argument(
        "--data",
        "-d",
        help=(
            "path to one or more json training files. If none are given, the default training "
            "data in the quantulum3 project folder is used. Multiple files can be given by "
            "specifying this argument multiple times (e.g. -d train1.json -d train2.json). "
            "See the project README for more information."
        ),
        type=str,
        action="append",
    )
    parser.add_argument(
        "--output",
        "-o",
        help=(
            "path to a folder where the resulting classifier is stored. If "
            "not given, the default location in the quantulum3 project folder "
            "is used"
        ),
        type=str,
        default=None,
    )

    args = parser.parse_args(args)

    if args.data is not None:
        training_set = []
        args.lang = None
        for file in args.data:
            with open(file) as f:
                training_set += json.load(f)
    else:
        training_set = None

    if args.output is not None:
        # override this option if an output file is given, feels intuitive to do
        args.store = True

    _LOGGER.info(
        "Start training for language {}, {}storing the classifier".format(
            args.lang, "" if args.store else "not "
        )
    )
    start = time.process_time()
    try:
        train_classifier(
            store=args.store,
            lang=args.lang,
            training_set=training_set,
            output_path=args.output,
        )
    except ImportError:
        _LOGGER.error(
            "Could not train the classifier. Make sure you have the "
            f"required dependencies installed. "
            "These can be installed in pip using the command "
            "'pip install quantulum3[classifier]'"
        )
    else:
        end = time.process_time()
        _LOGGER.info("Done in {} s".format(end - start))


if __name__ == "__main__":
    main()
