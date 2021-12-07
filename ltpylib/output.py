#!/usr/bin/env python
import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from ltpylib.common_types import TypeWithDictRepr

CUSTOM_JSON_DUMPERS: Dict[str, Tuple[Callable[[Any], Any], Optional[Callable[[Any], bool]]]] = {}


def colorize_json(json_data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  import pygments
  from pygments.formatters.terminal import TerminalFormatter
  from pygments.formatters.terminal256 import Terminal256Formatter
  from pygments.lexers.data import JsonLexer

  if not pygments_style:
    pygments_style = os.getenv("PYGMENTS_STYLE", "solarized-light")

  return pygments.highlight(
    json_data if isinstance(json_data, str) or json_data is None else prettify_json(json_data, colorize=False),
    JsonLexer(),
    Terminal256Formatter(style=pygments_style) if '256' in os.environ.get('TERM', '') else TerminalFormatter(style=pygments_style),
  )


def is_output_to_terminal() -> bool:
  import sys

  return sys.stdout.isatty()


def add_custom_json_dumper(dumper_id: str, dumper: Callable[[Any], Any], use_if: Callable[[Any], bool] = None):
  global CUSTOM_JSON_DUMPERS
  CUSTOM_JSON_DUMPERS[dumper_id] = (dumper, use_if)


def json_dump_default(val: Any) -> Any:
  if hasattr(val, "to_dict"):
    return getattr(val, "to_dict")()

  if CUSTOM_JSON_DUMPERS:
    for dumper, use_if in CUSTOM_JSON_DUMPERS.values():
      if use_if is not None:
        if not use_if(val):
          continue
        return dumper(val)
      else:
        dumper_val = dumper(val)
        if dumper_val is not None:
          return dumper_val

  return getattr(val, '__dict__', str(val))


def prettify_json_compact(obj, remove_nulls: bool = False, colorize: bool = False) -> str:
  if remove_nulls:
    from ltpylib import dicts

    obj = json.loads(
      prettify_json(obj, remove_nulls=False, colorize=False),
      object_hook=dicts.remove_nulls_and_empty,
    )
  output = json.dumps(
    obj,
    sort_keys=True,
    indent=None,
    separators=(",", ":"),
    default=json_dump_default,
  )

  if colorize:
    output = colorize_json(output)

  return output


def prettify_json_auto_color(obj, remove_nulls: bool = False) -> str:
  return prettify_json(obj, remove_nulls=remove_nulls, colorize=is_output_to_terminal())


def prettify_json(obj, remove_nulls: bool = False, colorize: bool = False) -> str:
  if remove_nulls:
    from ltpylib import dicts

    obj = json.loads(
      prettify_json(obj, remove_nulls=False, colorize=False),
      object_hook=dicts.remove_nulls_and_empty,
    )
  output = json.dumps(
    obj,
    sort_keys=True,
    indent='  ',
    default=json_dump_default,
  )

  if colorize:
    output = colorize_json(output)

  return output


def prettify_json_remove_nulls(obj) -> str:
  return prettify_json(obj, remove_nulls=True)


def prettify_yaml(obj, remove_nulls: bool = False) -> str:
  import yaml

  obj = json.loads(prettify_json(
    obj,
    remove_nulls=remove_nulls,
    colorize=False,
  ))

  return yaml.dump(
    obj,
    default_flow_style=False,
  )


def dicts_to_csv(data: List[dict], showindex: bool = False) -> str:
  from pandas import DataFrame

  data_frame = DataFrame(data)
  return data_frame.to_csv(index=showindex)


def dicts_to_markdown_table(data: Union[List[dict], List[TypeWithDictRepr]], showindex: bool = False, tablefmt: str = "github") -> str:
  import tabulate

  from pandas import DataFrame

  if len(data) > 0 and isinstance(data[0], TypeWithDictRepr):
    data_as_class: List[TypeWithDictRepr] = data
    data = [val.as_dict() for val in data_as_class]

  data_frame = DataFrame(data)
  return tabulate.tabulate(
    data_frame,
    showindex=showindex,
    headers=data_frame.columns,
    tablefmt=tablefmt,
  )


def sort_csv_rows(rows: List[str]) -> List[str]:
  return [rows[0]] + sorted(rows[1:])
