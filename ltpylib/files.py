#!/usr/bin/env python3
# pylint: disable=C0111
import os
import re
import subprocess
from collections import OrderedDict
from configparser import ConfigParser
from pathlib import Path
from typing import AnyStr, List, Sequence, Set, Tuple, Union, Pattern, Callable, Match

import itertools

from ltpylib import filters


def replace_matches_in_file(file: Union[str, Path], search_string: str, replacement: Union[str, Callable[[Match], str]], quote_replacement: Union[bool, str] = False, force_replace: bool = False) -> bool:
  if isinstance(quote_replacement, str):
    quote_replacement = quote_replacement.lower() in ['true', '1', 't', 'y', 'yes']

  if quote_replacement and isinstance(replacement, str):
    replacement = re.escape(replacement)

  content = read_file(file)
  content_new = re.sub(search_string, replacement, content)

  if content != content_new:
    write_file(file, content_new)
    return True
  elif force_replace and re.search(search_string, content):
    write_file(file, content_new)
    return True

  return False


def chmod_proc(perms: str, file: Union[str, Path]) -> int:
  if isinstance(file, str):
    file = Path(file)

  return subprocess.call(["chmod", perms, file.as_posix()])


def read_file(file: Union[str, Path]) -> AnyStr:
  if isinstance(file, str):
    file = Path(file)

  with open(file.as_posix(), 'r') as fr:
    content = fr.read()
  return content


def read_file_n_lines(file: Union[str, Path], n_lines: int) -> List[str]:
  if isinstance(file, str):
    file = Path(file)

  lines: List[str] = []
  with open(file.as_posix()) as fr:
    for n in range(n_lines - 1):
      line = fr.readline()
      if not line:
        break
      lines.append(line.rstrip('\n'))

  return lines


def write_file(file: Union[str, Path], contents: AnyStr):
  if isinstance(file, str):
    file = Path(file)

  with open(file.as_posix(), 'w') as fw:
    fw.write(contents)


def append_file(file: Union[str, Path], contents: AnyStr):
  if isinstance(file, str):
    file = Path(file)

  with open(file.as_posix(), 'a') as fw:
    fw.write(contents)


def list_files(dir: Path, globs: List[str] = ('**/*',)) -> List[Path]:
  files: Set[Path] = set()
  file: Path = None
  for file in list(itertools.chain(*[dir.glob(glob) for glob in globs])):
    if file.is_file():
      files.add(file)

  files_list = list(files)
  files_list.sort()
  return files_list


def list_dirs(base_dir: Path, globs: List[str] = ('**/*',)) -> List[Path]:
  dirs: Set[Path] = set()
  child_dir: Path = None
  for child_dir in list(itertools.chain(*[base_dir.glob(glob) for glob in globs])):
    if child_dir.is_dir():
      dirs.add(child_dir)

  dirs_list = list(dirs)
  dirs_list.sort()
  return dirs_list


def read_properties(file: Union[str, Path], use_mock_default_section: bool = True, config: ConfigParser = None) -> ConfigParser:
  if isinstance(file, str):
    file = Path(file)

  if not file.is_file():
    raise ValueError("File does not exist: %s" % file)

  if config is None:
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str

  if use_mock_default_section:
    with open(file.as_posix(), 'r') as configfile:
      config.read_string('[DEFAULT]\n' + configfile.read())
  else:
    config.read(file.as_posix())

  return config


def write_properties(config: ConfigParser, file: Union[str, Path], sort_keys: bool = False):
  if sort_keys:
    if config._defaults:
      config._defaults = OrderedDict(sorted(config._defaults.items(), key=lambda t: t[0]))

    for section in config._sections:
      config._sections[section] = OrderedDict(sorted(config._sections[section].items(), key=lambda t: t[0]))

    config._sections = OrderedDict(sorted(config._sections.items(), key=lambda t: t[0]))

  if isinstance(file, str):
    file = Path(file)

  with open(file.as_posix(), 'w') as configfile:
    config.write(configfile)


