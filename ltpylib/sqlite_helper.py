#!/usr/bin/env python
import dataclasses
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Union

from ltpylib import files
from ltpylib.output import dicts_to_csv, prettify_sql

SQLITE_QUOTE_COL_REGEX = re.compile(r"[^a-zA-Z0-9_]")


@dataclasses.dataclass
class SQLiteColumn:
  name: str
  value_type: str
  has_nulls: bool = False

  @staticmethod
  def col_sort(col: 'SQLiteColumn') -> list:
    return [col.name]

  def create_col_name(self) -> str:
    name = self.name
    if SQLITE_QUOTE_COL_REGEX.match(name):
      name = '"' + name + '"'

    return name

  def create_update_blanks_to_null(self, table_name: str) -> str:
    col_name = self.create_col_name()
    return f"""
UPDATE {table_name}
SET {col_name} = NULL
WHERE {col_name} = '';
    """.strip()

  def to_create_column(self) -> str:
    col_def = f"{self.create_col_name()} {self.value_type}"
    if not self.has_nulls:
      col_def = col_def + " NOT NULL"

    return col_def

  def to_primary_key(self) -> str:
    return f"PRIMARY KEY ({self.create_col_name()})"


@dataclasses.dataclass
class SQLiteCreateTable:
  columns: List[SQLiteColumn]
  sql_cmd: str
  rows_as_csv: str = None
  csv_file: Path = None


def add_sqlite_columns_from_dicts(
  datas: List[Dict[str, Any]],
  sqlite_cols: List[SQLiteColumn],
  ignore_cols: List[re.Pattern] = None,
  only_cols: List[str] = None,
) -> List[SQLiteColumn]:
  cols_by_name: Dict[str, SQLiteColumn] = {col.name: col for col in sqlite_cols}
  existing = [col.name for col in sqlite_cols]
  has_nulls = set()
  add_cols: List[SQLiteColumn] = []
  attr_cols: List[SQLiteColumn] = []

  for idx, data in enumerate(datas):
    missing_existing_cols = list(cols_by_name.keys())

    for key, value in data.items():
      if key in missing_existing_cols:
        missing_existing_cols.remove(key)
      elif idx > 0:
        has_nulls.add(key)

      if ignore_cols and any([regex.fullmatch(key) is not None for regex in ignore_cols]):
        continue
      elif only_cols and key not in only_cols:
        continue

      if value is None:
        has_nulls.add(key)

        if key in cols_by_name:
          cols_by_name.get(key).has_nulls = True

        continue
      elif key in existing:
        continue

      existing.append(key)
      value_type = "TEXT"
      if isinstance(value, int):
        value_type = "INTEGER"
      elif isinstance(value, float):
        value_type = "REAL"

      col = SQLiteColumn(name=key, value_type=value_type, has_nulls=(key in has_nulls))
      cols_by_name[col.name] = col

      if key.startswith("attr_"):
        attr_cols.append(col)
      else:
        add_cols.append(col)

    if missing_existing_cols:
      has_nulls.update(missing_existing_cols)
      for col_name in missing_existing_cols:
        cols_by_name.get(col_name).has_nulls = True

  sqlite_cols.extend(sorted(add_cols, key=SQLiteColumn.col_sort))
  sqlite_cols.extend(sorted(attr_cols, key=SQLiteColumn.col_sort))

  return sqlite_cols


def sqlite_create_table_from_dicts(
  table_name: str,
  rows: List[dict],
  existing_cols: List[SQLiteColumn] = None,
  primary_key: SQLiteColumn = None,
  ignore_cols: List[re.Pattern] = None,
  only_cols: List[str] = None,
  additional_table_config: List[str] = None,
  load_file: Union[str, Path] = None,
  create_csv_from_rows: bool = True,
  create_csv_convert_booleans: bool = True,
) -> SQLiteCreateTable:
  sqlite_cols: List[SQLiteColumn] = existing_cols.copy() if existing_cols else []

  add_sqlite_columns_from_dicts(
    rows,
    sqlite_cols,
    ignore_cols=ignore_cols,
    only_cols=only_cols,
  )

  sql_cmd_parts = []

  cols_sql_statements = [col.to_create_column() for col in sqlite_cols]

  if primary_key:
    cols_sql_statements.append(primary_key.to_primary_key())

  if additional_table_config:
    cols_sql_statements.extend(additional_table_config)

  cols_sql = ",\n  ".join(cols_sql_statements)

  drop_create_sql = prettify_sql(textwrap.dedent(f"""\
    DROP TABLE IF EXISTS {table_name}
    ;

    CREATE TABLE {table_name} (
      {cols_sql}
    )
    ;
  """.rstrip()))

  sql_cmd_parts.append(drop_create_sql)

  if load_file:
    if isinstance(load_file, Path):
      load_file = load_file.as_posix()

    sqlite_cmds = textwrap.dedent(
      f"""\
      -- @formatter:off
      .mode csv
      .separator |
      .echo on
      .import {load_file} {table_name}
      .echo off
      -- @formatter:on
      """.rstrip()
    )

    sql_cmd_parts.append(sqlite_cmds)

    set_null_sql = prettify_sql("\n\n".join([col.create_update_blanks_to_null(table_name) for col in sqlite_cols if col.has_nulls]))
    sql_cmd_parts.append(set_null_sql)

  sql_cmd = "\n\n".join([part.strip() for part in sql_cmd_parts])

  result = SQLiteCreateTable(columns=sqlite_cols, sql_cmd=sql_cmd)

  if create_csv_from_rows:
    cols_fields = [col.name for col in sqlite_cols]
    if create_csv_convert_booleans:
      for row in rows:
        for col_name in cols_fields:
          value = row.get(col_name)
          if isinstance(value, bool):
            row[col_name] = str(value).upper()

    result.rows_as_csv = dicts_to_csv(
      rows,
      sep="|",
      header=False,
      fields_included=cols_fields,
      fields_order=cols_fields,
    )

    if load_file:
      result.csv_file = files.convert_to_path(load_file)
      files.write_file(result.csv_file, result.rows_as_csv, log_file_path=True)

  return result
