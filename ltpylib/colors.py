#!/usr/bin/env python
import io
import logging
import os
import sys
from functools import cache
from typing import Iterable


class TermColors:
  BLACK = 0
  BLUE = 4
  CYAN = 6
  GREEN = 2
  PURPLE = 5
  RED = 1
  WHITE = 7
  YELLOW = 3


class TermAttr:
  BOLD = 0
  DARK = 2
  UNDERLINE = 4
  BLINK = 5
  REVERSE = 7
  CONCEALED = 8
  STRIKE = 9


RESET = '\033[0m'
DEFAULT_ATTRS = frozenset([1])


def colored(
  color: int | tuple[int, int, int],
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  result = str(value)
  if not can_colorize(no_color=no_color, force_color=force_color):
    return result

  fmt_str = '\033[%dm%s'
  rgb_fore_fmt_str = '\033[38;2;%d;%d;%dm%s'
  rgb_back_fmt_str = '\033[48;2;%d;%d;%dm%s'

  if color is not None:
    if isinstance(color, int):
      result = fmt_str % (30 + color, result)
    elif isinstance(color, tuple):
      result = rgb_fore_fmt_str % (color[0], color[1], color[2], result)

  if on_color is not None:
    if isinstance(on_color, int):
      result = fmt_str % (40 + on_color, result)
    elif isinstance(on_color, tuple):
      result = rgb_back_fmt_str % (on_color[0], on_color[1], on_color[2], result)

  if 0 not in attrs and 1 not in attrs:
    attrs = [1] + list(attrs)

  for attr in attrs:
    result = fmt_str % (attr, result)

  return result + RESET


def black(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.BLACK, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def blue(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.BLUE, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def cyan(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.CYAN, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def green(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.GREEN, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def purple(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.PURPLE, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def red(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.RED, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def white(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.WHITE, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def yellow(
  value: object,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> str:
  return colored(TermColors.YELLOW, value, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_colored(
  color: int | tuple[int, int, int],
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  logging.log(level, colored(color, str(msg) % args if args else msg, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color))


def log_black(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.BLACK, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_blue(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.BLUE, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_cyan(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.CYAN, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_green(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.GREEN, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_purple(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.PURPLE, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_red(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.RED, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_white(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.WHITE, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


def log_yellow(
  msg: object,
  *args: object,
  level: int = logging.INFO,
  on_color: int | tuple[int, int, int] | None = None,
  attrs: Iterable[int] = DEFAULT_ATTRS,
  no_color: bool | None = None,
  force_color: bool | None = None,
):
  log_colored(TermColors.YELLOW, msg, *args, level=level, on_color=on_color, attrs=attrs, no_color=no_color, force_color=force_color)


@cache
def can_colorize(
  *,
  no_color: bool | None = None,
  force_color: bool | None = None,
) -> bool:
  # First check overrides:
  if no_color is not None and no_color:
    return False
  if force_color is not None and force_color:
    return True

  # Then check env vars:
  if os.environ.get("ANSI_COLORS_DISABLED"):
    return False
  if os.environ.get("NO_COLOR"):
    return False
  if os.environ.get("FORCE_COLOR"):
    return True

  # Then check system:
  if os.environ.get("TERM") == "dumb":
    return False
  if not hasattr(sys.stdout, "fileno"):
    return False

  try:
    return os.isatty(sys.stdout.fileno())
  except io.UnsupportedOperation:
    return sys.stdout.isatty()
