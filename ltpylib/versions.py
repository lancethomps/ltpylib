#!/usr/bin/env python
import semver


class LenientVersionInfo(semver.VersionInfo):

  def __init__(self, major: int, minor: int = 0, patch: int = 0, prerelease: str = None, build: str = None, original_version: str = None):
    self.original_version: str = original_version
    semver.VersionInfo.__init__(self, major, minor, patch, prerelease, build)
    self.version: str = self.__str__()

  @staticmethod
  def make_version_semantic(version: str) -> str:
    dot_count = version.count(".")
    if dot_count <= 0:
      version = version + ".0.0"
    elif dot_count <= 1:
      version = version + ".0"

    return version

  @staticmethod
  def parse_lenient(original_version: str) -> 'LenientVersionInfo':
    version = LenientVersionInfo.make_version_semantic(original_version)

    prerelease = None
    try:
      parsed = semver.VersionInfo.parse(version)
      prerelease = parsed.prerelease
    except ValueError:
      parts = original_version.split(".")
      if len(parts) > 3:
        prerelease = ".".join(parts[3:])
      elif "-" in original_version:
        main_part, prerelease = original_version.split("-", maxsplit=1)
        parts = LenientVersionInfo.make_version_semantic(main_part).split(".")
      else:
        raise

      parsed = semver.VersionInfo.parse(".".join(parts[:3]))

    return LenientVersionInfo(
      parsed.major,
      minor=parsed.minor,
      patch=parsed.patch,
      prerelease=prerelease,
      build=parsed.build,
      original_version=original_version,
    )


def parse_semver_lenient(version: str) -> LenientVersionInfo:
  return LenientVersionInfo.parse_lenient(version)
