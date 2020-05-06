#!/usr/bin/env python3


class DataWithUnknownProperties(object):

  def __init__(self, values: dict = None):
    self.unknownProperties: dict = values if values else None


class DataWithUnknownPropertiesAsAttributes(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    if values:
      self.hasUnknownProperties: bool = True
      for item in values.items():
        setattr(self, str(item[0]), item[1])

      values.clear()

    DataWithUnknownProperties.__init__(self, values=None)
