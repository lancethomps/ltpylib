#!/usr/bin/env python3
from datetime import datetime


def from_millis(millis: int) -> datetime:
  return datetime.fromtimestamp(millis / 1000.0)


def parse_iso_date(date_string: str) -> datetime:
  if not date_string:
    return None

  from dateutil import parser

  return parser.isoparse(date_string)


def parse_date(date_string: str, format: str = None) -> datetime:
  from dateutil import parser

  if not format:
    return parser.parse(date_string)
  return datetime.strptime(date_string, format)


def parse_possibly_relative_date(date_string: str) -> datetime:
  import dateparser

  return dateparser.parse(date_string)


def to_yyyymmdd(date: datetime) -> str:
  return date.strftime("%Y%m%d")


def to_json_isoformat(date: datetime) -> str:
  return date.isoformat(sep="T", timespec="milliseconds") + "Z"


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
