#!/usr/bin/env python
import functools
import signal
from concurrent import futures
from typing import Callable


def trap_pool_shutdown(pool: futures.Executor, wait: bool = False, cancel_futures: bool = True):
  shutdown_handler: Callable = functools.partial(pool.shutdown, wait=wait, cancel_futures=cancel_futures)
  signal.signal(signal.SIGINT, shutdown_handler)
  signal.signal(signal.SIGTERM, shutdown_handler)
