#!/usr/bin/env python

import logging
from typing import List


class ChromeExtensions(object):

  def __init__(self):
    self.installed: List[ChromeExtension] = []
    self.pinned_extensions: List[str] = []
    self.toolbar: List[str] = []


class ChromeExtension(object):

  def __init__(self, extension_id: str, name: str, description: str):
    self.extension_id: str = extension_id
    self.name: str = name
    self.description: str = description


def create_chrome_extension(extension_id: str) -> ChromeExtension:
  import requests
  from ltpylib import htmlparser

  url = f"https://chrome.google.com/webstore/detail/{extension_id}"
  logging.debug(f"Getting extension details: {url}")

  response = requests.get(url)
  parsed_html = htmlparser.create_parser(response.text)
  name_elem = parsed_html.select_one("meta[property='og:title']")
  description_elem = parsed_html.select_one("meta[property='og:description']")

  return ChromeExtension(
    extension_id,
    name_elem.get("content") if name_elem else None,
    description_elem.get("content") if description_elem else None,
  )
