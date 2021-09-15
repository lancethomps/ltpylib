#!/usr/bin/env python
import argparse
import logging
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Union

from ltpylib import opts

LOG_FORMAT_PART_LEVEL = "{levelname:<8}"
LOG_FORMAT_PART_MESSAGE = "{message}"
LOG_FORMAT_PART_TIMESTAMP = "{asctime}"

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = f"{LOG_FORMAT_PART_MESSAGE}"
DEFAULT_LOG_STYLE = "{"
LOG_SEP = "------------------------------------------------"

LOG_FORMAT_WITH_LEVEL = f"{LOG_FORMAT_PART_LEVEL} {LOG_FORMAT_PART_MESSAGE}"
LOG_FORMAT_WITH_TIMESTAMP = f"[{LOG_FORMAT_PART_TIMESTAMP}] {LOG_FORMAT_PART_MESSAGE}"


class LogPipe(threading.Thread):

  def __init__(self, level: int = logging.INFO):
    """Setup the object with a logger and a loglevel
    and start the thread
    """
    threading.Thread.__init__(self)
    self.daemon = False
    self.level = level
    self.fdRead, self.fdWrite = os.pipe()
    self.pipeReader = os.fdopen(self.fdRead)
    self.start()

  def fileno(self):
    """Return the write file descriptor of the pipe
    """
    return self.fdWrite

  def run(self):
    """Run the thread, logging everything.
    """
    for line in iter(self.pipeReader.readline, ''):
      logging.log(self.level, line.strip('\n'))

    self.pipeReader.close()

  def close(self):
    """Close the write end of the pipe.
    """
    os.close(self.fdWrite)


class StdoutStreamHandler(logging.StreamHandler):

  def __init__(self):
    super().__init__(stream=sys.stdout)

  def handleError(self, record):
    err_type, err_value, traceback = sys.exc_info()
    if err_type == BrokenPipeError:
      exit(0)

    super().handleError(record)


def init_logging(
  verbose: bool = None,
  quiet: bool = None,
  log_level: Union[int, str] = None,
  log_format: str = None,
  args: Union[argparse.Namespace, opts.BaseArgs] = None,
):
  if args:
    if verbose is None and hasattr(args, "verbose"):
      verbose = args.verbose
    if log_level is None and hasattr(args, "log_level"):
      log_level = args.log_level
    if log_format is None and hasattr(args, "log_format"):
      log_format = args.log_format
    if quiet is None and hasattr(args, "quiet"):
      quiet = args.quiet

  if verbose:
    log_level = logging.DEBUG
  elif quiet:
    log_level = logging.WARNING
  elif log_level is not None:
    log_level = log_level
  elif os.environ.get("log_level") is not None:
    log_level = os.environ.get("log_level")
  else:
    log_level = DEFAULT_LOG_LEVEL

  log_config_kwargs = {
    "style": DEFAULT_LOG_STYLE,
    "handlers": [StdoutStreamHandler()],
  }
  logging.basicConfig(
    level=log_level,
    format=log_format if log_format else DEFAULT_LOG_FORMAT,
    **log_config_kwargs,
  )


def is_debug_enabled():
  return logging.root.isEnabledFor(logging.DEBUG)


def log_sep(debug_only=False):
  if debug_only:
    logging.debug(LOG_SEP)
  else:
    logging.info(LOG_SEP)


def create_path_log_info(path: Path, replace_home_dir: bool = True) -> str:
  output = path.as_posix()

  if replace_home_dir:
    output = output.replace(os.getenv('HOME'), '~', 1)

  return output


def log_with_sep(level: int, msg, *args, **kwargs):
  logging.log(level, LOG_SEP)
  logging.log(level, msg, *args, **kwargs)
  logging.log(level, LOG_SEP)


def log_with_title_sep(level: int, title, msg, *args, **kwargs):
  logging.log(level, title)
  logging.log(level, LOG_SEP)
  logging.log(level, msg, *args, **kwargs)
  logging.log(level, '')


def tail_log_file(file: str, *func_args):
  if shutil.which('multitail'):
    log_cmd = ['multitail']
    mt_conf = Path(os.getenv('DOTFILES') + '/multitail.conf')
    if '-F' not in func_args and mt_conf.is_file():
      log_cmd.extend(['-F', mt_conf.as_posix()])

    if '-CS' not in func_args:
      log_cmd.extend(['-CS', 'l4j'])

    if '-n' not in func_args:
      log_cmd.extend(['-n', '1500'])

  else:
    log_cmd = ['tail', '-1500f']

  if func_args:
    log_cmd.extend(func_args)

  log_cmd.append(file)

  subprocess.check_call(log_cmd, universal_newlines=True)


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
