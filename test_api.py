from main import cacheme, CleanupThread, app
import main
import time
from datetime import datetime
import sys
from threading import Thread, Event
import requests
import logging

logger = logging.getLogger('werkzeug')
logger.setLevel('WARNING')

thread = Thread(target=main.main)
# Not exactly save, but we'll just ignore errors here
thread.daemon = True
thread.start()

old_token = main.TOKEN
main.TOKEN = 'WONTWORK'
response = requests.get('http://localhost:5000/events-with-subscriptions/24b49c4875ab33d3c13531d9d3d3f2fc_15132679600050')
assert response.status_code == 401, "Invalid response to invalid token: {}".format(response.text)

# trigger expiry of negative cache entry
main.TOKEN=old_token
time.sleep((main.EXPIRY + 0.1) * 60)

response = requests.get('http://localhost:5000/events-with-subscriptions/24b49c4875ab33d3c13531d9d3d3f2fc_15132679600050')
assert response.status_code == 200, "Invalid response to known key: {}".format(response.text)

response = requests.get('http://localhost:5000/events-with-subscriptions/willnotwork')
assert response.status_code == 404, "Invalid response to unknown key: {}".format(response.text)


sys.exit(0)


