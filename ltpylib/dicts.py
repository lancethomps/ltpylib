#!/usr/bin/env python
# pylint: disable=C0111
from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar, Union

from ltpylib import checks, strings
from ltpylib.collect import modify_list_of_dicts

T = TypeVar('T')


def convert_keys_to_snake_case(
  obj: Union[dict, list],
  recursive: bool = False,
) -> Union[dict, list]:
  if isinstance(obj, list):
    objs = obj
  else:
    objs = [obj]

  for obj_dict in objs:
    dict_items = list(obj_dict.items())
    for key, val in dict_items:
      key_snake_case = strings.to_snake_case(key)
      if key != key_snake_case:
        obj_dict[key_snake_case] = obj_dict.pop(key)

      if recursive and isinstance(val, dict):
        convert_keys_to_snake_case(
          val,
          recursive=recursive,
        )
      elif recursive and isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
        for inner_val in val:
          convert_keys_to_snake_case(
            inner_val,
            recursive=recursive,
          )

  return obj


def convert_boolean_values_to_string(
  value_to_convert: Union[dict, list],
  recursive: bool = True,
  ignore_fields: List[str] = None,
  only_fields: List[str] = None,
) -> Union[dict, list]:
  if isinstance(value_to_convert, list):
    if isinstance(value_to_convert[0], str):
      return value_to_convert

    objs = value_to_convert
  else:
    objs = [value_to_convert]

  for obj_dict in objs:
    items = obj_dict.items() if not only_fields else [(f, obj_dict[f]) for f in only_fields if f in obj_dict]
    for key, val in items:
      if isinstance(val, bool):
        if ignore_fields and key in ignore_fields:
          continue

        obj_dict[key] = str(val).lower()
      elif recursive and isinstance(val, dict):
        convert_boolean_values_to_string(
          val,
          recursive=recursive,
          ignore_fields=ignore_fields,
          only_fields=only_fields,
        )
      elif recursive and isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
        for inner_val in val:
          convert_boolean_values_to_string(
            inner_val,
            recursive=recursive,
            ignore_fields=ignore_fields,
            only_fields=only_fields,
          )

  return value_to_convert


def convert_string_values_to_correct_type(
  value_to_convert: Union[dict, list],
  convert_numbers: bool = True,
  convert_booleans: bool = True,
  use_decimal: bool = False,
  recursive: bool = False,
  ignore_fields: List[str] = None,
) -> Union[dict, list]:
  if isinstance(value_to_convert, list):
    if isinstance(value_to_convert[0], str):
      return [convert_string_to_correct_type(val, convert_numbers=convert_numbers, convert_booleans=convert_booleans, use_decimal=use_decimal) for val in value_to_convert]

    objs = value_to_convert
  else:
    objs = [value_to_convert]

  for obj_dict in objs:
    for key, val in obj_dict.items():
      if isinstance(val, str):
        if ignore_fields and key in ignore_fields:
          continue

        obj_dict[key] = convert_string_to_correct_type(val, convert_numbers=convert_numbers, convert_booleans=convert_booleans, use_decimal=use_decimal)
      elif recursive and isinstance(val, dict):
        convert_string_values_to_correct_type(
          val,
          convert_numbers=convert_numbers,
          convert_booleans=convert_booleans,
          use_decimal=use_decimal,
          recursive=recursive,
          ignore_fields=ignore_fields,
        )
      elif recursive and isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
        for inner_val in val:
          convert_string_values_to_correct_type(
            inner_val,
            convert_numbers=convert_numbers,
            convert_booleans=convert_booleans,
            use_decimal=use_decimal,
            recursive=recursive,
            ignore_fields=ignore_fields,
          )

  return value_to_convert


def convert_string_to_correct_type(
  val: str,
  convert_numbers: bool = True,
  convert_booleans: bool = True,
  use_decimal: bool = False,
):
  if convert_numbers and strings.is_number(val, allow_comma=True):
    return strings.convert_to_number(val, use_decimal=use_decimal, remove_commas=True)
  elif convert_booleans and strings.is_boolean(val):
    return strings.convert_to_bool(val)

  return val


