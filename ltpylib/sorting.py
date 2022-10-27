#!/usr/bin/env python
from typing import List, Sequence

from ltpylib.dicts import create_key_getter


def sort_by_key(vals: List[dict], key: str, reverse: bool = False) -> List[dict]:
  vals.sort(key=create_key_getter(key), reverse=reverse)
  return vals


def sort_by_keys(
  vals: List[dict],
  keys: Sequence[str],
  reverse: bool = False,
  skip_missing: bool = False,
) -> List[dict]:
  if skip_missing:

    def key_func(val: dict) -> list:
      return [val.get(key) for key in keys if key in val]

  else:

    def key_func(val: dict) -> list:
      return [val.get(key, "") for key in keys]

  vals.sort(key=key_func, reverse=reverse)
  return vals
