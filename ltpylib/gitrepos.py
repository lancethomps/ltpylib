#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path
from typing import IO, List, Optional, Sequence, Union

from ltpylib import files, filters, procs

FIND_REPOS_RECURSION_EXCLUDES = frozenset([
  'node_modules',
])


def create_git_cmd(
  git_args: Union[str, List[str]],
) -> List[str]:
  git_cmd = ["git"]
  if isinstance(git_args, str):
    git_cmd.append(git_args)
  else:
    git_cmd.extend(git_args)

  return git_cmd


def run_git_cmd(
  git_args: Union[str, List[str]],
  cwd: Union[Path, str] = os.getcwd(),
  check: bool = True,
  stderr: Optional[Union[int, IO]] = sys.stderr,
  log_cmd: bool = False,
) -> subprocess.CompletedProcess:
  return procs.run(create_git_cmd(git_args), check=check, cwd=cwd, stderr=stderr, log_cmd=log_cmd)


def run_git_cmd_stdout(
  git_args: Union[str, List[str]],
  cwd: Union[Path, str] = os.getcwd(),
  check: bool = True,
  stderr: Optional[Union[int, IO]] = sys.stderr,
  log_cmd: bool = False,
  strip: bool = True,
) -> str:
  result = run_git_cmd(git_args, cwd=cwd, check=check, stderr=stderr, log_cmd=log_cmd)

  if strip and result.stdout:
    return result.stdout.strip()

  return result.stdout


def run_git_cmd_regular_stdout(
  git_args: Union[str, List[str]],
  cwd: Union[Path, str] = os.getcwd(),
  check: bool = True,
  log_cmd: bool = False,
  **kwargs,
) -> subprocess.CompletedProcess:
  return procs.run_with_regular_stdout(create_git_cmd(git_args), cwd=cwd, check=check, log_cmd=log_cmd, **kwargs)


def base_dir(cwd: Union[Path, str] = os.getcwd()) -> Path:
  return Path(run_git_cmd_stdout("base-dir", cwd=cwd))


def current_branch(cwd: Union[Path, str] = os.getcwd()) -> str:
  return run_git_cmd_stdout("current-branch", cwd=cwd)


def default_branch(cwd: Union[Path, str] = os.getcwd()) -> str:
  return run_git_cmd_stdout("default-branch", cwd=cwd)


def repo_name(cwd: Union[Path, str] = os.getcwd()) -> str:
  return run_git_cmd_stdout("repo-name", cwd=cwd)


def repo_name_with_owner(cwd: Union[Path, str] = os.getcwd()) -> str:
  return run_git_cmd_stdout("repo-name-with-owner", cwd=cwd)


def repo_owner(cwd: Union[Path, str] = os.getcwd()) -> str:
  return run_git_cmd_stdout("repo-owner", cwd=cwd)


def in_repo(cwd: Union[Path, str] = os.getcwd()) -> bool:
  return run_git_cmd("in-repo", cwd=cwd).returncode == 0


def diff_show(
  cwd: Union[Path, str] = os.getcwd(),
  diff_file: Union[Path, str] = None,
  diff_to_head: bool = True,
  log_cmd: bool = False,
) -> bool:
  git_args = ["--no-pager", "diff"]

  if diff_to_head:
    git_args.append("HEAD")

  if diff_file:
    diff_file_path = files.convert_to_path(diff_file)
    git_args.append(diff_file_path.relative_to(cwd).as_posix() if diff_file_path.is_absolute() else diff_file_path.as_posix())

  return run_git_cmd_regular_stdout(git_args, cwd=cwd, check=False, log_cmd=log_cmd).returncode == 1


def commit_show(
  message: str,
  cwd: Union[Path, str] = os.getcwd(),
  repo_files: Sequence[Union[Path, str]] = None,
  add_first: bool = True,
  check: bool = True,
  log_cmd: bool = False,
) -> subprocess.CompletedProcess:
  file_args = [files.convert_to_path(f).relative_to(cwd).as_posix() for f in repo_files if f] if repo_files else []
  if add_first:
    run_git_cmd_regular_stdout(["add"] + file_args, cwd=cwd, check=check, log_cmd=log_cmd)

  return run_git_cmd_regular_stdout(["commit", "-m", message] + file_args, cwd=cwd, check=check, log_cmd=log_cmd)


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


def is_valid_repo(repo: Path) -> bool:
  if not repo.is_dir():
    return False

  if repo.joinpath('.git').is_dir():
    return True

  return in_repo(repo)


def filter_invalid_repos(git_repos: List[Path]) -> List[Path]:
  filtered = []
  for repo in git_repos:
    if not is_valid_repo(repo):
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
