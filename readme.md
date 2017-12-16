Introducton
==============


Design choices
==============

Using an external caching service or not
----------------------------------------
For such an project I would normally use an external caching service
such as redis. However, I thought it would be more illustrative to implement
the cache myself.

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

Json handling
-------------
At first I chose not to use a library for the parsing of json. This was in part because
I did not know the actual data structures of the C42 services, but also because I 
suspect the json structures to be fairly simple. If there were more complicated 
patterns or schemas involved I would normally use a jsonpath library (if I only
need to extract a few values) or a json serialization library such as Munch 
(if I need to manipulate the objects using their json structure.

In the end I went with jsonpath anyway, as it made the code  prettier and it was just
a few minutes extra work.
 
Web Framework
-------------
I am more fond of flask than django, but not very religious about it. In particular
I like decorator based routing more than the django routing approach.




