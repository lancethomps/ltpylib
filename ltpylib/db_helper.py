#!/usr/bin/env python
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Union

import sqlalchemy
import sqlalchemy.engine.url

from ltpylib import configs
from ltpylib.common_types import DataWithUnknownPropertiesAsAttributes

DEFAULT_PG_SERVICE_CONFIG_SECTION = "dwh"
PG_ENGINES: Dict[str, sqlalchemy.engine.Engine] = {}


class PgServiceConfig(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.dbname: str = values.pop("dbname", None)
    self.host: str = values.pop("host", None)
    self.password: str = values.pop("password", None)
    self.port: int = int(values.pop("port")) if "port" in values else None
    self.user: str = values.pop("user", None)

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


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
