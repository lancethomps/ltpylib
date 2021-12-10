#!/usr/bin/env python
import os
import tempfile
from pathlib import Path
from typing import Tuple, Union

from ltpylib import files, procs
from ltpylib.files import convert_to_path


def diff_git(
  initial: str,
  updated: str,
  add_suffix: str = None,
  context_lines: int = None,
  color: str = "always",
) -> Tuple[str, bool]:
  suffix_prefix = ("." + add_suffix) if add_suffix else ""

  ifd, initial_temp_file = tempfile.mkstemp(suffix=suffix_prefix + ".initial")
  ufd, updated_temp_file = tempfile.mkstemp(suffix=suffix_prefix + ".updated")
  os.close(ifd)
  os.close(ufd)

  files.write_file(initial_temp_file, initial)
  files.write_file(updated_temp_file, updated)

  try:
    return diff_git_files(initial_temp_file, updated_temp_file, context_lines=context_lines, color=color)
  finally:
    os.remove(initial_temp_file)
    os.remove(updated_temp_file)


def diff_git_files(
  initial_file: Union[Path, str],
  updated_file: Union[Path, str],
  context_lines: int = None,
  color: str = "always",
) -> Tuple[str, bool]:
  initial_file = convert_to_path(initial_file)
  updated_file = convert_to_path(updated_file)

  command = [
    "git",
    "diff",
    "--no-index",
    "-w",
  ]

  if color:
    command.append("--color=%s" % color)

  if context_lines is not None:
    command.append("--unified=%s" % str(context_lines))

  command.extend([initial_file, updated_file])
  result = procs.run(
    command,
    check=False,
  )
  return result.stdout, result.returncode == 1
