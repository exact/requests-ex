import time
from RequestsEx import *

# main/testing function
def testing():
    # this file was made quickly & should show everything this library can do, if you have any questions feel free to contact!

    # accuracy checking & timing
    connecting  = round(time.time()+3)
    sending     = round(time.time()+5)
    recving     = round(time.time()+10)
    print(f'connecting at: {connecting}')
    print(f'sending at:    {sending}') 
    print(f'recving at:    {recving}') # not using currently(works tho), and kinda pointless but why not add it right?

    # build test eRequest object and give it some test mc api info (create a new MC profile)
    newRequest = eRequest(
        # request method & URI are two required params for the request, all others are optional
        'post', 'https://api.minecraftservices.com/minecraft/profile', # <- only 2 required arguements

        headers = { # optionally set additional HTTP headers to be sent in request, can be None or an empty dict for no added Headers
            'Authorization': f'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ4dWlkIjpiMjUzNTQ3MzQzMDQwNDI2MyIsImFnZyI6IkFkdWx0Iiwic3ViIjoiMWYwMmI5ODktYzJmNS00ZGRlLWI4YjctM2YyYWQ5MDA1ZmE1IiwibmJmIjoxNjYzMzI3OTAzLCJhdXRoIjoiWEJPWCIsInJvbGVzIjpbXSwiaXNzIjoiYXV0aXVudGljYXRpb24iLCJleHAiOjE2NjM0MTQzMDMsImlwdCI6MTY2MzMyNzkwMywicGxhdGZvcm0iOiJVTktOT1dOIiwieXVpZCI6IjQ4NmZiZGRiNWZlMjI4NDcwMGRkMTZlMzEwZWJjY2E5In0.8y0Hx-1Pf5j_Go1elQketynUF33GiKvyT7gr6I2GUEE'
        }, 

        params = { }, # HTTP/GET URL parameters that are appended onto the path of your request, can be unset, None or empty for no params
                      # ex. /myUrlPath?these=are&params <<<

        data = { 
            "profileName": "crystal"
        }, # data/json sent in HTTP request under the Headers, can be unset, None or an empty dict for sending no data

        timing = RequestTiming( # also optionally, params can be unset or None for normal/random times
            connectAt   = connecting, 
            sendAt      = sending, 
            receiveAt   = None
        ) # ~ More About Request Timing ~
          # Priority is as follows: connectAt -> sendAt -> receiveAt, if any are set & are valid ints/floats they will be executed 
          # in this order. This means that no matter what connecting will happen before sending and sending will happen before 
          # receiving, never out of order, regardless of what times you set. This is because of how sockets & requests work.
          # Support for receiving before sending may come later.
    )

    # execute() fires the request and respects any timing if set, the debug arg can be set to True to view raw payloads in console
    # NOTE: if send/connect time is within ~1s of calling execute() it will throw an error unless skipTimesCheck is True
    # all parameters are optional!
    newResp = newRequest.do(debug=True, skipTimesCheck=False) 

    # now we pretty print out all request data & variables :D

    # all time data is in UNIX or seconds, things like travel/connection time can be * 1000 to convert to milliseconds
    # timing data like send/recv/conn times are taken after the socket operation is called
    # response data is formatted into 'text' and 'headers' variables on the response object, similar to the normal requests library
    print(f'Connection Took: {newResp.connection_time}')
    print(f'Travel Time:     {newResp.round_trip}\n')
    print(f'Sent At:         {newResp.sent_at}')
    print(f'Received At:     {newResp.received_at}')
    print(f'Connected At:    {newResp.connected_at}\n')
    print(f'Status Code:     {newResp.status_code}')

    print(f'\nResponse:\n\n"""\n{newResp.text}\n"""')
    print(f'\nHeaders:\n\n{newResp.headers}')

    input('\ndone :)')



if __name__ == '__main__':
    testing()