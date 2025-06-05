#!/usr/bin/env python
import atexit
from typing import List, Optional, Type, TypeVar

import datadog_api_client
import requests
from datadog_api_client.model_utils import deserialize_model, OpenApiModel
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_update_request import MonitorUpdateRequest

from ltpylib import requests_helper

DD_API_BASE = "https://api.datadoghq.com/api/v1"
OpenApiModelType = TypeVar("OpenApiModelType", bound=OpenApiModel)


class DatadogApi(object):

  def __init__(
    self,
    dd_api_key: str,
    dd_application_key: str = None,
    base_url: str = DD_API_BASE,
  ):
    self._dd_api_key: str = dd_api_key
    self._dd_application_key: str = dd_application_key

    self.dd_api_client: datadog_api_client.ApiClient = datadog_api_client.ApiClient(
      datadog_api_client.Configuration(api_key={
        "apiKeyAuth": dd_api_key,
        "appKeyAuth": dd_application_key,
      })
    )
    atexit.register(self.dd_api_client.close)
    self.dashboards_api: DashboardsApi = DashboardsApi(self.dd_api_client)
    self.monitors_api: MonitorsApi = MonitorsApi(self.dd_api_client)

    self.base_url: str = base_url.removesuffix("/")
    self.session: requests.Session = requests.Session()
    self.session.headers.update({
      "Accept": "application/json",
      "Content-Type": "application/json",
      "DD-API-KEY": dd_api_key,
    })
    if dd_application_key:
      self.session.headers.update({"DD-APPLICATION-KEY": dd_application_key})

  def create_api_model(self, data: dict, model_type: Type[OpenApiModelType], check_type: bool = True) -> OpenApiModelType:
    return deserialize_model(data, model_type, [], check_type, self.dd_api_client.configuration, True)

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

  def get_monitors(self, monitor_tags: Optional[str] = None) -> List[dict]:
    params = {}
    if monitor_tags:
      params["monitor_tags"] = monitor_tags

    return requests_helper.maybe_throw(self.session.get(self.url("/monitor"), params=params)).json()

  def update_monitor(self, monitor_id: int, monitor: dict) -> Monitor:
    return self.monitors_api.update_monitor(monitor_id, self.create_api_model(monitor, MonitorUpdateRequest))
