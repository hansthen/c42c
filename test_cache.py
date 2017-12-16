from main import cacheme, CleanupThread, app
import main
import time
from datetime import datetime
import sys
from threading import Thread, Event
import requests
import os
import logging


@cacheme
def test(x):
    return datetime.now()

stop = Event()
thread = CleanupThread(stop)
thread.start()

try:
    x1 = test(None)
    x2 = test(None)

    time.sleep((main.EXPIRY + 0.1) * 60)
    x3 = test(None)

    assert x1 == x2, "cache failed to cache"
    assert x1 != x3, "cache failed to expire"

finally:
    stop.set()

sys.exit(0)


