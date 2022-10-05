#!/usr/bin/env python
import re
from decimal import Decimal
from typing import List, Match, Union

BOOLEAN_STRINGS_FALSE = frozenset([
  "no",
  "n",
  "false",
])
BOOLEAN_STRINGS_TRUE = frozenset([
  "yes",
  "y",
  "true",
])

CAMEL_CASE_CAP_CHARS_REGEX = re.compile(r"(?<=[a-z])([A-Z0-9])|(?<=[^0-9])([A-Z])(?=[a-z])")
CASE_CONVERSION_IGNORE_REGEX = re.compile(r"[']")
MULTI_SPACE_REGEX = re.compile(r"\s+")
NON_ALPHA_NUMERIC_REGEX = re.compile(r"[^a-zA-Z0-9]")


def camel_case_to_title_case(val: str):
  val = val[:1].upper() + val[1:]
  return " ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', val))


def convert_to_bool(val: str, check_if_valid: bool = False, unknown_value: bool = None) -> Union[bool, str, None]:
  if val is None:
    return None

  if check_if_valid and not is_boolean(val):
    return val

  lower_val = val.lower()

  if lower_val in BOOLEAN_STRINGS_FALSE:
    return False
  elif lower_val in BOOLEAN_STRINGS_TRUE:
    return True
  elif unknown_value is not None:
    return unknown_value

  raise ValueError("String is not a boolean: " % val)


def convert_to_number(
  val: str,
  check_if_valid: bool = False,
  float_only: bool = False,
  use_decimal: bool = False,
  remove_commas: bool = False,
) -> Union[int, float, str, None]:
  if val is None:
    return None

  if check_if_valid and not is_number(val, allow_comma=remove_commas):
    return val

  if remove_commas:
    val = val.replace(",", "")

  if float_only:
    return Decimal(val) if use_decimal else float(val)

  try:
    return int(val)
  except ValueError:
    return Decimal(val) if use_decimal else float(val)


def is_boolean(val: str) -> bool:
  if not val:
    return False

  return val.lower() in BOOLEAN_STRINGS_FALSE or val.lower() in BOOLEAN_STRINGS_TRUE


def is_number(val: str, allow_comma: bool = False) -> bool:
  if not val:
    return False

  if val.isdigit():
    return True

  val = val.replace(".", "", 1)
  if val.isdigit():
    return True

  if val.startswith("-") and val.replace("-", "", 1).isdigit():
    return True

  if allow_comma and val.replace(",", "").isdigit():
    return True

  return False


def maybe_json_string(val: str) -> bool:
  if not val:
    return False

  if val.startswith("[") and val.endswith("]"):
    return True

  return val.startswith("{") and val.endswith("}")


def str_list_max_length(values: List[str]) -> int:
  return len(max(values, key=len))


def strip_color_codes(val: str) -> str:
  return re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]", "", val)


def substring_after(val: str, before_str: str) -> str:
  return val.split(before_str, 1)[1]


def substring_before(val: str, before_str: str) -> str:
  return val.split(before_str)[0]


def _to_snake_case_replacer(match: Match) -> str:
  return " " + "".join([val for val in match.group(1, 2) if val is not None])


def to_snake_case(val: str) -> str:
  val = CASE_CONVERSION_IGNORE_REGEX.sub("", val)

  val = NON_ALPHA_NUMERIC_REGEX.sub(" ", val)

  val = CAMEL_CASE_CAP_CHARS_REGEX.sub(_to_snake_case_replacer, val)

  return MULTI_SPACE_REGEX.sub("_", val.lower().strip())


def truncate_if_needed(val: str, max_length: int, include_ellipsis: bool = True) -> str:
  if val and len(val) > max_length:
    return (val[:max_length] + "..") if include_ellipsis else val[:max_length]

  return val


def _main():
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)


if __name__ == "__main__":
  try:
    _main()
  except KeyboardInterrupt:
    exit(130)
