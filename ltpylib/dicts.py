#!/usr/bin/env python3
# pylint: disable=C0111
from typing import List

from ltpylib import checks, strings


def convert_string_values_to_correct_type(
  obj: dict,
  convert_numbers: bool = True,
  convert_booleans: bool = True,
) -> dict:
  for key in obj.keys():
    val = obj.get(key)
    if isinstance(val, str):
      if convert_numbers and strings.is_number(val):
        obj[key] = strings.convert_to_number(val)
      elif convert_booleans and strings.is_boolean(val):
        obj[key] = strings.convert_to_bool(val)

  return obj


def find(key: str, obj: dict) -> List[dict]:
  if isinstance(obj, dict):
    for k, v in obj.items():
      if k == key:
        yield v
      else:
        for res in find(key, v):
          yield res
  elif isinstance(obj, list):
    for d in obj:
      for res in find(key, d):
        yield res

  # for k, v in obj.items():
  #   if k == key:
  #     yield v
  #   elif isinstance(v, dict):
  #     for res in find(key, v):
  #       yield res
  #   elif isinstance(v, list):
  #     for d in v:
  #       for res in find(key, d):
  #         yield res


def remove_nulls(dict_with_nulls: dict) -> dict:
  return {key: val for (key, val) in dict_with_nulls.items() if val is not None}


def remove_nulls_and_empty(dict_with_nulls: dict) -> dict:
  return {key: val for (key, val) in dict_with_nulls.items() if checks.is_not_empty(val)}


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
