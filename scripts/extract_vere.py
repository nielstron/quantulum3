#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract the n nearest neighbours of the ambigous units from the word2vec file
"""
import os
import json
import argparse

from quantulum3 import classifier, classes, language

TOPDIR = os.path.dirname(__file__) or "."

arguments = [
    {
        "dest": "topn",
        "help": "number of nearest neighbours that are extracted",
        "type": int,
        "default": 500,
    },
    {
        "dest": "min_similarity",
        "help": "minimum similarity to neighbour (0 to 1)",
        "type": float,
        "default": None,
    },
    {
        "dest": "filename",
        "help": "path to magnitude file, relative to current path "
        "(glove.6B.100d.magnitude)",
        "type": str,
        "default": "glove.6B.100d.magnitude",
    },
    # TODO language support
]


def glove_via_magnitude(
    topn=500, min_similarity=None, filename="glove.6B.100d.magnitude", lang="en_US"
):

    from pymagnitude import Magnitude

    v = Magnitude(os.path.join(TOPDIR, filename))
    training_set = list()
    units = set()
    for unit_list in classifier.ambiguous_units():
        for unit in unit_list[1]:
            units.add(unit)
    for unit in units:
        print("Processing {}...".format(unit.name))

        name = unit.name
        surfaces = set(unit.name)
        if isinstance(unit, classes.Unit):
            surfaces.update(unit.surfaces)
            surfaces.update(unit.symbols)
        for surface in surfaces:
            neighbours = v.most_similar(
                v.query(surface), topn=topn, min_similarity=min_similarity
            )
            training_set.append(
                {
                    "unit": name,
                    "text": " ".join(neighbour[0] for neighbour in neighbours),
                }
            )
    print("Done")

    with language.topdir(lang).joinpath("train/similars.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(training_set, file, sort_keys=True, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "extract_vere",
        description="Extract k-nearest neighbours from word vector file in "
        "magnitude format. Store result in quantulum3/similars.json.",
    )
    for arg in arguments:
        parser.add_argument("--{}".format(arg["dest"]), **arg)
    args = parser.parse_args()
    glove_via_magnitude(
        topn=args.topn, min_similarity=args.min_similarity, filename=args.filename
    )
