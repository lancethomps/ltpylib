#!/usr/bin/env python3
from typing import List, Tuple

import stashy
from requests import Response
from stashy.pullrequests import PullRequest, PullRequests
from stashy.repos import Repos

from ltpylib import requests_helper
from ltpylib.stash_types import Builds, PullRequestActivities, PullRequestMergeability, PullRequestMergeStatus, PullRequestStatus, Repository, SearchResults

STASH_URL: str = "https://stash.wlth.fr"


class StashApi(object):

  def __init__(self, stash: stashy.Stash):
    self.stash: stashy.Stash = stash

  def builds_for_commit(self, commit: str, limit: int = 1000) -> Builds:
    api_url = '%s/rest/build-status/latest/commits/%s?limit=%s' % (
      self.stash._client._base_url,
      commit,
      str(limit),
    )
    kw = requests_helper.add_json_headers()
    result: Builds = Builds(requests_helper.parse_raw_response(self.stash._client._session.get(api_url, **kw)))

    return result

  def create_pull_request(
      self,
      project: str,
      repo: str,
      from_ref: str,
      to_ref: str,
      title: str,
      description: str,
      reviewers: List[str],
  ) -> PullRequestStatus:
    prs: PullRequests = self.stash.projects[project].repos[repo].pull_requests
    response: dict = prs.create(
      title=title,
      fromRef=from_ref,
      toRef=to_ref,
      description=description,
      reviewers=reviewers,
    )

    return PullRequestStatus(response)

  def delete_pull_request_source_branch(
      self,
      project: str,
      repo: str,
      pr_id: int,
  ) -> Response:
    api_url = '%s/rest/pull-request-cleanup/latest/projects/%s/repos/%s/pull-requests/%s' % (
      self.stash._client._base_url,
      project,
      repo,
      str(pr_id),
    )
    kw = requests_helper.add_json_headers()
    response = self.stash._client._session.post(
      api_url,
      json={
        "deleteSourceRef": True,
        "retargetDependents": True,
      },
      **kw,
    )
    return response

  def merge_pull_request(
      self,
      project: str,
      repo: str,
      pr_id: int,
      delete_source_branch: bool = True,
      commit_message: str = "",
      version: int = None,
  ) -> PullRequestMergeStatus:
    pr: PullRequest = self.stash.projects[project].repos[repo].pull_requests[str(pr_id)]
    if version is None:
      pr_info = self.pull_request(project, repo, pr_id, include_merge_info=False)
      version = pr_info.version

    result: PullRequestMergeStatus = PullRequestMergeStatus(
      requests_helper.parse_raw_response(pr._client.post(pr.url("/merge"), data=dict(message=commit_message, version=version)))
    )
    if delete_source_branch and result.state == "MERGED":
      delete_source_branch_response = self.delete_pull_request_source_branch(project, repo, pr_id)
      result.sourceBranchDeleted = delete_source_branch_response.status_code == 200 or delete_source_branch_response.status_code == 204

    return result

  def pull_request(
      self,
      project: str,
      repo: str,
      pr_id: int,
      include_merge_info: bool = True,
      include_builds: bool = False,
  ) -> PullRequestStatus:
    pr: PullRequest = self.stash.projects[project].repos[repo].pull_requests[str(pr_id)]
    result: PullRequestStatus = PullRequestStatus(pr.get())
    if include_merge_info and result.open:
      merge_info = self.pull_request_merge_info(project, repo, pr_id)
      result.mergeInfo = merge_info

    if include_builds and result.fromRef and result.fromRef.latestCommit:
      builds = self.builds_for_commit(result.fromRef.latestCommit)
      result.builds = builds

    return result

  def pull_request_activities(
      self,
      project: str,
      repo: str,
      pr_id: int,
  ) -> PullRequestActivities:
    pr: PullRequest = self.stash.projects[project].repos[repo].pull_requests[str(pr_id)]
    result: PullRequestActivities = PullRequestActivities(requests_helper.parse_raw_response(pr._client.get(pr.url() + "/activities")))

    return result

  def pull_request_merge_info(
      self,
      project: str,
      repo: str,
      pr_id: int,
  ) -> PullRequestMergeability:
    pr: PullRequest = self.stash.projects[project].repos[repo].pull_requests[str(pr_id)]
    return PullRequestMergeability(pr.merge_info())

  def pull_requests(
      self,
      project: str,
      repo: str,
      direction: str = 'INCOMING',
      at: str = None,
      state: str = 'OPEN',
      order: str = None,
      author: str = None,
  ) -> List[PullRequestStatus]:
    prs: PullRequests = self.stash.projects[project].repos[repo].pull_requests
    return [PullRequestStatus(pr) for pr in prs.all(
      direction=direction,
      at=at,
      state=state,
      order=order,
      author=author,
    )]

  def repos_for_project(self, project: str) -> List[Repository]:
    repos: Repos = self.stash.projects[project].repos
    return [Repository(repo) for repo in repos.list()]

  def search(self, query: str, limit: int = 25) -> SearchResults:
    api_json = {
      "entities": {
        "code": {}
      },
      "limits": {
        "primary": limit
      },
      "query": query,
    }
    kw = requests_helper.add_json_headers()
    return SearchResults(requests_helper.parse_raw_response(self.stash._client._session.post(
      '%s/rest/search/latest/search' % self.stash._client._base_url,
      json=api_json,
      **kw,
    )))


def create_stash_api(url: str, creds: Tuple[str, str]) -> StashApi:
  return StashApi(stashy.connect(url, creds[0], creds[1]))
