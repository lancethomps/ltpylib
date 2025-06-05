#!/usr/bin/env python
# pylint: disable=C0111
from typing import Any, Sequence


def check_command(cmd: str) -> bool:
  import shutil

  return shutil.which(cmd) is not None


def is_empty(val) -> bool:
  if val is None:
    return True

  if isinstance(val, (dict, list)):
    return not val

  return False


def is_not_empty(val) -> bool:
  return not is_empty(val)


def is_any_value_present(check: Sequence[Any], values: Sequence[Any]) -> bool:
  if not check or not values:
    return False

  for val in values:
    if val in check:
      return True

  return False
