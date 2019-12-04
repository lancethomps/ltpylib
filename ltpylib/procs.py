#!/usr/bin/env python3
import collections
import logging
import subprocess
import sys
from typing import Any, List, Tuple

import psutil
from psutil import AccessDenied, NoSuchProcess, ZombieProcess
from time import sleep


def run(*popenargs, input=None, timeout=None, check=False, **kwargs) -> subprocess.CompletedProcess:
  kwargs['universal_newlines'] = True
  if 'stdout' not in kwargs:
    kwargs['stdout'] = subprocess.PIPE
  if 'stderr' not in kwargs:
    kwargs['stderr'] = subprocess.PIPE

  return subprocess.run(*popenargs, input=input, timeout=timeout, check=check, **kwargs)


def run_with_regular_stdout(*popenargs, input=None, timeout=None, check=False, **kwargs) -> subprocess.CompletedProcess:
  return run(*popenargs, input=input, timeout=timeout, check=check, stdout=sys.stdout, stderr=sys.stderr, **kwargs)


def run_and_parse_output(*popenargs, input=None, timeout=None, check=False, **kwargs) -> Tuple[int, str]:
  kwargs['stdout'] = subprocess.PIPE
  kwargs['universal_newlines'] = True
  if 'stderr' not in kwargs:
    kwargs['stderr'] = subprocess.PIPE

  result = subprocess.run(*popenargs, input=input, timeout=timeout, check=check, **kwargs)
  return result.returncode, result.stdout


def get_procs_from_name(name_matcher: str) -> List[Tuple[int, str]]:
  matched_procs = []
  exit_code, output = run_and_parse_output(['pgrep', '-fl', name_matcher])
  if exit_code > 0:
    return matched_procs

  for line in output.splitlines():
    parts = line.partition(' ')
    matched_procs.append((int(parts[0]), parts[2]))

  return matched_procs


def proc_debug_string(proc: psutil.Process) -> str:
  info = collections.OrderedDict()
  info['pid'] = proc.pid
  try:
    info["name"] = proc.name()
    if proc._create_time:
      info['started'] = psutil._pprint_secs(proc._create_time)
  except ZombieProcess:
    info["status"] = "zombie"
  except NoSuchProcess:
    info["status"] = "terminated"
  except AccessDenied:
    pass
  info['cmdline'] = ' '.join(proc.cmdline())
  return "%s.%s(%s)" % (
    proc.__class__.__module__,
    proc.__class__.__name__,
    ", ".join(["%s=%r" % (k, v) for k, v in info.items()]),
  )


def stop_proc_by_name(name_matcher: str) -> bool:
  matched_procs = get_procs_from_name(name_matcher)
  if not matched_procs:
    return False

  if len(matched_procs) > 1:
    raise Exception('Multiple processes found: %s' % matched_procs)

  proc = psutil.Process(matched_procs[0][0])
  proc.terminate()
  return True


def stop_proc_by_pid(pid: Any) -> bool:
  proc = psutil.Process(int(pid))
  if proc.is_running():
    proc.terminate()
  else:
    return False
  return True


def await_termination(pid: int, timeout: int = 30, sleep_time: int = 1, log_level: int = logging.INFO):
  if pid is None:
    return

  proc = psutil.Process(pid)
  total_time = 0
  while total_time <= timeout:
    if proc.is_running():
      logging.log(log_level, 'STATUS: loop %s seconds - process is still running, please wait...', total_time)
    else:
      break

    total_time += sleep_time
    sleep(sleep_time)

  if proc.is_running():
    logging.error('STATUS: Process still running after %s seconds, sending SIGKILL to terminate...', total_time)
    proc.kill()
    proc.wait(5)
    logging.log(log_level, 'STATUS: Process killed.')
  else:
    logging.log(log_level, 'STATUS: Process successfully shutdown after %s seconds.', total_time)


if __name__ == "__main__":
  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
