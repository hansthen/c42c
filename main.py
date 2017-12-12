from flask import Flask
import requests
import logging
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep

logger = logging.getLogger(__name__)
app = Flask(__name__)

TOKEN='FIXME'
EXPIRY=4.2

cache = {}
lock = Lock()

def cacheme(fn):
    def wrapper(key):
        with lock:
            try:
                _, value = cache[key]
                return value
            except KeyError:
                expiry, value = (datetime.now() + timedelta(minutes=EXPIRY), fn(key))
                cache[key] = (expiry, value)
                return value
    return wrapper

def cleanup():
    for key in cache:
        expiry, value = cache[key]
        if expiry < datetime.now():
            del cache[key]
    sleep(1)


@app.route('/events-with-subscriptions/<id>')
@cacheme
def events_with_subscriptions(event_id):
    headers = { 'Accept': 'application/json',
                'Content-type': 'application/json',
                'Authorization': 'Token {}'.format(TOKEN) }
    url_evt = 'https://demo.calendar42.com/api/v2/events/{}'.format(event_id)
    url_subs = 'https://demo.calendar42.com/api/v2/events-subscriptions/'
    response = requests.get(url_evt, headers=headers)
    details = response.json()
    payload = { 'event_ids': event_id }
    response = request(url_subs, headers=headers, params=payload)
    subs = response.json()

    result = { 'id': event_id,
               'title': details['titles'],
               'names': [sub['name'] for sub in subs] }

    return result


if __name__ == '__main__':
    Thread(target=cleanup).start()
    app.run()
