#!/usr/bin/env python3
# pylint: disable=C0111

import re
import urllib.parse
from typing import Callable

StrConverter = Callable[[str], str]


def stripper(val: str) -> str:
  return val.strip()


def lower_case(val: str) -> str:
  return val.lower()


def alphanum_only(val: str) -> str:
  return re.sub(r'[^a-zA-Z0-9]', '', val)


def url_encode(val: str) -> str:
  return urllib.parse.quote_plus(val)


def url_decode(val: str) -> str:
  return urllib.parse.unquote_plus(val)


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
