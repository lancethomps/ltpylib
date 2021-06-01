#!/usr/bin/env python
import sqlite3
from pathlib import Path
from typing import Any, Dict, Union


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
