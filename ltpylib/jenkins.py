#!/usr/bin/env python
import re
from typing import Sequence, Tuple

JENKINS_JOB_URL_REGEX: str = r'^(https?):\/\/([^\/:]+)(:[0-9]+)?(?:\/)(?:job|blue\/organizations\/jenkins)\/(([^\/]+)(?:\/(?:job|detail)\/([^\/]+))?)\/([0-9]+)\/' \
                             r'(?:pipeline\/?|display\/redirect)?$'


def create_recursive_tree_param(container: str, fields: Sequence[str], depth: int) -> str:
  tree_param = f"{container}[{','.join(fields)}"
  start_tree = tree_param
  end_tree = "]"
  for idx in range(depth):
    start_tree += "," + tree_param
    end_tree += "]"

  return start_tree + end_tree


def parse_job_url(url: str) -> Tuple[str, int]:
  match = re.match(JENKINS_JOB_URL_REGEX, url)
  job_name = match.group(5)
  if match.group(6) and match.group(5) != match.group(6):
    job_name = job_name + "/job/" + match.group(6)

  job_num = int(match.group(7))

  return job_name, job_num
