#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Try to create a test case from a sentence """

import sys
import json

from quantulum3 import parser, classes

if __name__ == "__main__":
    sentence = " ".join(sys.argv[1:])
    quants = parser.parse(sentence)
    res = []
    for q in quants:
        assert isinstance(q, classes.Quantity)
        quantity = {
            "value": q.value,
            "unit": q.unit.name,
            "surface": q.surface,
            "entity": q.unit.entity.name,
            "dimensions": q.unit.entity.dimensions,
            "uncertainty": q.uncertainty,
        }
        res.append(quantity)

    test = {"req": sentence, "res": res}
    print(json.dumps(test, indent=2))
