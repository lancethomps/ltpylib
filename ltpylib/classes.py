#!/usr/bin/env python
from pathlib import Path
from typing import Optional, Type, TypeVar, Union

from dacite import Config, from_dict
from dacite.data import Data

from ltpylib import files

T = TypeVar("T")
DEFAULT_CONFIG = Config(
  type_hooks={
    Path: Path,
  },
)


def class_from_dict(
  data_class: Type[T],
  data: Union[Data, dict],
  config: Optional[Config] = DEFAULT_CONFIG,
) -> T:
  return from_dict(data_class=data_class, data=data, config=config)


def class_from_json_file(
  data_class: Type[T],
  file: Union[str, Path],
  config: Optional[Config] = DEFAULT_CONFIG,
) -> T:
  return class_from_dict(data_class, files.read_json_file(file), config=config)


def class_from_yaml_file(
  data_class: Type[T],
  file: Union[str, Path],
  config: Optional[Config] = DEFAULT_CONFIG,
) -> T:
  return class_from_dict(data_class, files.read_yaml_file(file), config=config)
