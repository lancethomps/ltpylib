#!/usr/bin/env python3
# pylint: disable=C0111
import re
from typing import Union


def replace_matches(content: str, search_string: str, replacement: str, quote_replacement: Union[bool, str] = False) -> str:
  if isinstance(quote_replacement, str):
    quote_replacement = quote_replacement.lower() in ['true', '1', 't', 'y', 'yes']

  if quote_replacement:
    replacement = re.escape(replacement)

  return re.sub(search_string, replacement, content)


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
