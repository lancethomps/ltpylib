#!/usr/bin/env python
import os
import tempfile

from ltpylib import files, procs


def diff_git(
  initial: str,
  updated: str,
  add_suffix: str = None,
  context_lines: int = None,
  color: str = "always",
) -> str:
  suffix_prefix = ("." + add_suffix) if add_suffix else ""

  ifd, initial_temp_file = tempfile.mkstemp(suffix=suffix_prefix + ".initial")
  ufd, updated_temp_file = tempfile.mkstemp(suffix=suffix_prefix + ".updated")
  os.close(ifd)
  os.close(ufd)

  files.write_file(initial_temp_file, initial)
  files.write_file(updated_temp_file, updated)

  try:
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

    command.extend([initial_temp_file, updated_temp_file])
    result = procs.run(
      command,
      check=False,
    )
    return result.stdout
  finally:
    os.remove(initial_temp_file)
    os.remove(updated_temp_file)
