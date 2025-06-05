#!/usr/bin/env python

import logging
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Union

from ltpylib import files, procs

SHEBANG_REGEX = re.compile(r"^#!(.*)$")
FILE_EXT_MAPPINGS = {
  "jsonl": "json",
  "json5": "json",
  "lookml": "yaml",
  "py": "python",
  "rb": "ruby",
  "sh": "bash",
  "yml": "yaml",
}
FILE_NAME_MAPPINGS = {
  "Gemfile": "ruby",
}


def prettify(
  files_to_prettify: Union[Path, List[Path]],
  file_type: str = None,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
  read_shebang_if_necessary: bool = True,
):
  if not isinstance(files_to_prettify, list):
    files_to_prettify = [files_to_prettify]

  for file in files_to_prettify:
    if file_type:
      single_file_type = file_type
    else:
      single_file_type = FILE_EXT_MAPPINGS.get(file.suffix[1:], file.suffix[1:])
      if not single_file_type and read_shebang_if_necessary:
        single_file_type = read_file_shebang(file)

      if not single_file_type:
        single_file_type = FILE_NAME_MAPPINGS.get(file.name, None)

    if not single_file_type:
      raise ValueError("Could not determine file type: file=%s" % file.as_posix())

    func_for_type = globals()["prettify_" + single_file_type + "_file"]
    if not callable(func_for_type):
      raise ValueError("Unsupported file type: file=%s type=%s" % (file.as_posix(), single_file_type))

    func_for_type(file, compact=compact, debug_mode=debug_mode, verbose=verbose)
    if verbose:
      logging.debug("Updated %s", file.as_posix())


def prettify_bash_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  formatter_args = [
    "shfmt",
    "--simplify",
    "--indent",
    "2",
    "--case-indent",
    "--write",
  ]

  if compact:
    formatter_args.append("--minify")

  formatter_args.append(file.as_posix())

  run_formatter(
    file,
    formatter_args,
    debug_mode=debug_mode,
    verbose=verbose,
    use_run_with_regular_stdout=True,
    should_have_stdout=False,
  )


def prettify_html_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  formatter_path = "/usr/bin/tidy" if Path("/usr/bin/tidy").exists() else "tidy"
  formatter_args = [
    formatter_path,
    "-icm",
    "-wrap",
    "200",
    "--doctype",
    "omit",
    "--indent",
    "yes",
    "--vertical-space",
    "no",
  ]

  if not verbose:
    formatter_args.extend([
      "-quiet",
      "--show-warnings",
      "no",
    ])

  formatter_args.append(file.as_posix())

  run_formatter(
    file,
    formatter_args,
    debug_mode=debug_mode,
    verbose=verbose,
    use_run_with_regular_stdout=True,
    should_have_stdout=False,
    allow_exit_codes=[0, 1],
  )


def prettify_json_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  jq_args = ["--sort-keys", ".", file.as_posix()]
  if compact:
    jq_args.insert(0, "--compact-output")

  result = run_formatter(
    file,
    ["jq"] + jq_args,
    debug_mode=debug_mode,
    verbose=verbose,
  )
  files.write_file(file, result.stdout)


def prettify_python_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  formatter_args = [
    "yapf",
    "--in-place",
    "--recursive",
  ]
  yapf_style_home_file = Path.home().joinpath(".style.yapf")
  if yapf_style_home_file.is_file():
    formatter_args.extend([
      "--style",
      yapf_style_home_file.as_posix(),
    ])

  formatter_args.append(file.as_posix())
  run_formatter(
    file,
    formatter_args,
    debug_mode=debug_mode,
    verbose=verbose,
    should_have_stdout=False,
    use_run_with_regular_stdout=True,
  )


def prettify_ruby_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  formatter_args = [
    "standardrb",
    "--fix",
    "--",
    file.as_posix(),
  ]

  run_formatter(
    file,
    formatter_args,
    debug_mode=debug_mode,
    verbose=verbose,
    should_have_stdout=False,
    use_run_with_regular_stdout=True,
  )


def prettify_sql_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  formatter_args = [
    "sql-formatter",
    "--language",
    "sqlite",
    "--config",
    Path.home().joinpath(".config/sql-formatter/sqlite.json").as_posix(),
    "--output",
    file.as_posix(),
    file.as_posix(),
  ]
  run_formatter(
    file,
    formatter_args,
    debug_mode=debug_mode,
    verbose=verbose,
    use_run_with_regular_stdout=True,
  )


def prettify_xml_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  result = run_formatter(
    file,
    ["xmllint", "--format", file.as_posix()],
    debug_mode=debug_mode,
    verbose=verbose,
  )
  files.write_file(file, result.stdout)


def prettify_yaml_file(
  file: Path,
  compact: bool = False,
  debug_mode: bool = False,
  verbose: bool = False,
):
  result = run_formatter(
    file,
    ["yq", "--yaml-roundtrip", "--indentless-lists", "--sort-keys", "--width=5000", ".", file.as_posix()],
    debug_mode=debug_mode,
    verbose=verbose,
  )
  files.write_file(file, result.stdout)


def run_formatter(
  file: Path,
  formatter_args: List[str],
  debug_mode: bool = False,
  verbose: bool = False,
  use_run_with_regular_stdout: bool = False,
  should_have_stdout: bool = True,
  allow_exit_codes: List[int] = None,
) -> subprocess.CompletedProcess:
  result = check_proc_result(
    file,
    procs.run_with_regular_stdout(formatter_args, log_cmd=verbose) if use_run_with_regular_stdout else procs.run(formatter_args, log_cmd=verbose),
    should_have_stdout=should_have_stdout,
    allow_exit_codes=allow_exit_codes,
  )
  return result


def check_proc_result(
  file: Path,
  result: subprocess.CompletedProcess,
  should_have_stdout: bool = True,
  allow_exit_codes: List[int] = None,
) -> subprocess.CompletedProcess:
  exit_code = result.returncode
  proc_succeeded = exit_code == 0
  if allow_exit_codes and exit_code in allow_exit_codes:
    proc_succeeded = True

  if should_have_stdout and not result.stdout:
    raise Exception("Issue prettifying file: file=%s status=%s stderr=%s" % (file.as_posix(), exit_code, result.stderr))

  if result.stderr:
    if proc_succeeded:
      logging.warning(result.stderr)
    else:
      raise Exception("Issue prettifying file: file=%s status=%s stderr=%s stdout=%s" % (file.as_posix(), exit_code, result.stderr, result.stderr))

  if not proc_succeeded:
    result.check_returncode()

  return result


def read_file_shebang(file: Path) -> Optional[str]:
  if file.is_file():
    file_lines = files.read_file_n_lines(file, n_lines=1)
    if file_lines and len(file_lines) >= 1:
      first_line = file_lines[0]
      match = SHEBANG_REGEX.fullmatch(first_line)
      if match:
        full_command = match.group(1)
        command_parts = full_command.split(" ")

        shebang_file_type = ""
        if len(command_parts) == 1 or not command_parts[0].endswith("env"):
          shebang_file_type = Path(command_parts[0]).name
        else:
          shebang_file_type = command_parts[1]

        logging.debug("Resolved file type from shebang: file=%s type=%s first_line=%s", file.as_posix(), shebang_file_type, first_line)
        return shebang_file_type
      else:
        logging.debug("Shebang regex did not match: file=%s regex=%s first_line=%s", file.as_posix(), SHEBANG_REGEX, first_line)
    else:
      logging.debug("File is empty: file=%s", file.as_posix())
