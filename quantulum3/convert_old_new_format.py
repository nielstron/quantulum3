import json
import logging
from typing import Any, List, Tuple

__LOGGER__ = logging.getLogger()


def object_pairs_hook_alt(object_pairs: List[Tuple[str, Any]]):
    keys = [x[0] for x in object_pairs]
    try:
        assert len(set(keys)) == len(keys)
    except AssertionError:
        raise AssertionError(
            "Dictionary has entries with same name: {}".format(
                [object_pairs[i] for i, k in enumerate(keys) if keys.count(k) > 1]
            )
        )
    return dict(object_pairs)


with open("_lang/en_US/entities.json", "r", encoding="utf-8") as old_file:
    old_dict = json.load(old_file, object_pairs_hook=object_pairs_hook_alt)
new_dict = {x.pop("name"): x for x in old_dict}
with open("_lang/en_US/entities.json", "w", encoding="utf-8") as new_file:
    json.dump(new_dict, new_file)
