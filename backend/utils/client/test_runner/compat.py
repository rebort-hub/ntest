# -*- coding: utf-8 -*-
from collections import OrderedDict

try:
    import simplejson as json
except ImportError:
    import json

import sys

try:
    JSONDecodeError = json.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError

builtin_str = str
basestring = (str, bytes)
numeric_types = (int, float)
integer_types = (int,)
