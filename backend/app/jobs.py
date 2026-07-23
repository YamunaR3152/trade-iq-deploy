# this is backend\app\jobs.py
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

_executor = ThreadPoolExecutor(max_workers=4)


def enqueue_job(function: Callable[..., Any], *args, **kwargs):
    return _executor.submit(function, *args, **kwargs)


def run_job_sync(function: Callable[..., Any], *args, **kwargs):
    return function(*args, **kwargs)
