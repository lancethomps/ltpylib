#!/usr/bin/env python3
from datetime import datetime
from typing import Dict, List

from ltpylib import dates
from ltpylib.common_types import DataWithUnknownPropertiesAsAttributes


class IdAndSelf(object):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.id: int = int(values.pop("id")) if "id" in values else None
    self.self: str = values.pop("self", None)


class ValueIdAndSelf(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.value: str = values.pop("value", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class Issue(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.aggregateprogress: Dict[str, int] = values.pop("aggregateprogress", None)
    self.cashScrumTeam: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("cashScrumTeam")) if "cashScrumTeam" in values else None
    self.comment: Dict[str, int] = values.pop("comment", None)
    self.controlGroup: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("controlGroup")) if "controlGroup" in values else None
    self.created: datetime = dates.parse_iso_date(values.pop("created")) if "created" in values else None
    self.creator: JiraUser = JiraUser(values=values.pop("creator")) if "creator" in values else None
    self.development: str = values.pop("development", None)
    self.epicLink: str = values.pop("epicLink", None)
    self.expand: str = values.pop("expand", None)
    self.issuetype: dict = values.pop("issuetype", None)
    self.key: str = values.pop("key", None)
    self.labels: List[str] = values.pop("labels", None)
    self.names: Dict[str, str] = values.pop("names", None)
    self.onsite: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("onsite")) if "onsite" in values else None
    self.priority: dict = values.pop("priority", None)
    self.progress: Dict[str, int] = values.pop("progress", None)
    self.project: JiraProject = JiraProject(values=values.pop("project")) if "project" in values else None
    self.rank: str = values.pop("rank", None)
    self.reporter: JiraUser = JiraUser(values=values.pop("reporter")) if "reporter" in values else None
    self.sprint: str = values.pop("sprint", None)
    self.sprintFinal: str = values.pop("sprintFinal", None)
    self.sprintRaw: List[str] = values.pop("sprintRaw", None)
    self.status: JiraStatus = JiraStatus(values=values.pop("status")) if "status" in values else None
    self.summary: str = values.pop("summary", None)
    self.thirdPartyType: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("thirdPartyType")) if "thirdPartyType" in values else None
    self.timetracking: dict = values.pop("timetracking", None)
    self.updated: datetime = dates.parse_iso_date(values.pop("updated")) if "updated" in values else None
    self.userType: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("userType")) if "userType" in values else None
    self.votes: dict = values.pop("votes", None)
    self.watches: dict = values.pop("watches", None)
    self.worklog: dict = values.pop("worklog", None)
    self.workratio: int = values.pop("workratio", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueSearchResult(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.expand: str = values.pop("expand", None)
    self.issues: List[Issue] = list(map(Issue, values.pop("issues", []))) if "issues" in values else None
    self.maxResults: int = values.pop("maxResults", None)
    self.names: Dict[str, str] = values.pop("names", None)
    self.startAt: int = values.pop("startAt", None)
    self.total: int = values.pop("total", None)

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class JiraProject(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.avatarUrls: dict = values.pop("avatarUrls", None)
    self.key: str = values.pop("key", None)
    self.name: str = values.pop("name", None)
    self.projectTypeKey: str = values.pop("projectTypeKey", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class JiraStatus(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.description: str = values.pop("description", None)
    self.iconUrl: str = values.pop("iconUrl", None)
    self.name: str = values.pop("name", None)
    self.statusCategory: dict = values.pop("statusCategory", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class JiraUser(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.active: bool = values.pop("active", None)
    self.avatarUrls: dict = values.pop("avatarUrls", None)
    self.displayName: str = values.pop("displayName", None)
    self.emailAddress: str = values.pop("emailAddress", None)
    self.key: str = values.pop("key", None)
    self.name: str = values.pop("name", None)
    self.self: str = values.pop("self", None)
    self.timeZone: str = values.pop("timeZone", None)

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)
