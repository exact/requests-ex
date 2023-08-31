
# RequestsEx

This project is part of my script I used for [**my Minecraft sniper**](https://evie.space/snipes) which I don't use anymore and does not work. It is intended for applications which really need to be precise and only with a few milliseconds of any delay. This wrapper breaks down the underlying socket used for network requests and allows you, if you choose, to specify custom points in time for the socket event to occur exactly.

For example, you can specify your request to connect to the server at a specific time, lets call it **x**, and then additionally you can set your payload/data of your request to be sent **exactly 10 seconds** after your connection, so **x + 10**, it's that easy. Do note that time is relative to your server/machine, so make sure you're synced to an NTP protocol. Upon locally checking the times the socket actions were executed you will find **<1ms accuracy** on all set socket events.




## Contact Me

- [My Website](https://evie.space)
- [@garment on Discord](https://discord.com/users/993964054081191966)


## Usage

Start by defining when you want everything in your request to happen:

**Note:** You don't have to set all or any of the values, they are all optional.

```py
myConnecting  = round(time.time() + 3)
mySending     = round(time.time() + 5)
myRecving     = round(time.time() + 10)
```
In this example we'll connect in 3 seconds from the current time, send after 5 seconds and wait to receive any data after 10 seconds. We use `round()` to make the value even and not decimals for easy viewing.

Next, we build our `RequestEx` object that we'll use to send or manage our request:

```py
newRequest = RequestEx(
    # Set the request method(GET, POST, PATCH, etc) and URI the request will be made to
    'post', 'https://api.mysite.com/route/data',

    # OPTIONAL: Set HTTP headers to be sent, can be None or an empty dict for no added headers
    headers = { 
        'Authorization': f'Basic YWxhZGRpbjpvcGVuc2VzYW1l'
    }, 

    # OPTIONAL: Set URL parameters that are added onto the path of your request
    # (Can be unset, None or empty dict for no params. Example: x.com/myPath?these=are&params=here)
    params = {
        'dataType': '3'
    },

    # OPTIONAL: Set json sent in HTTP payload, can be unset, None or an empty dict for sending no data
    data = { 
        "queryUuid": "769ab60f-de62-4eae-a006-cb1d1026deed"
    },

    # OPTIONAL: Set RequestTiming object for specifying exact, millisecond specific request timing
    # (Can be unset or None for normal/random request timing)
    timing = RequestTiming(
        connectAt   = myConnecting, 
        sendAt      = mySending, 
        receiveAt   = None # Note that not all values must be defined!
    )
)
```
Request priority is as follows: **connectAt -> sendAt -> receiveAt**

If any are set and are valid ints/floats they will be executed in this order. This means that no matter what connecting will happen before sending and sending will happen before receiving, never out of that order, regardless of what times you set. This is because of how sockets & requests work. Support for receiving before sending may come later for lightning fast response speeds.

Finally, we execute our request & get all the information about it:

```py
# Do the request
newResp = newRequest.execute(debug=True, skipTimesCheck=False) # Parameters are optional

# Response/Result Details
newResp.connection_time  # Exact seconds/milliseconds it took to connect to the remote server
newResp.round_trip       # Exact seconds/milliseconds it took from sending to receiving the request
newResp.sent_at          # Exact, precise UNIX time your request payload was sent at
newResp.received_at      # Exact, precise UNIX time the response was received from the remote server
newResp.connected_at     # Exact, precise UNIX time we connected to the remote server
newResp.status_code      # HTTP Status Code the server/address responded with
newResp.text             # Body of HTTP response, will be the text/json of response
newResp.headers          # Headers of HTTP response from the remote server
```
`.execute()` fires the request and respects any timing if set. The **debug** arguement can be set to True to view raw payloads in the terminal.

**Note:** If specified connect/send is within ~1s of calling `.execute()` it will throw an error unless **skipTimesCheck** is True!

You now have all the response data & timing information, all time data is in UNIX or seconds. You can convert any value that is seconds to milliseconds **by multiplying by 1000**. Timing information like send/receive/connect times are gathered after the socket operation is called, response data is formatted into `text` and `headers` values on the response object, similar to the normal requests library.
## Optimizations & Recommendations

Recommended Python Version: **3.11+**

I've tried to make this code as easy to use as possible while also retaining the lazer-like precision my other scripts have. It mainly uses a CPU technique called [busy waiting](https://en.wikipedia.org/wiki/Busy_waiting) for very precise timing, but does so in short **<100ms** bursts(if set to) to make CPU utilization minimal. In my experience there is virtually no downside to this approach and even when running multiple scripts that are busy waiting the modern processors I've used are able to manage them and still get amazing precision. We wait until around 100 milliseconds before an operation is about to take place with the built-in Python `sleep()` method, [which has varying degrees of accuracy depending on your platform/device](https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep), then we busy wait the remaining milliseconds for the best result.


## Todo

- Threads/Futures for built-in & better concurrency
- Custom socket class objects for support for pysocks and other proxy/custom sockets
- Make socket fully modular and support receiving before sending if wanted
- Support for multiple requests/sockets & batch requests, all threaded and coordinated
If you have any recommendations or suggestions **please feel free to contact me**!


## Feedback

If you have any feedback, questions, concerns or just want to say hi, please reach out!

My email is issy@evie.space


## Resources & License

 - [Python WIKI: Python Speed & Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
