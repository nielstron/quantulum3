from quantulum3 import parser, regex as r
import re

for item in re.finditer(r.NUM_PATTERN, "4x2^5", re.VERBOSE | re.IGNORECASE):
    print(item)
print(parser.parse("4x2^5"))