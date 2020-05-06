#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from typing import Callable, List, Optional, Sequence

TRUE_VALUES = ['true', '1', 't', 'yes', 'y']
DEFAULT_POSITIONALS_KEY = 'command'


class PositionalsHelpFormatter(argparse.HelpFormatter):

  def __init__(
    self,
    prog,
    indent_increment=2,
    max_help_position=24,
    width=None,
    positionals_key: str = DEFAULT_POSITIONALS_KEY,
  ):
    super().__init__(prog, indent_increment, max_help_position, width)
    self.positionals_key = positionals_key
    self.positionals_action = argparse._StoreAction([], self.positionals_key, nargs='+')

  def add_usage(self, usage, actions, groups, prefix=None):
    from itertools import chain

    super().add_usage(usage, chain(actions, [self.positionals_action]), groups, prefix)

  def add_arguments(self, actions):
    from itertools import chain

    if self._current_section.heading == 'positional arguments':
      super().add_arguments(chain(actions, [self.positionals_action]))
    else:
      super().add_arguments(actions)


class ActionValidatePath(argparse.Action):

  def __init__(self, option_strings, dest, type=None, **kwargs):
    if type is not None:
      raise ValueError("type not allowed")
    super(ActionValidatePath, self).__init__(option_strings, dest, type=Path, **kwargs)

  def __call__(self, parser, namespace, values: List[Path], option_string=None):
    setattr(namespace, self.dest, values)

    if values:
      for item in values:
        if not item.exists():
          raise ValueError("Supplied Path does not exist: %s" % (item.as_posix()))


class ActionValidatePathAppend(argparse._AppendAction):

  def __init__(self, option_strings, dest, type=None, **kwargs):
    if type is not None:
      raise ValueError("type not allowed")
    super(ActionValidatePathAppend, self).__init__(option_strings, dest, type=Path, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None):
    super(ActionValidatePathAppend, self).__call__(parser, namespace, values, option_string=option_string)

    items: List[List[Path]] = getattr(namespace, self.dest, None)
    if items and items[0]:
      for item in items[0]:
        if not item.exists():
          raise ValueError("Supplied Path does not exist: %s" % (item.as_posix()))


class BaseArgs(object):

  def __init__(self, args: argparse.Namespace):
    self._args: argparse.Namespace = args
    self.debug: bool = args.dry_run
    self.dry_run: bool = args.dry_run
    self.verbose: bool = args.verbose


