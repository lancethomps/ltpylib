#!/usr/bin/env python

from concurrent import futures
from typing import Callable, Iterable, List, TypeVar

T = TypeVar('T')
V = TypeVar('V')


def trap_pool_shutdown(pool: futures.Executor, wait: bool = False, cancel_futures: bool = True):
  import signal

  def shutdown_handler():
    pool.shutdown(wait=wait, cancel_futures=cancel_futures)

  signal.signal(signal.SIGINT, shutdown_handler)
  signal.signal(signal.SIGTERM, shutdown_handler)


def run_parallel(
  fn: Callable[[T], V],
  *iterables: Iterable[T],
  timeout: float = None,
  chunksize: int = 1,
  max_workers: int = None,
  use_io_optimized_pool: bool = True,
  pool: futures.Executor = None,
) -> List[V]:
  if pool is not None:
    return list(pool.map(fn, *iterables, timeout=timeout, chunksize=chunksize))

  if use_io_optimized_pool:
    from multiprocessing.pool import Pool

    with Pool(max_workers) as pool:
      return list(pool.map(fn, *iterables, chunksize=chunksize))

  with futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
    return list(pool.map(fn, *iterables, timeout=timeout, chunksize=chunksize))
