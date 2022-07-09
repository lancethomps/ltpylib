#!/usr/bin/env python
import semver


class LenientVersionInfo(semver.VersionInfo):

  def __init__(self, major: int, minor: int = 0, patch: int = 0, prerelease: str = None, build: str = None, original_version: str = None):
    self.original_version: str = original_version
    semver.VersionInfo.__init__(self, major, minor, patch, prerelease, build)
    self.version: str = self.__str__()

  @staticmethod
  def parse_lenient(original_version: str) -> 'LenientVersionInfo':
    version = original_version
    if version.count(".") <= 0:
      version = version + ".0.0"
    elif version.count(".") <= 1:
      version = version + ".0"

    parsed = semver.parse_version_info(version)
    return LenientVersionInfo(
      parsed.major,
      minor=parsed.minor,
      patch=parsed.patch,
      prerelease=parsed.prerelease,
      build=parsed.build,
      original_version=original_version,
    )


def parse_semver_lenient(version: str) -> LenientVersionInfo:
  return LenientVersionInfo.parse_lenient(version)
