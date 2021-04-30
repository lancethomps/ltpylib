#!/usr/bin/env python
from enum import auto

from datetime import datetime
from typing import Dict, List, Optional

from ltpylib import dates, enums
from ltpylib.common_types import DataWithUnknownPropertiesAsAttributes


class IdAndSelf(object):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.id: int = int(values.pop("id")) if "id" in values else None
    self.self: str = values.pop("self", None)


class NameIdAndSelf(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.name: str = values.pop("name", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class ValueIdAndSelf(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.value: str = values.pop("value", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class TextAndValue(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.text: str = values.pop("text", None)
    self.value: float = float(values.pop("value")) if "value" in values else None

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class FixVersion(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.archived: bool = values.pop("archived", None)
    self.name: str = values.pop("name", None)
    self.released: bool = values.pop("released", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class Issue(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.acceptanceCriteria: str = values.pop("acceptanceCriteria", None)
    self.aggregateprogress: Dict[str, int] = values.pop("aggregateprogress", None)
    self.aggregatetimeestimate: int = values.pop("aggregatetimeestimate", None)
    self.aggregatetimeoriginalestimate: int = values.pop("aggregatetimeoriginalestimate", None)
    self.aggregatetimespent: int = values.pop("aggregatetimespent", None)
    self.assignee: JiraUser = JiraUser(values=values.pop("assignee")) if "assignee" in values else None
    self.attachment: List[dict] = values.pop("attachment", None)
    self.cashScrumTeam: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("cashScrumTeam")) if "cashScrumTeam" in values else None
    self.comment: Dict[str, int] = values.pop("comment", None)
    self.components: List[NameIdAndSelf] = list(map(NameIdAndSelf, values.pop("components", []))) if "components" in values else None
    self.controlGroup: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("controlGroup")) if "controlGroup" in values else None
    self.created: datetime = dates.parse_iso_date(values.pop("created")) if "created" in values else None
    self.creator: JiraUser = JiraUser(values=values.pop("creator")) if "creator" in values else None
    self.description: str = values.pop("description", None)
    self.development: str = values.pop("development", None)
    self.epicColour: str = values.pop("epicColour", None)
    self.epicLink: str = values.pop("epicLink", None)
    self.epicName: str = values.pop("epicName", None)
    self.epicStatus: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("epicStatus")) if "epicStatus" in values else None
    self.expand: str = values.pop("expand", None)
    self.fixVersions: List[FixVersion] = list(map(FixVersion, values.pop("fixVersions", []))) if "fixVersions" in values else None
    self.issuelinks: List[IssueLink] = list(map(IssueLink, values.pop("issuelinks", []))) if "issuelinks" in values else None
    self.issuetype: IssueType = IssueType(values=values.pop("issuetype")) if "issuetype" in values else None
    self.key: str = values.pop("key", None)
    self.labels: List[str] = values.pop("labels", None)
    self.lastViewed: datetime = dates.parse_date(values.pop("lastViewed")) if "lastViewed" in values else None
    self.names: Dict[str, str] = values.pop("names", None)
    self.onsite: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("onsite")) if "onsite" in values else None
    self.parent: IssueBasic = IssueBasic(values=values.pop("parent")) if "parent" in values else None
    self.planned: List[ValueIdAndSelf] = list(map(ValueIdAndSelf, values.pop("planned", []))) if "planned" in values else None
    self.priority: dict = values.pop("priority", None)
    self.progress: Dict[str, int] = values.pop("progress", None)
    self.project: JiraProject = JiraProject(values=values.pop("project")) if "project" in values else None
    self.rank: str = values.pop("rank", None)
    self.reporter: JiraUser = JiraUser(values=values.pop("reporter")) if "reporter" in values else None
    self.resolution: IssueResolution = IssueResolution(values=values.pop("resolution")) if "resolution" in values else None
    self.resolutiondate: datetime = dates.parse_date(values.pop("resolutiondate")) if "resolutiondate" in values else None
    self.sprint: str = values.pop("sprint", None)
    self.sprintFinal: str = values.pop("sprintFinal", None)
    self.sprintRaw: List[str] = values.pop("sprintRaw", None)
    self.status: JiraStatus = JiraStatus(values=values.pop("status")) if "status" in values else None
    self.storyPoints: float = values.pop("storyPoints", None)
    self.subtasks: List[IssueBasic] = list(map(IssueBasic, values.pop("subtasks", []))) if "subtasks" in values else None
    self.summary: str = values.pop("summary", None)
    self.testCases: str = values.pop("testCases", None)
    self.thirdPartyType: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("thirdPartyType")) if "thirdPartyType" in values else None
    self.timeestimate: int = values.pop("timeestimate", None)
    self.timeoriginalestimate: int = values.pop("timeoriginalestimate", None)
    self.timespent: int = values.pop("timespent", None)
    self.timetracking: dict = values.pop("timetracking", None)
    self.updated: datetime = dates.parse_iso_date(values.pop("updated")) if "updated" in values else None
    self.userType: ValueIdAndSelf = ValueIdAndSelf(values=values.pop("userType")) if "userType" in values else None
    self.votes: dict = values.pop("votes", None)
    self.watches: dict = values.pop("watches", None)
    self.worklog: dict = values.pop("worklog", None)
    self.workratio: int = values.pop("workratio", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueBasic(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    if "fields" in values:
      values.update(values.pop("fields"))

    self.issuetype: IssueType = IssueType(values=values.pop("issuetype")) if "issuetype" in values else None
    self.key: str = values.pop("key", None)
    self.priority: dict = values.pop("priority", None)
    self.status: JiraStatus = JiraStatus(values=values.pop("status")) if "status" in values else None
    self.summary: str = values.pop("summary", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueKeyAndValue(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.issueKey: str = values.pop("issueKey", None)
    self.value: float = float(values.pop("value")) if "value" in values else None

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueLink(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.inwardIssue: IssueBasic = IssueBasic(values=values.pop("inwardIssue")) if "inwardIssue" in values else None
    self.outwardIssue: IssueBasic = IssueBasic(values=values.pop("outwardIssue")) if "outwardIssue" in values else None
    self.type: IssueLinkType = IssueLinkType(values=values.pop("type")) if "type" in values else None

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueLinkType(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.inward: str = values.pop("inward", None)
    self.name: str = values.pop("name", None)
    self.outward: str = values.pop("outward", None)

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class IssueResolution(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.description: str = values.pop("description", None)
    self.name: str = values.pop("name", None)

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


class IssueType(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.avatarId: int = values.pop("avatarId", None)
    self.description: str = values.pop("description", None)
    self.iconUrl: str = values.pop("iconUrl", None)
    self.name: str = values.pop("name", None)
    self.subtask: bool = values.pop("subtask", None)

    IdAndSelf.__init__(self, values)
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


class SprintState(enums.EnumAutoName):
  ACTIVE = auto()
  CLOSED = auto()
  FUTURE = auto()

  @staticmethod
  def from_string(state: str) -> Optional['SprintState']:
    return SprintState[state.upper()] if state else None


class Sprint(IdAndSelf, DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.canUpdateSprint: bool = values.pop("canUpdateSprint", None)
    self.completeDate: datetime = dates.parse_date(values.pop("completeDate")) if "completeDate" in values else None
    self.daysRemaining: int = int(values.pop("daysRemaining")) if "daysRemaining" in values else None
    self.endDate: datetime = dates.parse_date(values.pop("endDate")) if "endDate" in values else None
    self.goal: str = values.pop("goal", None)
    self.linkedPagesCount: int = int(values.pop("linkedPagesCount")) if "linkedPagesCount" in values else None
    self.name: str = values.pop("name", None)
    self.originBoardId: int = int(values.pop("originBoardId")) if "originBoardId" in values else None
    self.sequence: int = int(values.pop("sequence")) if "sequence" in values else None
    self.startDate: datetime = dates.parse_date(values.pop("startDate")) if "startDate" in values else None
    self.state: SprintState = SprintState.from_string(values.pop("state")) if "state" in values else None

    IdAndSelf.__init__(self, values)
    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class SprintReportContents(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.allIssuesEstimateSum: TextAndValue = TextAndValue(values=values.pop("allIssuesEstimateSum")) if "allIssuesEstimateSum" in values else None
    self.completedIssues: List[dict] = values.pop("completedIssues", None)
    self.completedIssuesEstimateSum: TextAndValue = TextAndValue(values=values.pop("completedIssuesEstimateSum")) if "completedIssuesEstimateSum" in values else None
    self.completedIssuesInitialEstimateSum: TextAndValue = TextAndValue(
      values=values.pop("completedIssuesInitialEstimateSum")
    ) if "completedIssuesInitialEstimateSum" in values else None
    self.issueKeysAddedDuringSprint: Dict[str, bool] = values.pop("issueKeysAddedDuringSprint", None)
    self.issuesCompletedInAnotherSprint: List[dict] = values.pop("issuesCompletedInAnotherSprint", None)
    self.issuesCompletedInAnotherSprintEstimateSum: TextAndValue = TextAndValue(
      values=values.pop("issuesCompletedInAnotherSprintEstimateSum")
    ) if "issuesCompletedInAnotherSprintEstimateSum" in values else None
    self.issuesCompletedInAnotherSprintInitialEstimateSum: TextAndValue = TextAndValue(
      values=values.pop("issuesCompletedInAnotherSprintInitialEstimateSum")
    ) if "issuesCompletedInAnotherSprintInitialEstimateSum" in values else None
    self.issuesNotCompletedEstimateSum: TextAndValue = TextAndValue(values=values.pop("issuesNotCompletedEstimateSum")) if "issuesNotCompletedEstimateSum" in values else None
    self.issuesNotCompletedInCurrentSprint: List[dict] = values.pop("issuesNotCompletedInCurrentSprint", None)
    self.issuesNotCompletedInitialEstimateSum: TextAndValue = TextAndValue(
      values=values.pop("issuesNotCompletedInitialEstimateSum")
    ) if "issuesNotCompletedInitialEstimateSum" in values else None
    self.puntedIssues: List[str] = values.pop("puntedIssues", None)
    self.puntedIssuesEstimateSum: TextAndValue = TextAndValue(values=values.pop("puntedIssuesEstimateSum")) if "puntedIssuesEstimateSum" in values else None
    self.puntedIssuesInitialEstimateSum: TextAndValue = TextAndValue(values=values.pop("puntedIssuesInitialEstimateSum")) if "puntedIssuesInitialEstimateSum" in values else None

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class SprintReport(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.contents: SprintReportContents = SprintReportContents(values=values.pop("contents")) if "contents" in values else None
    self.lastUserToClose: str = values.pop("lastUserToClose", None)
    self.sprint: Sprint = Sprint(values=values.pop("sprint")) if "sprint" in values else None
    self.supportsPages: bool = values.pop("supportsPages", None)

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class VelocityReportStats(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.allConsideredIssueKeys: List[str] = values.pop("allConsideredIssueKeys", None)
    self.completed: TextAndValue = TextAndValue(values=values.pop("completed")) if "completed" in values else None
    self.completedEntries: List[IssueKeyAndValue] = list(map(IssueKeyAndValue, values.pop("completedEntries", []))) if "completedEntries" in values else None
    self.estimated: TextAndValue = TextAndValue(values=values.pop("estimated")) if "estimated" in values else None
    self.estimatedEntries: List[IssueKeyAndValue] = list(map(IssueKeyAndValue, values.pop("estimatedEntries", []))) if "estimatedEntries" in values else None

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)


class VelocityReport(DataWithUnknownPropertiesAsAttributes):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.sprints: List[Sprint] = list(map(Sprint, values.pop("sprints", []))) if "sprints" in values else None
    self.velocityStatEntries: Dict[str, VelocityReportStats] = dict((str(k), VelocityReportStats(values=v)) for (k, v) in values.pop("velocityStatEntries").items()
                                                                   ) if "velocityStatEntries" in values else None

    DataWithUnknownPropertiesAsAttributes.__init__(self, values)
