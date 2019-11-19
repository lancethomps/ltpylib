#!/usr/bin/env python3

import argparse
import os
from typing import List, Optional, Sequence

import argcomplete
import itertools

from pylib import logs

TRUE_VALUES = ['true', '1', 't', 'yes', 'y']
DEFAULT_POSITIONALS_KEY = 'command'


class PositionalsHelpFormatter(argparse.HelpFormatter):

  def __init__(self,
               prog,
               indent_increment=2,
               max_help_position=24,
               width=None,
               positionals_key: str = DEFAULT_POSITIONALS_KEY):
    super().__init__(prog, indent_increment, max_help_position, width)
    self.positionals_key = positionals_key
    self.positionals_action = argparse._StoreAction([], self.positionals_key, nargs='+')

  def add_usage(self, usage, actions, groups, prefix=None):
    super().add_usage(usage, itertools.chain(actions, [self.positionals_action]), groups, prefix)

  def add_arguments(self, actions):
    if self._current_section.heading == 'positional arguments':
      super().add_arguments(itertools.chain(actions, [self.positionals_action]))
    else:
      super().add_arguments(actions)


def add_default_arguments_to_parser(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
  arg_parser.add_argument('-v', '--verbose', action='store_true')
  arg_parser.add_argument('--dry-run', action='store_true')
  return arg_parser


def check_debug_mode() -> bool:
  return os.getenv('debug_mode', 'false').lower() in TRUE_VALUES


def check_verbose() -> bool:
  return os.getenv('verbose', 'false').lower() in TRUE_VALUES


def create_default_arg_parser() -> argparse.ArgumentParser:
  arg_parser = argparse.ArgumentParser()
  return add_default_arguments_to_parser(arg_parser)


def create_default_with_positionals_arg_parser() -> argparse.ArgumentParser:
  arg_parser = argparse.ArgumentParser(formatter_class=PositionalsHelpFormatter)
  return add_default_arguments_to_parser(arg_parser)


def parse_args(arg_parser: argparse.ArgumentParser, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
  argcomplete.autocomplete(arg_parser)
  args = arg_parser.parse_args(args=argv)
  return args


def parse_args_and_init_others(arg_parser: argparse.ArgumentParser, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
  args = parse_args(arg_parser, argv=argv)
  logs.init_logging(args=args)
  return args


def parse_args_with_positionals_and_init_others(arg_parser: argparse.ArgumentParser, positionals_key: str = DEFAULT_POSITIONALS_KEY,
                                                argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
  argcomplete.autocomplete(arg_parser)
  args, positionals = arg_parser.parse_known_intermixed_args(args=argv)
  args.__setattr__(positionals_key, positionals)
  logs.init_logging(args=args)
  return args


class BaseArgs(object):

  def __init__(self, args: argparse.Namespace):
    self._args: argparse.Namespace = args
    self.verbose: bool = args.verbose
    self.dry_run: bool = args.dry_run


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
