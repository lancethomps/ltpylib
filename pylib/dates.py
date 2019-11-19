#!/usr/bin/env python3
import datetime


def from_millis(millis: int) -> datetime.datetime:
  return datetime.datetime.fromtimestamp(millis / 1000.0)


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
