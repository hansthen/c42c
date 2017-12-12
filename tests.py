from main import cacheme, cleanup
import time
from datetime import datetime
import sys
from threading import Thread

@cacheme
def test(x):
    return datetime.now()

Thread(target=cleanup).start()

x1 = test(None)
x2 = test(None)

time.sleep(4.4 * 60)
x3 = test(None)

assert x1 == x2, "cache failed to cache"
assert x1 != x3, "cache failed to expire"

sys.exit(0)


