#!/usr/bin/env python3
# pylint: disable=C0111
import re
from pathlib import Path
from typing import List, Union

from ltpylib import files


def replace_matches(content: str, search_string: str, replacement: str, quote_replacement: Union[bool, str] = False) -> str:
  if isinstance(quote_replacement, str):
    quote_replacement = quote_replacement.lower() in ['true', '1', 't', 'y', 'yes']

  if quote_replacement:
    replacement = re.escape(replacement)

  return re.sub(search_string, replacement, content)


def pull_matches_from_file(
    file: Union[str, Path],
    search_string: str,
    group: int = 0,
    flags: Union[int, re.RegexFlag] = 0
) -> List[str]:
  content = files.read_file(file)

  matches: List[str] = []
  for match in re.finditer(search_string, content, flags=flags):
    matches.append(match.group(group))

  return matches


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
