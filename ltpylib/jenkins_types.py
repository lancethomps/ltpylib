#!/usr/bin/env python3
import time

from ltpylib.common_types import DataWithUnknownProperties


class JenkinsBuild(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.building: bool = values.pop("building", None)
    self.duration: int = values.pop("duration", None)
    self.estimatedDuration: int = values.pop("estimatedDuration", None)
    self.result: str = values.pop("result", None)
    self.timestamp: int = values.pop("timestamp", None)

    self.timeRunning: int = None
    if self.timestamp is not None:
      self.timeRunning = (int(time.time() * 1000) - self.timestamp)

    self.estimatedTimeRemaining: int = None
    if self.duration is not None and self.duration > 0 and self.estimatedDuration is not None and self.estimatedDuration > 0:
      self.estimatedTimeRemaining: int = self.estimatedDuration - self.duration
    elif self.estimatedDuration is not None and self.estimatedDuration > 0 and self.timeRunning is not None:
      self.estimatedTimeRemaining: int = self.estimatedDuration - self.timeRunning

    DataWithUnknownProperties.__init__(self, values)
