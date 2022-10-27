#!/usr/bin/env python
from typing import List

import requests

from ltpylib import requests_helper

DD_API_BASE = "https://api.datadoghq.com/api/v1"


class DatadogApi(object):

  def __init__(
    self,
    dd_api_key: str,
    dd_application_key: str = None,
    base_url: str = DD_API_BASE,
  ):
    self._dd_api_key: str = dd_api_key
    self._dd_application_key: str = dd_application_key

    self.base_url: str = base_url.removesuffix("/")
    self.session: requests.Session = requests.Session()
    self.session.headers.update({
      "Accept": "application/json",
      "Content-Type": "application/json",
      "DD-API-KEY": dd_api_key,
    })
    if dd_application_key:
      self.session.headers.update({"DD-APPLICATION-KEY": dd_application_key})

  def url(self, path: str) -> str:
    if not path.startswith("/"):
      path = "/" + path

    return self.base_url + path

  def get_dashboard(self, dashboard_id: str) -> dict:
    return requests_helper.maybe_throw(self.session.get(self.url(f"/dashboard/{dashboard_id}"))).json()

  def get_dashboards(self) -> List[dict]:
    return requests_helper.maybe_throw(self.session.get(self.url("/dashboard"))).json()["dashboards"]

  def update_dashboard(self, dashboard_id: str, dashboard: dict) -> dict:
    return requests_helper.maybe_throw(self.session.put(self.url(f"/dashboard/{dashboard_id}"), json=dashboard)).json()
