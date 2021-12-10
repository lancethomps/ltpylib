#!/usr/bin/env python
import signal
from concurrent import futures


def trap_pool_shutdown(pool: futures.Executor, wait: bool = False, cancel_futures: bool = True):

  def shutdown_handler():
    pool.shutdown(wait=wait, cancel_futures=cancel_futures)

  signal.signal(signal.SIGINT, shutdown_handler)
  signal.signal(signal.SIGTERM, shutdown_handler)
