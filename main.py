from flask import Flask
import requests
import logging
from datetime import datetime, timedelta
from threading import Lock, Thread, Event
from time import sleep
import json
import os
from jsonpath_ng import parse

logging.basicConfig(level=os.getenv('C42_LOGLEVEL') or 'INFO')
logger = logging.getLogger(__name__)
app = Flask(__name__)

TOKEN = os.getenv('C42_TOKEN')
EXPIRY = float(os.getenv('C42_EXPIRY') or 4.2)

cache = {}
lock = Lock()

def cacheme(fn):
    def function(event_id):
        with lock:
            try:
                _, value = cache[event_id]
                return value
            except KeyError:
                expiry, value = (datetime.now() + timedelta(minutes=EXPIRY),
                                 fn(event_id))

                cache[event_id] = (expiry, value)
                return value
    return function


class CleanupThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(1.0):
            try:
                for key in cache:
                    expiry, value = cache[key]
                    if expiry < datetime.now():
                        del cache[key]
                        break
            except RuntimeError:
                pass


title = parse('$.data[*].title')
names = parse('$.data[*].subscriber.first_name')


@app.route('/events-with-subscriptions/<event_id>')
@cacheme
def events_with_subscriptions(event_id):
    headers = {'Accept': 'application/json',
               'Content-type': 'application/json',
               'Authorization': 'Token {}'.format(TOKEN)}
    url_evt = 'https://demo.calendar42.com/api/v2/events/{}'.format(event_id)
    url_subs = 'https://demo.calendar42.com/api/v2/event-subscriptions/'
    response = requests.get(url_evt, headers=headers)
    if response.status_code != 200:
        return response.text, response.status_code

    details = response.json()
    payload = {'event_ids': '[{}]'.format(event_id), 'limit': '10'}
    response = requests.get(url_subs, headers=headers, params=payload)
    subs = response.json()

    result = {'id': event_id,
              'title': title.find(details)[0].value,
              'names': [name.value for name in names.find(subs)]}

    return json.dumps(result)

def main():
    try:
        stop = Event()
        thread = CleanupThread(stop)
        thread.start()
        app.run()
    finally:
        stop.set()

if __name__ == '__main__':
    main()
