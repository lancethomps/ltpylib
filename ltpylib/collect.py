#!/usr/bin/env python
# pylint: disable=C0111
from typing import Callable, List, Optional, TypeVar, Union

EMPTY_LIST: frozenset = frozenset([])
EMPTY_MAP: tuple = tuple(sorted({}.items()))
T = TypeVar("T")


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


def modify_list_of_dicts(
  datas: List[dict],
  fn: Callable[[dict], Optional[dict]],
  in_place: bool = False,
) -> List[dict]:
  result: List[dict] = datas

  if not in_place:
    result = []

  for idx, data in enumerate(datas):
    if in_place:
      updated_data = data
    else:
      updated_data = data.copy()

    fn_result = fn(updated_data)
    if fn_result is not None:
      updated_data = fn_result

    if in_place:
      result[idx] = updated_data
    else:
      result.append(updated_data)

  return result


def remove_nulls(values: List[T]) -> List[T]:
  return [elem for elem in values if elem is not None]


def to_csv(values: Union[List, None], sep: str = ",") -> Union[str, None]:
  return sep.join(values) if values else None