def copy_fields(
  from_val: dict,
  to_val: dict,
  fields: List[str],
  field_converter: Callable[[str], str] = None,
  field_converter_map: Dict[str, str] = None,
) -> dict:
  if from_val:
    for field in fields:
      if field in from_val:
        if field_converter is not None:
          to_val[field_converter(field)] = from_val[field]
        elif field_converter_map:
          to_val[field_converter_map.get(field, field)] = from_val[field]
        else:
          to_val[field] = from_val[field]

  return to_val


def find(key: str, obj: dict, yield_parent: bool = False) -> List[dict]:
  if isinstance(obj, dict):
    for k, v in list(obj.items()):
      if k == key:
        if yield_parent:
          yield obj
        else:
          yield v
      else:
        for res in find(key, v, yield_parent):
          yield res
  elif isinstance(obj, list):
    for d in obj:
      for res in find(key, d, yield_parent):
        yield res


def create_key_getter(key: Union[str, Callable[[T], Any]], is_dict: bool = True) -> Callable[[T], Any]:
  if isinstance(key, str):

    if is_dict:

      def key_getter(x):
        return x.get(key)
    else:

      def key_getter(x):
        return getattr(x, key)

  else:
    key_getter = key

  return key_getter


def find_first_with_key_value(list_of_dicts: List[dict], key: Union[str, Callable[[dict], Any]], expected_value: Any) -> Optional[dict]:
  key_getter = create_key_getter(key)

  for val in list_of_dicts:
    field_value = key_getter(val)
    if field_value == expected_value:
      return val


def group_by(list_of_dicts: List[T], key: Union[str, Callable[[T], Any]], is_dict: bool = True) -> Dict[Any, List[T]]:
  key_getter = create_key_getter(key, is_dict=is_dict)
  by_field: Dict[str, List[T]] = {}
  for val in list_of_dicts:
    field_value = key_getter(val)
    if field_value not in by_field:
      by_field[field_value] = []

    by_field[field_value].append(val)

  return by_field


def modify_dict_fields(
  datas: List[dict],
  fields_included: Sequence[str] = None,
  fields_order: Sequence[str] = None,
  in_place: bool = False,
) -> List[dict]:
  result: List[dict] = datas

  if fields_included:

    def fn(updated_data: dict):
      for field in list(updated_data.keys()):
        if field not in fields_included:
          updated_data.pop(field)

    result = modify_list_of_dicts(result, fn, in_place=in_place)

  if fields_order:
    if in_place:
      data_copy = result[0].copy()
      ordered_data = result[0]
      ordered_data.clear()
    else:
      data_copy = result[0].copy()
      ordered_data = dict()

    for field in fields_order:
      ordered_data[field] = data_copy.pop(field, None)

    ordered_data.update(data_copy)
    result[0] = ordered_data

  return result


def prefix_dict_keys(require_prefix: str, data: Dict[str, Any], always_add: str = None) -> dict:
  updated_data = {}
  for input_key, value in data.items():
    key = input_key
    if not key.startswith(require_prefix):
      key = require_prefix + key

    if always_add:
      key = always_add + key

    updated_data[key] = value

  return updated_data


def unique_key_values(list_of_dicts: List[dict], key: Union[str, Callable[[dict], Any]], include_nulls: bool = False) -> List[Any]:
  key_getter = create_key_getter(key)
  unique_values = []
  for val in list_of_dicts:
    field_value = key_getter(val)
    if field_value is None and not include_nulls:
      continue

    if field_value not in unique_values:
      unique_values.append(field_value)

  return unique_values


def remove_nulls(dict_with_nulls: dict) -> dict:
  return {key: val for (key, val) in dict_with_nulls.items() if val is not None}


def remove_nulls_and_empty(dict_with_nulls: dict) -> dict:
  return {key: val for (key, val) in dict_with_nulls.items() if checks.is_not_empty(val)}


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
