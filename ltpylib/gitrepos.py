#!/usr/bin/env python
import os
from pathlib import Path
from typing import List, Optional, Sequence

from ltpylib import files, filters

FIND_REPOS_RECURSION_EXCLUDES = frozenset([
  'node_modules',
])


def is_file_part_of_git_repo(file_path: Path) -> bool:
  return git_repo_root_for_file(file_path) is not None


def git_repo_root_for_file(file_path: Path) -> Optional[Path]:
  if file_path.is_dir() and file_path.joinpath(".git").is_dir():
    return file_path

  for parent_file in file_path.parents:
    if parent_file.joinpath(".git").is_dir():
      return parent_file

  return None


def resolve_file_relative_to_git_base_dir(file_path: Path, current_dir: Path = Path(os.getcwd())) -> Optional[Path]:
  git_repo_root = git_repo_root_for_file(current_dir)
  if not git_repo_root:
    return None

  maybe_file = git_repo_root.joinpath(file_path)
  return maybe_file if maybe_file.exists() else None


def filter_invalid_repos(git_repos: List[Path]) -> List[Path]:
  filtered = []
  for repo in git_repos:
    if not repo.is_dir():
      continue

    if not repo.joinpath('.git').is_dir():
      continue

    filtered.append(repo)

  return filtered


def print_repos(git_repos: List[Path]):
  for repo in git_repos:
    print(repo.as_posix())


def find_git_repos(
  base_dir: Path,
  max_depth: int = -1,
  recursion_include_patterns: Sequence[str] = None,
  recursion_exclude_patterns: Sequence[str] = None,
  recursion_includes: Sequence[str] = None,
  recursion_excludes: Sequence[str] = FIND_REPOS_RECURSION_EXCLUDES
) -> List[Path]:
  dotgit_dirs = files.find_children(
    base_dir,
    break_after_match=True,
    include_files=False,
    max_depth=max_depth,
    includes=['.git'],
    recursion_include_patterns=recursion_include_patterns,
    recursion_exclude_patterns=recursion_exclude_patterns,
    recursion_includes=recursion_includes,
    recursion_excludes=recursion_excludes
  )
  return [dotgit.parent for dotgit in dotgit_dirs]


def add_git_dirs(
  git_repos: List[Path],
  add_dir: List[Path],
  include_patterns: List[str] = None,
  exclude_patterns: List[str] = None,
  max_depth: int = -1,
  recursion_include_patterns: Sequence[str] = None,
  recursion_exclude_patterns: Sequence[str] = None,
  recursion_includes: Sequence[str] = None,
  recursion_excludes: Sequence[str] = FIND_REPOS_RECURSION_EXCLUDES
) -> List[Path]:
  for git_dir in add_dir:
    if not git_dir.is_dir():
      continue

    add_dir_repos = find_git_repos(
      git_dir,
      max_depth=max_depth,
      recursion_include_patterns=recursion_include_patterns,
      recursion_exclude_patterns=recursion_exclude_patterns,
      recursion_includes=recursion_includes,
      recursion_excludes=recursion_excludes
    )
    add_dir_repos.sort()
    for git_repo in add_dir_repos:
      if filters.should_skip(git_repo, exclude_patterns=exclude_patterns, include_patterns=include_patterns):
        continue

      if git_repo in git_repos:
        continue

      git_repos.append(git_repo)

  return git_repos
