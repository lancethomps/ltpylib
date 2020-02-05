#!/usr/bin/env python3
# pylint: disable=C0111
import inspect
from typing import ClassVar, List


def get_functions_of_class(
    inspect_class: ClassVar,
    include_private: bool = False,
    include_signature: bool = False
) -> List[str]:
  result: List[str] = []
  functions = inspect.getmembers(inspect_class, predicate=inspect.isfunction)
  for func in functions:
    if not include_private and func[0].startswith("_"):
      continue

    func_info: str = func[0]

    if include_signature:
      func_sig: str = str(inspect.signature(func[1])).replace("(self, ", "(", 1)
      func_info += func_sig

    result.append(func_info)

  return result