def filter_files_with_matching_line(files: List[Union[str, Path]], regexes: List[Union[str, Pattern]], check_n_lines: int = 1) -> List[Path]:
  filtered: List[Path] = []
  for file in files:
    lines = read_file_n_lines(file, check_n_lines)
    has_match = False
    for line in lines:
      for regex in regexes:
        if re.search(regex, line):
          has_match = True
          break

      if has_match:
        break

    if not has_match:
      filtered.append(file)

  return filtered


def find_children(
    base_dir: Union[Path, str],
    break_after_match: bool = False,
    max_depth: int = -1,
    include_dirs: bool = True,
    include_files: bool = True,
    match_absolute_path: bool = False,
    include_patterns: Sequence[str] = None,
    exclude_patterns: Sequence[str] = None,
    includes: Sequence[str] = None,
    excludes: Sequence[str] = None,
    recursion_include_patterns: Sequence[str] = None,
    recursion_exclude_patterns: Sequence[str] = None,
    recursion_includes: Sequence[str] = None,
    recursion_excludes: Sequence[str] = None
) -> List[Path]:
  if isinstance(base_dir, str):
    top = str(base_dir)
  else:
    top = base_dir.as_posix()

  return _find_children(
    top,
    [],
    1,
    break_after_match,
    max_depth,
    include_dirs,
    include_files,
    match_absolute_path,
    include_patterns,
    exclude_patterns,
    includes,
    excludes,
    recursion_include_patterns,
    recursion_exclude_patterns,
    recursion_includes,
    recursion_excludes
  )[1]


def _find_children(
    top: str,
    found_dirs: List[Path],
    current_depth: int,
    break_after_match: bool,
    max_depth: int,
    include_dirs: bool,
    include_files: bool,
    match_absolute_path: bool,
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
    includes: Sequence[str],
    excludes: Sequence[str],
    recursion_include_patterns: Sequence[str],
    recursion_exclude_patterns: Sequence[str],
    recursion_includes: Sequence[str],
    recursion_excludes: Sequence[str]
) -> Tuple[bool, List[Path]]:
  found_match = False
  scandir_it = os.scandir(top)
  dirs = []

  with scandir_it:
    while True:
      try:
        try:
          entry = next(scandir_it)
        except StopIteration:
          break
      except OSError as error:
        return found_match, found_dirs

      try:
        is_dir = entry.is_dir()
      except OSError:
        # If is_dir() raises an OSError, consider that the entry is not
        # a directory, same behaviour than os.path.isdir().
        is_dir = False

      if is_dir and not include_dirs:
        continue
      elif not is_dir and not include_files:
        continue

      child = entry.name
      full_path = os.path.join(top, child)
      test_value = child if not match_absolute_path else full_path
      include = filters.should_include(
        test_value,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        includes=includes,
        excludes=excludes
      )

      if include:
        found_match = True
        found_dirs.append(Path(full_path))
        if break_after_match:
          break

      if is_dir:
        include_child = filters.should_include(
          test_value,
          include_patterns=recursion_include_patterns,
          exclude_patterns=recursion_exclude_patterns,
          includes=recursion_includes,
          excludes=recursion_excludes
        )
        if include_child:
          dirs.append(child)

  if (max_depth <= -1 or current_depth < max_depth) and (not found_match or not break_after_match):
    for dirname in dirs:
      _find_children(
        os.path.join(top, dirname),
        found_dirs,
        current_depth + 1,
        break_after_match,
        max_depth,
        include_dirs,
        include_files,
        match_absolute_path,
        include_patterns,
        exclude_patterns,
        includes,
        excludes,
        recursion_include_patterns,
        recursion_exclude_patterns,
        recursion_includes,
        recursion_excludes
      )

  return found_match, found_dirs


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
