#!/usr/bin/env python
# pylint: disable=C0111
import re
from pathlib import Path
from typing import Callable, List, Match, Sequence, Union


def join_by_regex_or(parts: Sequence[str]) -> str:
  return "(" + "|".join(parts) + ")"


def replace_matches(
  content: str,
  search_string: Union[str, re.Pattern],
  replacement: Union[str, Callable[[Match], str]],
  quote_replacement: Union[bool, str] = False,
  wrap_replacement_in_function: bool = False,
  flags: Union[int, re.RegexFlag] = 0,
) -> str:
  if isinstance(quote_replacement, str):
    quote_replacement = quote_replacement.lower() in ['true', '1', 't', 'y', 'yes']

  if quote_replacement and isinstance(replacement, str):
    replacement = re.escape(replacement)
  elif wrap_replacement_in_function and isinstance(replacement, str):
    replacement_content = replacement

    def replacement_function(match: Match) -> str:
      return replacement_content

    replacement = replacement_function

  return re.sub(search_string, replacement, content, flags=flags)


def pull_matches_from_file(
  file: Union[str, Path],
  search_string: Union[str, re.Pattern],
  group: int = 0,
  flags: Union[int, re.RegexFlag] = 0,
) -> List[str]:
  from ltpylib import files

  content = files.read_file(file)

  matches: List[str] = []
  for match in re.finditer(search_string, content, flags=flags):
    matches.append(match.group(group))

  return matches


def regex_match(val: str, patterns: List[Union[str, re.Pattern]]) -> bool:
  for pattern in patterns:
    if re.fullmatch(pattern, val):
      return True

  return False


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
