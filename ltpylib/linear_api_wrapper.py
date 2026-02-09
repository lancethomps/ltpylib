#!/usr/bin/env python
from linear_api import LinearClient, LinearIssue


class LinearApi(object):

  def __init__(
    self,
    api_key: str = None,
    api: LinearClient = None,
  ):
    if api is not None:
      self.api: LinearClient = api
    else:
      self.api: LinearClient = LinearClient(api_key=api_key)

  def issue(self, issue_id: str) -> LinearIssue:
    return self.api.issues.get(issue_id)


def _main():
  import sys
  from ltpylib import output

  api = LinearApi()
  result = getattr(api, sys.argv[1])(*sys.argv[2:])
  if result is not None:
    print(output.prettify_json_auto_color(result, remove_nulls=True))


if __name__ == "__main__":
  try:
    _main()
  except KeyboardInterrupt:
    exit(130)
