#!/usr/bin/env python
import os
from pathlib import Path
from typing import Any, Generic, Sequence, TypeVar, Union

import looker_sdk
from looker_sdk.rtl.serialize import TModelOrSequence
from looker_sdk.sdk.api40.methods import Looker40SDK
from looker_sdk.sdk.api40.models import Dashboard

from ltpylib import files
from ltpylib.output import prettify_json, prettify_json_compact

LOOKER_CONFIG_FILE_DEFAULT = Path.home().joinpath(".config/looker.ini")
T = TypeVar("T")


class LookerApi(object):

  def __init__(
    self,
    config_file: Path = LOOKER_CONFIG_FILE_DEFAULT,
    user_id: str = os.getenv("LOOKER_USER_ID"),
  ):
    self.config_file: Path = config_file
    self.user_id: str = user_id

    self.client: Looker40SDK = looker_sdk.init40(config_file=self.config_file.as_posix())

  @staticmethod
  def deserialize(data: Union[str, Path, Any], structure: Generic[T]) -> T:
    if isinstance(data, Path):
      data = files.read_file(data)
    elif not isinstance(data, str):
      data = prettify_json_compact(data)

    return looker_sdk.rtl.serialize.deserialize40(data=data, structure=structure)

  @staticmethod
  def remove_dashboard_non_config_fields(dash: Dashboard) -> Dashboard:
    dash.last_accessed_at = None
    dash.last_viewed_at = None
    dash.view_count = None
    return dash

  @staticmethod
  def to_json(api_model: TModelOrSequence) -> str:
    return prettify_json(looker_sdk.rtl.serialize.converter40.unstructure(api_model))

  @property
  def user_id(self) -> str:
    if not self._user_id:
      self._user_id = self.client.me().id

    return self._user_id

  @user_id.setter
  def user_id(self, user_id: str):
    self._user_id = user_id

  def my_dashboards(self, limit: int = 100) -> Sequence[Dashboard]:
    return self.client.search_dashboards(user_id=self.user_id, limit=limit)
