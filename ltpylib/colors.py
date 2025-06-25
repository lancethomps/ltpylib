#!/usr/bin/env python


class TermColors:
  BLACK = '\033[1;30m'
  BLUE = '\033[1;34m'
  BOLD = '\033[1m'
  CYAN = '\033[1;36m'
  ENDC = '\033[0m'
  GREEN = '\033[1;32m'
  HEADER = '\033[95m'
  BOLD_BLUE = '\033[0;34m'
  BOLD_CYAN = '\033[0;36m'
  BOLD_GREEN = '\033[0;32m'
  BOLD_PURPLE = '\033[0;35m'
  BOLD_RED = '\033[0;31m'
  BOLD_YELLOW = '\033[0;33m'
  PURPLE = '\033[1;35m'
  RED = '\033[1;31m'
  UNDERLINE = '\033[4m'
  WHITE = '\033[1;37m'
  YELLOW = '\033[1;33m'


def black(value: str) -> str:
  return TermColors.BLACK + value + TermColors.ENDC


def blue(value: str) -> str:
  return TermColors.BLUE + value + TermColors.ENDC


def bold(value: str) -> str:
  return TermColors.BOLD + value + TermColors.ENDC


def cyan(value: str) -> str:
  return TermColors.CYAN + value + TermColors.ENDC


def green(value: str) -> str:
  return TermColors.GREEN + value + TermColors.ENDC


def bold_blue(value: str) -> str:
  return TermColors.BOLD_BLUE + value + TermColors.ENDC


def bold_cyan(value: str) -> str:
  return TermColors.BOLD_CYAN + value + TermColors.ENDC


def bold_green(value: str) -> str:
  return TermColors.BOLD_GREEN + value + TermColors.ENDC


def bold_purple(value: str) -> str:
  return TermColors.BOLD_PURPLE + value + TermColors.ENDC


def bold_red(value: str) -> str:
  return TermColors.BOLD_RED + value + TermColors.ENDC


def bold_yellow(value: str) -> str:
  return TermColors.BOLD_YELLOW + value + TermColors.ENDC


def purple(value: str) -> str:
  return TermColors.PURPLE + value + TermColors.ENDC


def red(value: str) -> str:
  return TermColors.RED + value + TermColors.ENDC


def underline(value: str) -> str:
  return TermColors.UNDERLINE + value + TermColors.ENDC


def white(value: str) -> str:
  return TermColors.WHITE + value + TermColors.ENDC


def yellow(value: str) -> str:
  return TermColors.YELLOW + value + TermColors.ENDC
