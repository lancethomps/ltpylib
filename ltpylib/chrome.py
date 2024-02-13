#!/usr/bin/env python

import logging
from typing import List

from ltpylib.common_types import TypeWithDictRepr


class ChromeExtensions(TypeWithDictRepr):

  def __init__(self):
    self.installed: List[ChromeExtension] = []
    self.pinned_extensions: List[str] = []
    self.toolbar: List[str] = []


class ChromeExtension(TypeWithDictRepr):

  def __init__(self, extension_id: str, name: str, description: str):
    self.extension_id: str = extension_id
    self.name: str = name
    self.description: str = description


def create_chrome_extension(extension_id: str, use_search: bool = False) -> ChromeExtension:
  import requests
  from ltpylib import htmlparser

  if use_search:
    url = f"https://chromewebstore.google.com/search/{extension_id}?hl=en-US"
  else:
    url = f"https://chromewebstore.google.com/detail/{extension_id}"

  logging.debug(f"Getting extension details: {url}")
  response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"})
  parsed_html = htmlparser.create_parser(response.text)

  if use_search:
    name_elem = parsed_html.select_one(f"[data-item-id=\"{extension_id}\"] h2")
    description_elem = parsed_html.select_one(f"[data-item-id=\"{extension_id}\"] > div > div > p:last-child")
    name = name_elem.text if name_elem else None
    description = description_elem.text if description_elem else None
  else:
    name_elem = parsed_html.select_one("meta[property='og:title']")
    description_elem = parsed_html.select_one("meta[property='og:description']")
    name = name_elem.get("content") if name_elem else None
    description = description_elem.get("content") if description_elem else None

  return ChromeExtension(extension_id, name, description)