class ColorArgs(object):

  def __init__(self, args: argparse.Namespace):
    self.no_color: bool = args.no_color
    self.use_color: bool = args.use_color

  def should_use_color(self, default: bool = True) -> bool:
    if self.use_color:
      return True

    if self.no_color:
      return False

    return default

  @staticmethod
  def add_arguments_to_parser(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    arg_parser.add_argument('--no-color', action='store_true')
    arg_parser.add_argument('--use-color', action='store_true')
    return arg_parser


class IncludeExcludeCmdArgs(object):

  def __init__(self, args: argparse.Namespace):
    self.exclude_commands: List[str] = args.exclude_cmd or []
    self.include_commands: List[str] = args.include_cmd or []

  @staticmethod
  def add_arguments_to_parser(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    arg_parser.add_argument('--exclude-cmd', action='append')
    arg_parser.add_argument('--include-cmd', action='append')
    return arg_parser


class IncludeExcludeRegexArgs(object):

  def __init__(self, args: argparse.Namespace):
    self.exclude_regex: List[str] = args.exclude_regex or []
    self.include_regex: List[str] = args.include_regex or []

  @staticmethod
  def add_arguments_to_parser(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    arg_parser.add_argument('--exclude-regex', action='append')
    arg_parser.add_argument('--include-regex', action='append')
    return arg_parser


class PagerArgs(object):

  def __init__(self, args: argparse.Namespace):
    self.no_pager: bool = args.no_pager
    self.pager: str = args.pager
    self.use_pager: bool = args.use_pager

  def should_use_pager(self, default: bool = True) -> bool:
    if self.use_pager:
      return True

    if self.no_pager:
      return False

    return default

  @staticmethod
  def add_arguments_to_parser(arg_parser: argparse.ArgumentParser, default_pager: str = None) -> argparse.ArgumentParser:
    arg_parser.add_argument('--no-pager', action='store_true')
    arg_parser.add_argument('--pager', default=default_pager if default_pager else os.getenv('PAGER', 'less'))
    arg_parser.add_argument('--use-pager', action='store_true')
    return arg_parser


def add_default_arguments_to_parser(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
  arg_parser.add_argument('-v', '--verbose', action='store_true')
  arg_parser.add_argument('--dry-run', "--debug", action='store_true')
  return arg_parser


def check_debug_mode() -> bool:
  return os.getenv('debug_mode', 'false').lower() in TRUE_VALUES


def check_verbose() -> bool:
  return os.getenv('verbose', 'false').lower() in TRUE_VALUES


def create_default_arg_parser() -> argparse.ArgumentParser:
  arg_parser = argparse.ArgumentParser()
  return add_default_arguments_to_parser(arg_parser)


def create_default_with_positionals_arg_parser(positionals_key: str = DEFAULT_POSITIONALS_KEY) -> argparse.ArgumentParser:
  import functools

  arg_parser = argparse.ArgumentParser(formatter_class=functools.partial(PositionalsHelpFormatter, positionals_key=positionals_key))
  return add_default_arguments_to_parser(arg_parser)


def parse_args(arg_parser: argparse.ArgumentParser, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
  import argcomplete

  argcomplete.autocomplete(arg_parser)
  args = arg_parser.parse_args(args=argv)
  return args


def parse_args_and_init_others(arg_parser: argparse.ArgumentParser, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
  from ltpylib.logs import init_logging

  args = parse_args(arg_parser, argv=argv)
  init_logging(args=args)
  return args


def parse_args_with_positionals_and_init_others(
    arg_parser: argparse.ArgumentParser,
    positionals_key: str = None,
    argv: Optional[Sequence[str]] = None,
    positionals_type: Callable = None,
) -> argparse.Namespace:
  import argcomplete
  import functools
  from ltpylib.logs import init_logging

  argcomplete.autocomplete(arg_parser)
  args, positionals = arg_parser.parse_known_intermixed_args(args=argv)

  if positionals_key is None:
    if isinstance(arg_parser.formatter_class, PositionalsHelpFormatter):
      help_formatter: PositionalsHelpFormatter = arg_parser.formatter_class
      positionals_key = help_formatter.positionals_key
    elif isinstance(arg_parser.formatter_class, functools.partial):
      help_formatter: functools.partial = arg_parser.formatter_class
      positionals_key = help_formatter.keywords.get("positionals_key")
    else:
      positionals_key = DEFAULT_POSITIONALS_KEY

  if positionals_type is not None:
    positionals = [positionals_type(arg) for arg in positionals]

  args.__setattr__(positionals_key, positionals)
  init_logging(args=args)
  return args


def does_stdin_have_data() -> bool:
  import sys
  import select

  if select.select([sys.stdin], [], [], 0.0)[0]:
    return True
  elif sys.stdin.isatty():
    return True
  else:
    return False


def check_command(cmd: str) -> bool:
  import shutil

  return shutil.which(cmd) is not None


def check_for_debug_and_log_args(args: BaseArgs, exit_code: int = 0):
  if args.dry_run:
    log_args(args)
    exit(exit_code)


def log_args(args: BaseArgs, only_keys: List[str] = None, skip_keys: List[str] = None):
  import logging
  from ltpylib.logs import log_with_title_sep

  for item in sorted(args.__dict__.items()):
    if item[0] == '_args':
      continue
    elif only_keys and not item[0] in only_keys:
      continue
    elif skip_keys and item[0] in skip_keys:
      continue

    log_with_title_sep(logging.INFO, item[0], item[1])
