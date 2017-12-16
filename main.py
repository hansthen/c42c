from flask import Flask
import requests
import logging
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep
import json

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)
app = Flask(__name__)

TOKEN='d6126cc0239dcdc1b300bf34b8dcf2ea3a303901'
EXPIRY=4.2

cache = {}
lock = Lock()

def cacheme(fn):
    def function(event_id):
        with lock:
            try:
                _, value = cache[event_id]
                return value
            except KeyError:
                expiry, value = (datetime.now() + timedelta(minutes=EXPIRY), fn(event_id))
                cache[event_id] = (expiry, value)
                return value
    return function

def cleanup():
    for key in cache:
        expiry, value = cache[key]
        if expiry < datetime.now():
            del cache[key]
    sleep(1)


@app.route('/events-with-subscriptions/<event_id>')
@cacheme
def events_with_subscriptions(event_id):
    headers = { 'Accept': 'application/json',
                'Content-type': 'application/json',
                'Authorization': 'Token {}'.format(TOKEN) }
    url_evt = 'https://demo.calendar42.com/api/v2/events/{}'.format(event_id)
    url_subs = 'https://demo.calendar42.com/api/v2/event-subscriptions/'
    response = requests.get(url_evt, headers=headers)
    response.raise_for_status()
    details = response.json()
    payload = { 'event_ids': '[{}]'.format(event_id), 'limit': '10' }
    response = requests.get(url_subs, headers=headers, params=payload)
    subs = response.json()

    result = { 'id': event_id,
               'title': details['data'][0]['title'],
               'names': ["{last_name}, {first_name}".format(**sub['actor']) for sub in subs['data']] }

    return json.dumps(result)


if __name__ == '__main__':
    Thread(target=cleanup).start()
    app.run()
