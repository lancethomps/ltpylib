#!/usr/bin/env python
import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from ltpylib.collect import modify_list_of_dicts
from ltpylib.common_types import TypeWithDictRepr
from ltpylib.dicts import modify_dict_fields

CUSTOM_JSON_DUMPERS: Dict[str, Tuple[Callable[[Any], Any], Optional[Callable[[Any], bool]]]] = {}

HAS_JQ: Optional[bool] = None

PYGMENTS_DEFAULT_STYLE_ORDER = ["jq", "smyck", "vim", "solarized-light"]
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

  raise ValueError("Could not find pygments style from options: %s" % PYGMENTS_DEFAULT_STYLE_ORDER)


def find_pygments_style() -> str:
  pygments_style = os.getenv("PYGMENTS_STYLE")
  if not pygments_style:
    pygments_style = default_pygments_style()

  return pygments_style


def create_terminal_formatter(pygments_style: str):
  if "256" in os.getenv("TERM", ""):
    from pygments.formatters.terminal256 import Terminal256Formatter

    return Terminal256Formatter(style=pygments_style)

  from pygments.formatters.terminal import TerminalFormatter

  return TerminalFormatter(style=pygments_style)


def has_jq() -> bool:
  global HAS_JQ
  if HAS_JQ is not None:
    return HAS_JQ

  from ltpylib.checks import check_command

  HAS_JQ = check_command("jq")
  return HAS_JQ


def colorize_json_jq(data: Union[str, dict, Sequence]) -> Optional[str]:
  from ltpylib.procs import run_and_parse_output

  if data is None:
    json_data = "null"
  else:
    json_data = data if isinstance(data, str) or data is None else json.dumps(data, indent=None, default=json_dump_default)

  return run_and_parse_output(["jq", "--sort-keys", "--color-output"], input=json_data, check=True)[1]


def colorize_with_pygments(format_lang: str, prettifier: Callable, data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  from pygments import highlight
  from pygments.lexers import get_lexer_by_name

  if not pygments_style:
    pygments_style = find_pygments_style()

  if data is None:
    string_data = "null"
  elif isinstance(data, str):
    string_data = data
  else:
    string_data = prettifier(data, colorize=False)

  return highlight(
    string_data,
    get_lexer_by_name(format_lang),
    create_terminal_formatter(pygments_style),
  )


def colorize_json(data: Union[str, dict, Sequence], pygments_style: str = None, force_pygments: bool = False) -> Union[bytes, str]:
  global HAS_JQ
  if not force_pygments and pygments_style is None and HAS_JQ is not False:
    if HAS_JQ is None:
      try:
        result = colorize_json_jq(data)
        HAS_JQ = True
        return result
      except FileNotFoundError:
        HAS_JQ = False

    else:
      return colorize_json_jq(data)

  return colorize_with_pygments("json", prettify_json, data, pygments_style=pygments_style)


def colorize_xml(data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  return colorize_with_pygments("xml", prettify_xml, data, pygments_style=pygments_style)


def colorize_yaml(data: Union[str, dict, Sequence], pygments_style: str = None) -> Union[bytes, str]:
  return colorize_with_pygments("yaml", prettify_yaml, data, pygments_style=pygments_style)


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


def prettify_yaml(obj, remove_nulls: bool = False, colorize: bool = False, auto_color: bool = False) -> str:
  import yaml

  if remove_nulls:
    obj = load_json_remove_nulls(json.dumps(obj, default=json_dump_default))

  output = yaml.dump(
    obj,
    default_flow_style=False,
  )

  if should_color(colorize=colorize, auto_color=auto_color):
    output = colorize_yaml(output)

  return output


def dicts_to_csv(
  data: Union[List[dict], List[TypeWithDictRepr]],
  showindex: bool = False,
  sep: str = ",",
  header: bool = True,
  fields_included: Sequence[str] = None,
  fields_order: Sequence[str] = None,
  modify_in_place: bool = False,
) -> str:
  from pandas import DataFrame

  data_as_dicts: List[dict] = create_data_as_dicts(
    data,
    fields_included=fields_included,
    fields_order=fields_order,
    modify_in_place=modify_in_place,
  )

  data_frame = DataFrame(data_as_dicts)
  return data_frame.to_csv(
    sep=sep,
    header=header,
    index=showindex,
  )


def dicts_to_markdown_table(
  data: Union[List[dict], List[TypeWithDictRepr]],
  showindex: bool = False,
  tablefmt: str = "github",
  escape_data: bool = True,
  headers: Sequence[str] = None,
  fields_included: Sequence[str] = None,
  fields_order: Sequence[str] = None,
  modify_in_place: bool = False,
) -> str:
  import tabulate

  from pandas import DataFrame

  data_as_dicts: List[dict] = create_data_as_dicts(
    data,
    fields_included=fields_included,
    fields_order=fields_order,
    modify_in_place=modify_in_place,
  )

  if escape_data:

    def escape_fn(row: dict):
      for field, value in row.items():
        if isinstance(value, str) and ("|" in value or "\n" in value):
          row[field] = value.replace("|", "&#124;").replace("\n", "<br/>")

    data_as_dicts = modify_list_of_dicts(data_as_dicts, escape_fn, in_place=modify_in_place)

  data_frame = DataFrame(data_as_dicts)
  return tabulate.tabulate(
    data_frame,
    showindex=showindex,
    headers=headers if headers is not None and len(headers) > 0 else data_frame.columns,
    tablefmt=tablefmt,
  )


def sort_csv_rows(rows: List[str]) -> List[str]:
  return [rows[0]] + sorted(rows[1:])


def create_data_as_dicts(
  data: Union[List[dict], List[TypeWithDictRepr]],
  fields_included: Sequence[str] = None,
  fields_order: Sequence[str] = None,
  modify_in_place: bool = False,
) -> List[dict]:
  data_as_dicts: List[dict] = data

  if len(data) > 0 and isinstance(data[0], TypeWithDictRepr):
    data_as_class: List[TypeWithDictRepr] = data
    data_as_dicts = [val.as_dict() for val in data_as_class]

  if fields_order or fields_included:
    data_as_dicts = modify_dict_fields(
      data_as_dicts,
      fields_included=fields_included,
      fields_order=fields_order,
      in_place=modify_in_place,
    )

  return data_as_dicts
