#!/usr/bin/env python3
import subprocess
from pathlib import Path
from typing import List, Tuple, Union

from ltpylib import procs, xmlparser

MVN_EXPR_PROJECT_GROUP_ID = 'project.groupId'
MVN_EXPR_PROJECT_ARTIFACT_ID = 'project.artifactId'
MVN_EXPR_PROJECT_VERSION = 'project.version'


class MavenArtifact(object):

  def __init__(self, group_id: str, artifact_id: str, version: str = None, packaging: str = None, classifier: str = None):
    self.group_id: str = group_id
    self.artifact_id: str = artifact_id
    self.version: str = version
    self.packaging: str = packaging
    self.classifier: str = classifier

  def to_artifact_string(self) -> str:
    parts: List[str] = [
      self.group_id,
      self.artifact_id,
    ]
    for val in [self.version, self.packaging, self.classifier]:
      if val:
        parts.append(val)

    return ":".join(parts)

  @staticmethod
  def from_artifact_string(artifact: str):
    artifact_parts = artifact.split(":")

    parts_len = len(artifact_parts)
    if parts_len < 2:
      raise Exception("Artifact should be in the form of groupId:artifactId:version[:packaging[:classifier]]")

    return MavenArtifact(
      artifact_parts[0],
      artifact_parts[1],
      version=(artifact_parts[2] if parts_len > 2 else None),
      packaging=(artifact_parts[3] if parts_len > 3 else None),
      classifier=(artifact_parts[4] if parts_len > 4 else None),
    )


def get_artifact_repository_path(artifact: Union[MavenArtifact, str]) -> Path:
  import os

  if isinstance(artifact, str):
    artifact = MavenArtifact.from_artifact_string(artifact)

  return Path(os.getenv("HOME")).joinpath(".m2/repository").joinpath(artifact.group_id.replace(".", "/")).joinpath(artifact.artifact_id)


def get_project_artifact_id(pom: Union[str, Path], use_mvn_expression: bool = False) -> str:
  result: str = None

  if not use_mvn_expression:
    result = xmlparser.parse_xml(pom).findtext('artifactId')

  if use_mvn_expression or not result:
    result = run_mvn_expression(pom, MVN_EXPR_PROJECT_ARTIFACT_ID)

  return result


def get_project_group_id(pom: Union[str, Path], use_mvn_expression: bool = False) -> str:
  result: str = None

  if not use_mvn_expression:
    parsed = xmlparser.parse_xml(pom)
    result = parsed.findtext('groupId')
    if not result:
      result = parsed.findtext('./parent/groupId')

  if use_mvn_expression or not result:
    result = run_mvn_expression(pom, MVN_EXPR_PROJECT_GROUP_ID)

  return result


def get_project_version(pom: Union[str, Path], use_mvn_expression: bool = False) -> str:
  result: str = None

  if not use_mvn_expression:
    parsed = xmlparser.parse_xml(pom)
    result = parsed.findtext('version')
    if not result:
      result = parsed.findtext('./parent/version')

  if use_mvn_expression or not result:
    result = run_mvn_expression(pom, MVN_EXPR_PROJECT_VERSION)

  return result


def parse_mvn_expression_output(mvn_out: str) -> str:
  return [line for line in mvn_out.splitlines() if '[INFO]' not in line][-1]


def run_mvn_expression(pom: Union[str, Path], expression: str) -> str:
  if isinstance(pom, str):
    pom = Path(pom)

  mvn_out = procs.run_and_parse_output(
    ['mvn', '-f', pom.absolute().as_posix(), 'help:evaluate', '-Dexpression={0}'.format(expression), '--quiet', '-DforceStdout'],
    check=True,
  )[1].strip()
  return mvn_out


def update_dep_version(pom: Union[str, Path], dep: str, version: str, additional_arguments: List[str] = None, check: bool = False) -> subprocess.CompletedProcess:
  if isinstance(pom, str):
    pom = Path(pom)

  if dep.count(':') <= 1:
    dep += ':*'

  mvn_command = [
    'mvn',
    '-f',
    pom.absolute().as_posix(),
    'versions:use-dep-version',
    '-DdepVersion=%s' % version,
    '-DgenerateBackupPoms=false',
    '-Dincludes=%s' % dep,
    '-DallowSnapshots=true',
  ]
  if additional_arguments:
    mvn_command.extend(additional_arguments)

  return procs.run(mvn_command, check=check)


def update_project_version(pom: Union[str, Path], version: str, additional_arguments: List[str] = None, check: bool = False) -> Tuple[int, str]:
  if isinstance(pom, str):
    pom = Path(pom)

  mvn_command = [
    'mvn',
    '-f',
    pom.absolute().as_posix(),
    'versions:set',
    '-DgenerateBackupPoms=false',
    '-DnewVersion=' + version,
  ]
  if additional_arguments:
    mvn_command.extend(additional_arguments)

  return procs.run_and_parse_output(mvn_command, check=check)


def _main():
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)


if __name__ == "__main__":
  try:
    _main()
  except KeyboardInterrupt:
    exit(130)
