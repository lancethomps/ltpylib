#!/usr/bin/env python
import dataclasses
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Union

import sqlalchemy
import sqlalchemy.engine.url

from ltpylib import configs
from ltpylib.common_types import DataWithUnknownPropertiesAsAttributes

DEFAULT_PG_SERVICE_CONFIG_SECTION = "dwh"
PG_ENGINES: Dict[str, sqlalchemy.engine.Engine] = {}
SQLITE_QUOTE_COL_REGEX = re.compile(r"[^a-zA-Z0-9_]")


class PgServiceConfig(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.dbname: str = values.pop("dbname", None)
    self.host: str = values.pop("host", None)
    self.password: str = values.pop("password", None)
    self.port: int = int(values.pop("port")) if "port" in values else None
    self.user: str = values.pop("user", None)

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


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


def add_sqlite_columns_from_dicts(
  datas: List[Dict[str, Any]],
  sqlite_cols: List[SQLiteColumn],
  ignore_cols: List[re.Pattern] = None,
) -> List[SQLiteColumn]:
  cols_by_name: Dict[str, SQLiteColumn] = {col.name: col for col in sqlite_cols}
  existing = [col.name for col in sqlite_cols]
  has_nulls = set()
  add_cols: List[SQLiteColumn] = []
  attr_cols: List[SQLiteColumn] = []

  for data in datas:
    for key, value in data.items():
      if ignore_cols and any([regex.fullmatch(key) is not None for regex in ignore_cols]):
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

  sqlite_cols.extend(sorted(add_cols, key=SQLiteColumn.col_sort))
  sqlite_cols.extend(sorted(attr_cols, key=SQLiteColumn.col_sort))

  return sqlite_cols


def create_sqlite_connection(
  db_file: Union[Path, str],
  detect_types: int = sqlite3.PARSE_DECLTYPES,
  use_row_factory_as_dict: bool = True,
) -> sqlite3.Connection:
  db_conn = sqlite3.connect(
    db_file,
    detect_types=detect_types,
  )

  if use_row_factory_as_dict:
    db_conn.row_factory = sqlite_row_factory_as_dict

  return db_conn


def sqlite_row_factory_as_dict(cursor: sqlite3.Cursor, row) -> Dict[str, Any]:
  row_as_dict = {}
  for idx, col in enumerate(cursor.description):
    row_as_dict[col[0]] = row[idx]
  return row_as_dict


def parse_pg_service_config_file(section: str = None) -> PgServiceConfig:
  config_file = Path.home().joinpath(".pg_service.conf")
  if not config_file.is_file():
    raise ValueError(".pg_service.conf file does not exist at: %s" % config_file.as_posix())

  use_mock_default_section = section is None
  parsed = configs.read_properties(config_file, use_mock_default_section=use_mock_default_section)

  if use_mock_default_section:
    parsed_as_dict = {key: val for key, val in parsed.defaults()}
  else:
    parsed_as_dict = {key: val for key, val in parsed.items(section)}

  return PgServiceConfig(values=parsed_as_dict)


def pg_query(
  sql: str,
  *multi_params,
  config: PgServiceConfig = None,
  **params,
) -> sqlalchemy.engine.ResultProxy:
  if params is not None:
    params = convert_pg_params_to_correct_types(params)

  engine = get_or_create_pg_engine(config if config else parse_pg_service_config_file(DEFAULT_PG_SERVICE_CONFIG_SECTION))
  return engine.execute(sqlalchemy.sql.text(sql), *multi_params, **params)


def pg_query_to_dicts(
  sql: str,
  *multi_params,
  config: PgServiceConfig = None,
  **params,
) -> List[Dict[str, Any]]:
  return query_result_to_dicts(pg_query(sql, *multi_params, config=config, **params))


def query_result_to_dicts(result: sqlalchemy.engine.ResultProxy) -> List[Dict[str, Any]]:
  return [dict(row.items()) for row in result.fetchall()]


def convert_pg_params_to_correct_types(params: dict) -> dict:
  for key, val in params.items():
    if isinstance(val, list):
      params[key] = tuple(val)

  return params


def create_pg_engine(config: PgServiceConfig) -> sqlalchemy.engine.Engine:
  db_connect_url = sqlalchemy.engine.url.URL(
    drivername="postgresql+psycopg2",  # pg+psycopg2
    username=config.user,
    password=config.password,
    host=config.host,
    port=config.port,
    database=config.dbname,
  )
  return sqlalchemy.create_engine(db_connect_url)


def get_or_create_pg_engine(config: PgServiceConfig) -> sqlalchemy.engine.Engine:
  global PG_ENGINES
  if str(config) not in PG_ENGINES:
    PG_ENGINES[str(config)] = create_pg_engine(config)

  return PG_ENGINES[str(config)]
