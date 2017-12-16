Introducton
==============
This service is a combined cache for two calendar 42 apis.

Setup
-----
I use a c42c virtualenv environment which I have setup in the root folder of the project.
It is .gitignore. You can create one by calling `virtualenv c42c` and then activate it
using `source c42c/bin/activate`.

Once you have activated the virtualenv environment, you can install the required python
packages using `pip install -r requirements.txt`.

To configure the server you can use the following environment variables

1. `C42_TOKEN` (mandatory)
2. `C42_EXPIRY` (default 4.2 in minutes)
3. `C42_LOGLEVEL` (default = INFO)

The server can be started using `python main.py`.

There are two test scripts: `test_cache.py` and `test_api.py`. No output is good.


Design choices
==============

Using an external caching service or not
----------------------------------------
For such an project I would normally use an external caching service
such as redis. However, I thought it would be more illustrative to implement
the cache myself. There are some nice edge cases in relation with threading,
locking and program termination. Since during my day job I hardly get to program
this type of code, I also thought it'd be a nice exercise.

Catching the KeyException (instead of checking the key first) is a bit ugly. I 
try to avoid using Exceptions for normal control flow, but here it prevents a
race condition when accessing a key that has just been expired.

Expiry
------
For cleanup I used a thread to find and delete expired cache entries. A few
other designs I considered, but rejected were
1. expiry of entries upon retrieval (Rejected as this may lead to a memory leak.)
2. using a scheduler to trigger cache expiry. I have experience with APScheduler,
and I briefly considered using it to trigger cache expiry events.
However, it seemed overkill to add another dependency. Depending on the actual 
requirements (what are the actual usage patterns? does expiry need to be 
near real-time?), I might reconsider.

We also cache negative results. This can be awkward sometimes, but is also a good
defence against malfunctioning programs that spam random keys.

Json handling
-------------
At first I chose not to use a library for the parsing of json. This was in part because
I did not know the actual data structures of the C42 services, but also because I 
suspect the json structures to be fairly simple. If there were more complicated 
patterns or schemas involved I would normally use a jsonpath library (if I only
need to extract a few values) or a json serialization library such as Munch 
(if I need to manipulate the objects using their json structure).

In the end I went with jsonpath anyway, as it made the code  prettier and it was just
a few minutes extra work.
 
Web Framework
-------------
I am more fond of flask than django, but not very religious about it. In particular
I like decorator based routing more than the django routing approach.

Error handling
--------------
Since this is a caching framework, I am a bit light on error handling. If one of the 
services returns an error we just pass it through. In particular I assume that the error
messages from the upstream services are safe to pass through and do not contain any
security sensitive information.

