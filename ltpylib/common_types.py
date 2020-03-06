#!/usr/bin/env python3


class DataWithUnknownProperties(object):

  def __init__(self, values: dict = None):
    if values:
      self.unknownProperties: dict = values
