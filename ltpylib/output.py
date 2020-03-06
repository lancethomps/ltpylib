#!/usr/bin/env python3
import json
from typing import List

import pandas
import tabulate


def prettify_json(obj) -> str:
  return json.dumps(obj, sort_keys=True, indent='  ', default=lambda x: getattr(x, '__dict__', str(x)))


def dicts_to_csv(data: List[dict], showindex: bool = False) -> str:
  data_frame = pandas.DataFrame(data)
  return data_frame.to_csv(
    index=showindex
  )


def dicts_to_markdown_table(data: List[dict], showindex: bool = False, tablefmt: str = "github") -> str:
  data_frame = pandas.DataFrame(data)
  return tabulate.tabulate(
    data_frame,
    showindex=showindex,
    headers=data_frame.columns,
    tablefmt=tablefmt
  )
