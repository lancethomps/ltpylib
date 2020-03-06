#!/usr/bin/env python3
from typing import List

from ltpylib.common_types import DataWithUnknownProperties


class JenkinsBuild(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.building: bool = values.pop("building", None)
    self.duration: int = values.pop("duration", None)
    self.estimatedDuration: int = values.pop("estimatedDuration", None)
    self.result: str = values.pop("result", None)
    self.timestamp: int = values.pop("timestamp", None)

    self.estimatedTimeRemaining: int = None
    if self.duration is not None and self.estimatedDuration is not None and self.estimatedDuration > 0:
      self.estimatedTimeRemaining: int = self.estimatedDuration - self.duration

    DataWithUnknownProperties.__init__(self, values)
