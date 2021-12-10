#!/usr/bin/env python
from typing import Any, List, Optional, Tuple

import jenkinsapi
import requests
from requests import Session

from ltpylib import output, requests_helper
from ltpylib.jenkins import create_recursive_tree_param
from ltpylib.jenkins_types import JenkinsBuild, JenkinsInstance


class JenkinsApi(object):

  def __init__(self, base_url: str, creds: Tuple[str, str]):
    if base_url.endswith("/"):
      self.base_url: str = base_url[:-1]
    else:
      self.base_url: str = base_url

    self.creds: Tuple[str, str] = creds
    self.session: Session = requests.Session()

    self.session.verify = True
    if creds is not None:
      self.session.auth = creds

    self.session.cookies = self.session.head(self.url("")).cookies
    self.session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

    self._api: Optional[jenkinsapi.jenkins.Jenkins] = None

  @property
  def api(self) -> jenkinsapi.jenkins.Jenkins:
    if not self._api:
      self._api = jenkinsapi.jenkins.Jenkins(
        self.base_url,
        username=self.creds[0] if self.creds else None,
        password=self.creds[1] if self.creds else None,
        lazy=True,
      )

    return self._api

  def url(self, resource_path: str):
    if not resource_path.startswith("/"):
      resource_path = "/" + resource_path
    return self.base_url + resource_path

  def all_builds(
    self,
    job: str,
    tree: str = "building,description,displayName,duration,estimatedDuration,executor,id,number,queueId,result,timestamp,url",
  ) -> List[JenkinsBuild]:
    response = self.session.get(self.url("job/%s/api/json?tree=%s" % (
      job,
      "allBuilds[%s]" % tree,
    )))
    return [JenkinsBuild(values=v) for v in requests_helper.parse_raw_response(response).get("allBuilds")]

  def build(
    self,
    job: str,
    build: int,
  ) -> JenkinsBuild:
    response = self.session.get(self.url("job/%s/%s/api/json?tree=*" % (job, str(build))))
    return JenkinsBuild(requests_helper.parse_raw_response(response))

  def instance_info(self, tree: str = "*") -> JenkinsInstance:
    response = self.session.get(self.url("api/json?tree=%s" % tree))
    return JenkinsInstance(requests_helper.parse_raw_response(response))

  def instance_info_all_jobs(
    self,
    fields: List[str] = ("color", "name", "url"),
    depth: int = 10,
  ) -> JenkinsInstance:
    return self.instance_info(tree=create_recursive_tree_param("jobs", fields, depth))

  def job(self, job_url_or_path: str) -> jenkinsapi.job.Job:
    job_url = job_url_or_path if job_url_or_path.startswith(self.base_url) else f"{self.base_url}/job/{job_url_or_path}"
    job_name = jenkinsapi.job.Job.get_full_name_from_url_and_baseurl(job_url, self.base_url)
    return self.api.get_job_by_url(job_url, job_name)


def jenkinsapi_dumper(val: Any) -> Any:
  return val._data


def jenkinsapi_dumper_use_if(val: Any) -> bool:
  return isinstance(val, jenkinsapi.jenkinsbase.JenkinsBase)


output.add_custom_json_dumper("jenkinsapi", jenkinsapi_dumper, use_if=jenkinsapi_dumper_use_if)
