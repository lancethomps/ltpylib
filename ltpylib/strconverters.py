#!/usr/bin/env python
# pylint: disable=C0111

import re
import urllib.parse as urllib_parse
from typing import Callable, List, Union

StrConverter = Callable[[str], str]

SEARCH_SEP_CHARS: List[str] = [
  " ",
  "_",
  "-",
  ".",
]


def stripper(val: str) -> str:
  return val.strip()


def lower_case(val: str) -> str:
  return val.lower()


def alphanum_only(val: str) -> str:
  return re.sub(r'[^a-zA-Z0-9]', '', val)


def num_only(val: str) -> str:
  return re.sub(r'[^0-9.]', '', val)


def url_encode(val: str, safe: Union[bytes, str] = "") -> str:
  return urllib_parse.quote_plus(val, safe=safe)


def url_decode(val: str) -> str:
  return urllib_parse.unquote_plus(val)


def dict_to_url_params(params: dict, safe: str = "") -> str:
  return urllib_parse.urlencode(params, safe=safe)


def to_camel_case(val: str, sep: str = None) -> str:
  if not val:
    return val

  if sep is None:
    sep = find_sep_char(val)

  val = re.sub(r'[^a-zA-Z0-9 ]', ' ', val.lower().replace(sep, " ")).title()
  return (val[0:1].lower() + val[1:]).replace(" ", "")


def to_snake_case(val: str, sep: str = None) -> str:
  if not val:
    return val

  if sep is None:
    sep = find_sep_char(val)

  val = re.sub(r'[^a-zA-Z0-9 ]', ' ', val.lower().replace(sep, " "))
  return "_".join(val.lower().split())


def find_sep_char(val: str) -> str:
  if val.count(" ") > 0:
    return " "

  sep = ""
  count: int = -1
  for sep_char in SEARCH_SEP_CHARS:
    sep_char_count = val.count(sep_char)
    if sep_char_count > count:
      count = sep_char_count
      sep = sep_char

  return sep


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
