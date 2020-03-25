#!/usr/bin/env python3
import logging
import subprocess
import sys
from typing import Sequence

from ltpylib import procs


def confirm(question: str = 'Continue?', default: str = None) -> bool:
  """Ask a yes/no question via raw_input() and return their answer.

  "question" is a string that is presented to the user.
  "default" is the presumed answer if the user just hits <Enter>.
      It must be "yes" (the default), "no" or None (meaning
      an answer is required of the user).

  The "answer" return value is True for "yes" or False for "no".
  """
  valid = {
    "yes": True,
    "y": True,
    "ye": True,
    "no": False,
    "n": False,
  }
  if default is None:
    prompt = "\n[y/n]> "
  elif default == "yes" or default == "y":
    prompt = "\n[Y/n]> "
  elif default == "no" or default == "n":
    prompt = "\n[y/N]> "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while True:
    choice = input(question + prompt).lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      logging.error("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def ask_for_input(prompt: str = 'Please input value.') -> str:
  return input(prompt + '\n> ')


def select_prompt(choices: Sequence[str], header: str = None, no_sort: bool = True, layout: str = "reverse") -> str:
  command = [
    'fzf',
    '--layout',
    layout,
  ]

  if header:
    command.extend(['--header', header])

  if no_sort:
    command.append('--no-sort')

  result: subprocess.CompletedProcess = procs.run(
    command,
    universal_newlines=True,
    stderr=sys.stderr,
    input="\n".join(choices),
  )

  if result.returncode == 130:
    raise KeyboardInterrupt

  result.check_returncode()
  return result.stdout.strip()


def select_prompt_old(choices: Sequence[str], message: str = None, bottom_message: str = None, max_width: int = None) -> str:
  command = ['select_prompt']

  if message:
    command.extend(['--message', message])

  if bottom_message:
    command.extend(['--bottom-message', message])

  if max_width:
    command.extend(['--max-width', str(max_width)])

  command.extend(choices)

  result: subprocess.CompletedProcess = procs.run(
    command,
    universal_newlines=True,
    stderr=sys.stderr,
  )
  if result.returncode == 130:
    raise KeyboardInterrupt

  result.check_returncode()
  return result.stdout.strip()


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
