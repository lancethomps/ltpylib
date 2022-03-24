#!/usr/bin/env python
# pylint: disable=C0111
from typing import List, Union

EMPTY_LIST: frozenset = frozenset([])
EMPTY_MAP: tuple = tuple(sorted({}.items()))


def add_missing_to_list(main_list: list, others: list) -> list:
  if not main_list:
    return others
  elif not others:
    return main_list

  main_list.extend([val for val in others if val not in main_list])
  return main_list


def flatten(list_of_lists: List[List]) -> List:
  from itertools import chain

  return list(chain.from_iterable(list_of_lists))


def flatten_list_of_possible_csv_strings(vals: List[str], sep: str = ",") -> List[str]:
  if not vals:
    return vals

  flattened = []
  for val in vals:
    flattened.extend(val.split(sep))

  return flattened


def to_csv(values: Union[List, None], sep: str = ",") -> Union[str, None]:
  return sep.join(values) if values else None
