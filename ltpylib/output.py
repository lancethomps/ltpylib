#!/usr/bin/env python3
import json


def prettify_json(obj) -> str:
  return json.dumps(obj, sort_keys=True, indent='  ', default=lambda x: getattr(x, '__dict__', str(x)))
