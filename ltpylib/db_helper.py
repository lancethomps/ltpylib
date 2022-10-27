#!/usr/bin/env python
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Union

import sqlalchemy
import sqlalchemy.engine.url

from ltpylib import configs, files, patterns
from ltpylib.common_types import DataWithUnknownPropertiesAsAttributes

DEFAULT_PG_SERVICE_CONFIG_SECTION = "dwh"
PG_ENGINES: Dict[str, sqlalchemy.engine.Engine] = {}

SQL_CMD_REGEX_MAIN = r"((SELECT|WITH|EXPLAIN)[^;]*?^;)"
SQL_CMD_REGEX_PRIMARY = r"(?s)^-- ?use\n" + SQL_CMD_REGEX_MAIN
SQL_CMD_REGEX_SECONDARY = r"(?s)^" + SQL_CMD_REGEX_MAIN
SQL_CMD_REGEX_QUERY_ID_REPL_STR = "<query_id>"
SQL_CMD_REGEX_QUERY_ID = r"(?s)^-- ?" + SQL_CMD_REGEX_QUERY_ID_REPL_STR + r"\n([^;]+^;)"
SQL_CMD_REGEX_QUERY_ID_ALL = r"(?s)^-- ?([a-zA-Z0-9_-]+)\n([^;]+^;)"
SQL_CMD_REGEX_FLAGS = re.MULTILINE
SQL_CMD_REGEX_GROUP = 1


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


def pull_sql_from_file(query_ids: Union[List[str], str], resolved_sql_file: Path) -> str:
  if isinstance(query_ids, str):
    query_ids = [query_ids]

  if query_ids:
    queries: List[str] = []
    for qid in query_ids:
      queries.append(match_query_regex_in_file(
        resolved_sql_file,
        [
          SQL_CMD_REGEX_QUERY_ID.replace(SQL_CMD_REGEX_QUERY_ID_REPL_STR, qid),
        ],
      ))

    return "\n".join(queries)

  else:
    return match_query_regex_in_file(
      resolved_sql_file,
      [
        SQL_CMD_REGEX_PRIMARY,
        SQL_CMD_REGEX_SECONDARY,
      ],
    )


def pull_query_ids_from_file(sql_file: Path) -> List[str]:
  return patterns.pull_matches_from_file(sql_file, SQL_CMD_REGEX_QUERY_ID_ALL, group=1, flags=SQL_CMD_REGEX_FLAGS)


def locate_sql_file(
  sql_file: str,
  base_dir: Path = None,
  default_file: Path = None,
) -> Path:
  if not sql_file:
    if not default_file:
      raise ValueError("You must either pass --default-file or a valid <sql_file> parameter to this script.")

    return default_file

  for maybe_file in [Path(sql_file), Path(sql_file + ".sql")]:
    if maybe_file.is_file():
      return maybe_file

  if not base_dir:
    raise ValueError("<sql_file> does not exist: " + sql_file)

  for maybe_file in [base_dir.joinpath(sql_file), base_dir.joinpath(sql_file + ".sql")]:
    if maybe_file.is_file():
      return maybe_file

  raise ValueError("<sql_file> does not exist: " + sql_file)


def match_query_regex_in_file(resolved_sql_file: Path, regexes_to_check: List[str]) -> str:
  file_contents = files.read_file(resolved_sql_file)

  for regex_to_check in regexes_to_check:
    for match in re.finditer(regex_to_check, file_contents, flags=SQL_CMD_REGEX_FLAGS):
      return match.group(SQL_CMD_REGEX_GROUP)

  raise Exception("Could not find a sql query match in file: " + resolved_sql_file.as_posix())
