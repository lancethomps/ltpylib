#!/usr/bin/env python
import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from ltpylib.common_types import TypeWithDictRepr

CUSTOM_JSON_DUMPERS: Dict[str, Tuple[Callable[[Any], Any], Optional[Callable[[Any], bool]]]] = {}

PYGMENTS_DEFAULT_STYLE_FALLBACK = "solarized-light"
PYGMENTS_DEFAULT_STYLE_ORDER = ["smyck", PYGMENTS_DEFAULT_STYLE_FALLBACK]
PYGMENTS_DEFAULT_STYLE: Optional[str] = None


def default_pygments_style() -> str:
  global PYGMENTS_DEFAULT_STYLE

  if PYGMENTS_DEFAULT_STYLE:
    return PYGMENTS_DEFAULT_STYLE

  from pygments.plugin import iter_entry_points, STYLE_ENTRY_POINT

  for desired_style in PYGMENTS_DEFAULT_STYLE_ORDER:
    for entrypoint in iter_entry_points(STYLE_ENTRY_POINT):
      if entrypoint.name == desired_style:
        PYGMENTS_DEFAULT_STYLE = desired_style
        return PYGMENTS_DEFAULT_STYLE

  PYGMENTS_DEFAULT_STYLE = PYGMENTS_DEFAULT_STYLE_FALLBACK
  return PYGMENTS_DEFAULT_STYLE


def find_pygments_style() -> str:
  pygments_style = os.getenv("PYGMENTS_STYLE")
  if not pygments_style:
    pygments_style = default_pygments_style()

  return pygments_style


def colorize_json(data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  import pygments
  from pygments.formatters.terminal import TerminalFormatter
  from pygments.formatters.terminal256 import Terminal256Formatter
  from pygments.lexers.data import JsonLexer

  if not pygments_style:
    pygments_style = find_pygments_style()

  return pygments.highlight(
    data if isinstance(data, str) or data is None else prettify_json(data, colorize=False),
    JsonLexer(),
    Terminal256Formatter(style=pygments_style) if '256' in os.environ.get('TERM', '') else TerminalFormatter(style=pygments_style),
  )


def colorize_xml(data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  import pygments
  from pygments.formatters.terminal import TerminalFormatter
  from pygments.formatters.terminal256 import Terminal256Formatter
  from pygments.lexers.html import XmlLexer

  if not pygments_style:
    pygments_style = find_pygments_style()

  return pygments.highlight(
    data if isinstance(data, str) or data is None else prettify_xml(data, colorize=False),
    XmlLexer(),
    Terminal256Formatter(style=pygments_style) if '256' in os.environ.get('TERM', '') else TerminalFormatter(style=pygments_style),
  )


def is_output_to_terminal() -> bool:
  import sys

  return sys.stdout.isatty()


def should_color(colorize: bool = False, auto_color: bool = False) -> bool:
  if colorize:
    return True

  if auto_color and is_output_to_terminal():
    return True

  return False


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


def load_json_remove_nulls(data: str) -> Any:
  from ltpylib import dicts

  return json.loads(
    data,
    object_hook=dicts.remove_nulls_and_empty,
  )


def prettify_json_compact(obj, remove_nulls: bool = False, colorize: bool = False) -> str:
  if remove_nulls:
    obj = load_json_remove_nulls(json.dumps(obj, default=json_dump_default))

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
  return prettify_json(obj, remove_nulls=remove_nulls, auto_color=True)


def prettify_json(obj, remove_nulls: bool = False, colorize: bool = False, auto_color: bool = False) -> str:
  if remove_nulls:
    obj = load_json_remove_nulls(json.dumps(obj, default=json_dump_default))

  output = json.dumps(
    obj,
    sort_keys=True,
    indent='  ',
    default=json_dump_default,
  )

  if should_color(colorize=colorize, auto_color=auto_color):
    output = colorize_json(output)

  return output


def prettify_json_remove_nulls(obj) -> str:
  return prettify_json(obj, remove_nulls=True)


def prettify_xml(obj, remove_nulls: bool = False, colorize: bool = False, auto_color: bool = False) -> str:
  from xml.dom.minidom import parseString
  from dicttoxml import dicttoxml

  if remove_nulls:
    obj = load_json_remove_nulls(json.dumps(obj, default=json_dump_default))

  output = parseString(dicttoxml(obj)).toprettyxml()

  if should_color(colorize=colorize, auto_color=auto_color):
    output = colorize_xml(output)

  return output


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


def dicts_to_markdown_table(
  data: Union[List[dict], List[TypeWithDictRepr]],
  showindex: bool = False,
  tablefmt: str = "github",
  headers: Sequence[str] = None,
) -> str:
  import tabulate

  from pandas import DataFrame

  if len(data) > 0 and isinstance(data[0], TypeWithDictRepr):
    data_as_class: List[TypeWithDictRepr] = data
    data = [val.as_dict() for val in data_as_class]

  data_frame = DataFrame(data)
  return tabulate.tabulate(
    data_frame,
    showindex=showindex,
    headers=headers if headers is not None else data_frame.columns,
    tablefmt=tablefmt,
  )


def sort_csv_rows(rows: List[str]) -> List[str]:
  return [rows[0]] + sorted(rows[1:])
