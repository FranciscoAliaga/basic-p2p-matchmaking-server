# basic p2p matchmaking server

A minimalist and simple server application that allows to POST and GET ip adresses from a player willing to host p2p games (for example, made in Godot).

Provides two urls:

* `URL:8080/host?number=<n>`: POST, inserts the client ip declaring that there are `<n>` player slots left.
    * if succesfull, returns `REQUEST UPDATED` message.
    * if `<n>` is 0, removes the client from the ip list. Returns `REQUEST DELETED` message.
    * for negative `<n>`, returns a `400: bad_request` error message.
* `URL:8080/join`: GET, fetches the ip adress of a hosting player that has more than one slot available.
    * returns `NO HOST AVAILABLE` if the list of hosting players is empty.

Also, automatically removes timed out requests.

`WARNING`: Not production ready. Has not been tested against security attacks, nor has the features expected from a matchmaking server.
Made as a part of a multiplayer games course. Only for testing and learning purposes.
 

## how to use
Install dependency:
```
pip install CherryPy
```

Using the `cherrypy.__version__ == '18.8.0'`.

**just run**
```python matchmaking.py```

You may want to deploy using another HTTP server, such as `nginx` as proxy. You may also [deploy using the cherrypy guide](https://docs.cherrypy.dev/en/latest/deploy.html#id6).
