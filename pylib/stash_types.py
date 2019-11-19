#!/usr/bin/env python3
from typing import List


class DataWithUnknownProperties(object):

  def __init__(self, values: dict = None):
    if values:
      self.unknownProperties: dict = values


class DisplayIdAndId(object):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.displayId: str = values.pop("displayId", None)
    self.id: str = values.pop("id", None)


class ApplicationProperties(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.buildDate: str = values.pop("buildDate", None)
    self.buildNumber: str = values.pop("buildNumber", None)
    self.displayName: str = values.pop("displayName", None)
    self.version: str = values.pop("version", None)

    DataWithUnknownProperties.__init__(self, values)


class Branch(DataWithUnknownProperties, DisplayIdAndId):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    DisplayIdAndId.__init__(self, values)

    self.isDefault: bool = values.pop("isDefault", None)
    self.latestChangeset: str = values.pop("latestChangeset", None)

    DataWithUnknownProperties.__init__(self, values)


class Comment(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.id: int = values.pop("id", None)
    self.text: str = values.pop("text", None)
    self.version: int = values.pop("version", None)

    DataWithUnknownProperties.__init__(self, values)


class Commit(DataWithUnknownProperties, DisplayIdAndId):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    DisplayIdAndId.__init__(self, values)

    DataWithUnknownProperties.__init__(self, values)


class Link(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.href: str = values.pop("href", None)
    self.name: str = values.pop("name", None)

    DataWithUnknownProperties.__init__(self, values)


class Links(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.clone: List[Link] = list(map(Link, values.pop("clone", []))) if "clone" in values else None
    self.self: List[Link] = list(map(Link, values.pop("self", []))) if "self" in values else None

    DataWithUnknownProperties.__init__(self, values)


class Project(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.description: str = values.pop("description", None)
    self.id: int = values.pop("id", None)
    self.key: str = values.pop("key", None)
    self.links: Links = Links(values=values.pop("links")) if "links" in values else None
    self.name: str = values.pop("name", None)
    self.owner: User = User(values=values.pop("owner")) if "owner" in values else None
    self.public: bool = values.pop("public", None)
    self.type: str = values.pop("type", None)

    DataWithUnknownProperties.__init__(self, values)


class PullRequestMergeability(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.canMerge: bool = values.pop("canMerge", None)
    self.conflicted: bool = values.pop("conflicted", None)
    self.outcome: str = values.pop("outcome", None)
    self.vetoes: List[PullRequestVeto] = list(map(PullRequestVeto, values.pop("vetoes", []))) if "vetoes" in values else None

    DataWithUnknownProperties.__init__(self, values)


class PullRequestParticipant(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.approved: bool = values.pop("approved", None)
    self.lastReviewedCommit: str = values.pop("lastReviewedCommit", None)
    self.role: str = values.pop("role", None)
    self.status: str = values.pop("status", None)
    self.user: User = User(values=values.pop("user")) if "user" in values else None

    DataWithUnknownProperties.__init__(self, values)


class PullRequestProperties(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.commentCount: int = values.pop("commentCount", None)
    self.mergeCommit: Commit = Commit(values=values.pop("mergeCommit")) if "mergeCommit" in values else None
    self.openTaskCount: int = values.pop("openTaskCount", None)
    self.resolvedTaskCount: int = values.pop("resolvedTaskCount", None)

    DataWithUnknownProperties.__init__(self, values)


class PullRequestRef(DataWithUnknownProperties, DisplayIdAndId):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    DisplayIdAndId.__init__(self, values)

    self.latestCommit: str = values.pop("latestCommit", None)
    self.repository: Repository = Repository(values=values.pop("repository")) if "repository" in values else None

    DataWithUnknownProperties.__init__(self, values)


class PullRequestStatus(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.author: PullRequestParticipant = PullRequestParticipant(values=values.pop("author")) if "author" in values else None
    self.closed: bool = values.pop("closed", None)
    self.createdDate: int = values.pop("createdDate", None)
    self.description: str = values.pop("description", None)
    self.fromRef: PullRequestRef = PullRequestRef(values=values.pop("fromRef")) if "fromRef" in values else None
    self.id: int = values.pop("id", None)
    self.links: Links = Links(values=values.pop("links")) if "links" in values else None
    self.locked: bool = values.pop("locked", None)
    self.open: bool = values.pop("open", None)
    self.outstandingTaskCount: int = values.pop("outstandingTaskCount", None)
    self.participants: List[PullRequestParticipant] = list(map(PullRequestParticipant, values.pop("participants", []))) if "participants" in values else None
    self.properties: PullRequestProperties = PullRequestProperties(values=values.pop("properties")) if "properties" in values else None
    self.reviewers: List[PullRequestParticipant] = list(map(PullRequestParticipant, values.pop("reviewers", []))) if "reviewers" in values else None
    self.state: str = values.pop("state", None)
    self.title: str = values.pop("title", None)
    self.toRef: PullRequestRef = PullRequestRef(values=values.pop("toRef")) if "toRef" in values else None
    self.updatedDate: int = values.pop("updatedDate", None)
    self.version: int = values.pop("version", None)
    self.mergeInfo: PullRequestMergeability = None

    DataWithUnknownProperties.__init__(self, values)


class PullRequestMergeStatus(PullRequestStatus):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.sourceBranchDeleted: bool = None

    PullRequestStatus.__init__(self, values)


class PullRequestVeto(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.detailedMessage: str = values.pop("detailedMessage", None)
    self.summaryMessage: str = values.pop("summaryMessage", None)

    DataWithUnknownProperties.__init__(self, values)


class Repository(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.forkable: bool = values.pop("forkable", None)
    self.id: int = values.pop("id", None)
    self.links: Links = Links(values=values.pop("links")) if "links" in values else None
    self.name: str = values.pop("name", None)
    self.origin: Repository = Repository(values=values.pop("origin")) if "origin" in values else None
    self.project: Project = Project(values=values.pop("project")) if "project" in values else None
    self.public: bool = values.pop("public", None)
    self.scmId: str = values.pop("scmId", None)
    self.slug: str = values.pop("slug", None)
    self.state: str = values.pop("state", None)
    self.statusMessage: str = values.pop("statusMessage", None)

    DataWithUnknownProperties.__init__(self, values)


class Tag(DataWithUnknownProperties, DisplayIdAndId):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    DisplayIdAndId.__init__(self, values)

    self.hash: str = values.pop("hash", None)
    self.latestChangeset: str = values.pop("latestChangeset", None)
    self.latestCommit: str = values.pop("latestCommit", None)

    DataWithUnknownProperties.__init__(self, values)


class User(DataWithUnknownProperties):

  def __init__(self, values: dict = None):
    values = values if values is not None else {}

    self.active: bool = values.pop("active", None)
    self.deletable: bool = values.pop("deletable", None)
    self.displayName: str = values.pop("displayName", None)
    self.emailAddress: str = values.pop("emailAddress", None)
    self.id: int = values.pop("id", None)
    self.lastAuthenticationTimestamp: int = values.pop("lastAuthenticationTimestamp", None)
    self.links: Links = Links(values=values.pop("links")) if "links" in values else None
    self.mutableDetails: bool = values.pop("mutableDetails", None)
    self.mutableGroups: bool = values.pop("mutableGroups", None)
    self.name: str = values.pop("name", None)
    self.slug: str = values.pop("slug", None)
    self.type: str = values.pop("type", None)

    DataWithUnknownProperties.__init__(self, values)
