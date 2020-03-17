#!/usr/bin/env python3
from datetime import datetime

from dateutil import parser


def from_millis(millis: int) -> datetime:
  return datetime.fromtimestamp(millis / 1000.0)


def parse_iso_date(date_string: str) -> datetime:
  return parser.isoparse(date_string)


def parse_date(date_string: str, format: str = None) -> datetime:
  if not format:
    return parser.parse(date_string)
  return datetime.strptime(date_string, format)


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
