#!/usr/bin/env python
import dataclasses
from typing import Any, List, Optional


@dataclasses.dataclass
class SearchParam:
  name: Optional[str]
  value: Any
  is_or: bool = False


def create_search_query(params: List[SearchParam]) -> str:
  query: List[str] = []

  for param in params:
    query.append(construct_search_param(param))

  return " ".join(query)


def construct_search_param(param: SearchParam) -> str:
  part = f"{param.name}:" if param.name else ""
  value = param.value
  if isinstance(value, list) and len(value) == 1:
    value = value[0]

  if isinstance(value, list):
    part += "("

    if len(value) > 0 and isinstance(value[0], SearchParam):
      values = [construct_search_param(v) for v in value]
    else:
      values = [str(v) for v in value]

    if param.is_or:
      part += " OR ".join(values)
    else:
      part += " AND ".join(values)

    part += ")"
  else:
    part += construct_search_param(value) if isinstance(value, SearchParam) else str(value)

  return part
