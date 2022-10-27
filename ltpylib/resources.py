#!/usr/bin/env python

import os
from typing import Optional


class PutEnvTemp(object):

  def __init__(self, var_name: str, var_value: str):
    self.var_name = var_name
    self.var_value = var_value
    self.reset_value: Optional[str] = None

  def update_env(self, to_val: Optional[str]):
    if to_val is None:
      os.unsetenv(self.var_name)
    else:
      os.putenv(self.var_name, to_val)

  def __enter__(self):
    self.reset_value = os.getenv(self.var_name)
    self.update_env(self.var_value)

  def __exit__(self, *exc_details):
    self.update_env(self.reset_value)


def putenv_temp(var_name: str, var_value: str) -> PutEnvTemp:
  return PutEnvTemp(var_name, var_value)
