#!/usr/bin/env python
import contextlib
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from ltpylib import strings
from ltpylib.common_types import TypeWithDictRepr


class ChromeExtensions(TypeWithDictRepr):

  def __init__(self):
    self.installed: List[ChromeExtension] = []
    self.pinned_extensions: List[str] = []
    self.toolbar: List[str] = []


@dataclass
class ChromeExtension:
  extension_id: str
  name: str
  description: str
  stars: Optional[float] = None
  ratings: Optional[int] = None


def create_chrome_extension(extension_id: str, use_search: bool = False) -> ChromeExtension:
  import requests
  from bs4 import BeautifulSoup
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
    stars = None
    ratings = None
  else:
    name_elem = parsed_html.select_one("meta[property='og:title']")
    description_elem = parsed_html.select_one("meta[property='og:description']")
    ratings_elem = parsed_html.select_one("a[href*='/reviews'] > p")
    stars_elem: BeautifulSoup | None = None
    if ratings_elem:
      try:
        stars_elem = next(ratings_elem.parent.parent.parent.children)
      except:
        pass

    name = name_elem.get("content") if name_elem else None
    description = description_elem.get("content") if description_elem else None
    with contextlib.suppress(BaseException):
      stars = strings.convert_to_number(stars_elem.text) if stars_elem else None
    with contextlib.suppress(BaseException):
      ratings = strings.convert_to_number(re.search(r"\d+", ratings_elem.text).group()) if ratings_elem else None

  return ChromeExtension(
    extension_id=extension_id,
    name=name,
    description=description,
    stars=stars,
    ratings=ratings,
  )
