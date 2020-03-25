#!/usr/bin/env python3
import json

from typing import List

from ltpylib import dicts


def prettify_json(obj, remove_nulls: bool = False) -> str:
  if remove_nulls:
    obj = json.loads(
      prettify_json(obj, remove_nulls=False),
      object_hook=dicts.remove_nulls_and_empty,
    )
  return json.dumps(
    obj,
    sort_keys=True,
    indent='  ',
    default=lambda x: getattr(x, '__dict__', str(x)),
  )


def prettify_json_remove_nulls(obj) -> str:
  return prettify_json(obj, remove_nulls=True)


def dicts_to_csv(data: List[dict], showindex: bool = False) -> str:
  from pandas import DataFrame

  data_frame = DataFrame(data)
  return data_frame.to_csv(index=showindex)


def dicts_to_markdown_table(data: List[dict], showindex: bool = False, tablefmt: str = "github") -> str:
  import tabulate

  from pandas import DataFrame

  data_frame = DataFrame(data)
  return tabulate.tabulate(
    data_frame,
    showindex=showindex,
    headers=data_frame.columns,
    tablefmt=tablefmt,
  )
