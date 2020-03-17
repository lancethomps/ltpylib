#!/usr/bin/env python3
# pylint: disable=C0111
from typing import List, Union

EMPTY_LIST: frozenset = frozenset([])
EMPTY_MAP: tuple = tuple(sorted({}.items()))


def to_csv(values: Union[List, None], sep: str = ",") -> Union[str, None]:
  return sep.join(values) if values else None
