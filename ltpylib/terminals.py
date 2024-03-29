#!/usr/bin/env python
# flake8: noqa E722
import os
import platform
import shlex
import struct
import subprocess
from typing import Tuple


def get_terminal_size() -> Tuple[int, int]:
  """ getTerminalSize()
   - get width and height of console
   - works on linux,os x,windows,cygwin(windows)
   originally retrieved from:
   http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
  """
  current_os = platform.system()
  tuple_xy = None
  if current_os == 'Windows':
    tuple_xy = _get_terminal_size_windows()
    if tuple_xy is None:
      tuple_xy = _get_terminal_size_tput()
      # needed for window's python in cygwin's xterm!
  if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
    tuple_xy = _get_terminal_size_linux()
  if tuple_xy is None:
    tuple_xy = (200, 25)
  return tuple_xy


def _get_terminal_size_windows():
  try:
    from ctypes import windll, create_string_buffer

    # stdin handle is -10
    # stdout handle is -11
    # stderr handle is -12
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
      (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
      sizex = right - left + 1
      sizey = bottom - top + 1
      return sizex, sizey
  except:
    pass


def _get_terminal_size_tput():
  try:
    cols = int(subprocess.check_call(shlex.split('tput cols')))
    rows = int(subprocess.check_call(shlex.split('tput lines')))
    return (cols, rows)
  except:
    pass


def _get_terminal_size_linux():

  def ioctl_gwinsz(fd):
    try:
      import fcntl
      import termios

      maybe_cols_rows = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
      return maybe_cols_rows
    except:
      pass

  cols_rows = ioctl_gwinsz(0) or ioctl_gwinsz(1) or ioctl_gwinsz(2)
  if not cols_rows:
    try:
      file_desc = os.open(os.ctermid(), os.O_RDONLY)
      cols_rows = ioctl_gwinsz(file_desc)
      os.close(file_desc)
    except:
      pass
  if not cols_rows:
    try:
      cols_rows = (os.environ['LINES'], os.environ['COLUMNS'])
    except:
      return None
  return int(cols_rows[1]), int(cols_rows[0])


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
