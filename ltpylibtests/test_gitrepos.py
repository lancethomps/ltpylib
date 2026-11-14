#!/usr/bin/env python
import subprocess
import tempfile
import unittest
from pathlib import Path

from ltpylib import gitrepos


def _git(*args: str, cwd: Path):
  subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class TestGitRepos(unittest.TestCase):

  def setUp(self):
    self._tmp = tempfile.TemporaryDirectory()
    self.base_dir = Path(self._tmp.name).resolve()
    self.repo = self.base_dir.joinpath("repos", "repo1")
    self.repo.mkdir(parents=True)
    _git("init", "-q", cwd=self.repo)
    _git("-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-q", "--allow-empty", "-m", "init", cwd=self.repo)
    self.worktree = self.base_dir.joinpath("worktrees", "repo1-wt")
    _git("worktree", "add", "-q", "-b", "wt-branch", self.worktree.as_posix(), cwd=self.repo)

  def tearDown(self):
    self._tmp.cleanup()

  def test_parse_worktree_list_porcelain_returns_all_worktree_paths(self):
    output = "worktree /a/main\nHEAD abc\nbranch refs/heads/main\n\nworktree /b/linked\nHEAD def\ndetached\n"
    assert gitrepos.parse_worktree_list_porcelain(output) == [Path("/a/main"), Path("/b/linked")]

  def test_parse_worktree_list_porcelain_empty_output(self):
    assert gitrepos.parse_worktree_list_porcelain("") == []

  def test_list_linked_worktrees_excludes_main_worktree(self):
    assert gitrepos.list_linked_worktrees(self.repo) == [self.worktree]

  def test_list_linked_worktrees_skips_missing_worktree_dirs(self):
    subprocess.run(["rm", "-rf", self.worktree.as_posix()], check=True)
    assert gitrepos.list_linked_worktrees(self.repo) == []

  def test_list_linked_worktrees_non_repo_returns_empty(self):
    assert gitrepos.list_linked_worktrees(self.base_dir.joinpath("worktrees")) == []

  def test_add_git_dirs_excludes_worktrees_by_default(self):
    assert gitrepos.add_git_dirs([], [self.base_dir.joinpath("repos")]) == [self.repo]

  def test_add_git_dirs_includes_worktrees_when_enabled(self):
    assert gitrepos.add_git_dirs([], [self.base_dir.joinpath("repos")], include_worktrees=True) == [self.repo, self.worktree]

  def test_add_git_dirs_does_not_apply_patterns_to_worktrees(self):
    result = gitrepos.add_git_dirs([], [self.base_dir.joinpath("repos")], exclude_patterns=["-wt$"], include_worktrees=True)
    assert result == [self.repo, self.worktree]

  def test_add_git_dirs_skips_worktrees_of_excluded_repos(self):
    result = gitrepos.add_git_dirs([], [self.base_dir.joinpath("repos")], exclude_patterns=["repo1$"], include_worktrees=True)
    assert result == []

  def test_add_git_dirs_skips_worktrees_already_present(self):
    result = gitrepos.add_git_dirs([self.worktree], [self.base_dir.joinpath("repos")], include_worktrees=True)
    assert result == [self.worktree, self.repo]


if __name__ == '__main__':
  unittest.main()
