# import all needed libraries, no externals needed
import socket, ssl, json, time

REQUEST_DEBUG_FORMAT = '<eRequest, payload bytes=[payload_here]>' # formatting for request debug print

# easy safer, yet slower sleep function
def sleep(dur: float | int):
    if dur > 0: time.sleep(dur) # only call sleep() if duration is positive

# custom request error objects
class RequestTimingsError(Exception): pass
class RequestPayloadError(Exception): pass
class RequestRequestError(Exception): pass

# custom request timing object, takes in UNIX times to perform socket operations
class RequestTiming:
    def __init__(self, *, connectAt: float | int = None, sendAt: float | int = None, receiveAt: float | int = None):
        self.connectAt = connectAt; self.sendAt = sendAt; self.receiveAt = receiveAt

# custom HttpResponse-like object with universal attributes such as 'text', 'status_code' and 'headers' for easy response parsing
class HttpResponse:
    def __init__(self, text: str, status_code: int, conn_at: float, sent_at: float, recv_at: float, round_trip: float, conn_time: float, headers: dict):
        self.text = text; self.status_code = status_code; self.connected_at = conn_at; self.sent_at = sent_at; self.received_at = recv_at; self.round_trip = round_trip; self.connection_time = conn_time; self.headers = headers

# custom easy-to-use request maker class that constructs with all info needed for the request then builds/executes it via the execute() extension
class eRequest:
    # initalize new custom request object, take in all attributes needed and set defaults if needed
    def __init__(self, method: str, uri: str, *, headers: dict = None, data: dict = None, params: dict = None, timing: RequestTiming = None):
        self.method = method; self.uri = uri; self.headers = headers; self.data = data; self.params = params; self.timing = timing

    # there are alternative type checks to the isinstance() calls we use, but I choose to use the isinstance built-in for valdiation

    # once initialized, execute & complete the request if possible and function is called
    def do(self, *, debug: bool = False, skipTimesCheck: bool = False) -> HttpResponse:
        # check that timings makes sense
        if self.timing != None and isinstance(self.timing, RequestTiming) and not skipTimesCheck:
            if self.timing.connectAt != None and self.timing.connectAt <= time.time() + 1:
                raise RequestTimingsError('Connection Time must not be in the past or within a second of current time!')
            if self.timing.sendAt != None and self.timing.sendAt <= time.time() + 1:
                raise RequestTimingsError('Send Time must not be in the past or within a second of current time!') 

        # ^ if timings above don't make sense(occur within 1 second of calling), we will raise an error, skipTimesCheck can be set to True to avoid this behavior

        # try to build the HTTP request payload
        try:
            # parse out host name (<subdomain>.<domain>.<tld>)
            host_name = self.uri.split('/')[2]

            # form start of payload with path and host header
            if self.params != None and isinstance(self.params, dict) and len(self.params) > 0: # check if params are set and append to the path
                encodedParams = '' # build params into pretty &= format
                for param in self.params: encodedParams += f'{param}={self.params[param]}&'
                payloadData = [f"{self.method.upper()} /{'/'.join(self.uri.split('/')[3:len(self.uri.split('/'))])}?{encodedParams[:-1]} HTTP/1.1", f"Host: {host_name}"]
            else: # no params set
                payloadData = [f"{self.method.upper()} /{'/'.join(self.uri.split('/')[3:len(self.uri.split('/'))])} HTTP/1.1", f"Host: {host_name}"]
            
            # if headers are present add them now (Header: Value)
            if self.headers != None and isinstance(self.headers, dict):
                for x in self.headers: payloadData.append(f'{x}: {self.headers[x]}')

            # finalize payload & add length and body data if present
            if self.data != None and isinstance(self.data, dict) and len(self.data) > 0: 
                payloadData.append(f'Content-Length: {len(str(self.data))}') # if data is set we need to set Content-Length header
            payloadData.append('') # \r\n
            if self.data != None and isinstance(self.data, dict) and len(self.data) > 0: 
                payloadData.append(json.dumps(self.data)) # dump the JSON formatted dictionary into the body of the request
            else: payloadData.append('') # \r\n

            # build the payload from the array we have constructed
            payload = '\r\n'.join(payloadData).encode('utf-8') # encode for bytes (UTF-8)
        except Exception as ex:
            raise RequestPayloadError(f'Failed to create request payload, exception was: {ex}') # propagate any error thrown

        # if debug is set print out payload in attached terminal
        if debug: print(f'\n{REQUEST_DEBUG_FORMAT.replace("[payload_here]", str(payload))}\n')

        # make a new normal socket & try to send the request/payload, respecting timings if set
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # TODO: make socket object settable & support all socket-like objects
                # timing solution is ugly but very accurate, we use infinite loops for close to real time performace & millisecond accuracy

                # time the connection operation (ugly but works TT)
                if self.timing != None and isinstance(self.timing, RequestTiming) and self.timing.connectAt != None:
                    sleep(self.timing.connectAt - time.time() - .1)
                    while 1:
                        if time.time() >= self.timing.connectAt: connStart = time.perf_counter(); s.connect((host_name, 443)); conn=time.time(); break
                else: connStart = time.perf_counter(); s.connect((host_name, 443)); conn=time.time() # no timing needed, do operation right away
                connEnd = time.perf_counter()

                # wrap the socket as a SSLSocket by default, maybe add granularity for no HTTPS later?
                with ssl.create_default_context().wrap_socket(s, server_hostname=host_name) as mainsocket:
                    # the main timing of the request now happens, we either send/recv right away or wait to send/recv at exact unix

                    # time the sending (ugly but works TT)
                    if self.timing != None and isinstance(self.timing, RequestTiming) and self.timing.sendAt != None:
                        sleep(self.timing.sendAt - time.time() - .1)
                        while 1:
                            if time.time() >= self.timing.sendAt: start = time.perf_counter(); mainsocket.send(payload); send=time.time(); break
                    else: start = time.perf_counter(); mainsocket.send(payload); send=time.time() # no timing needed, do operation right away

                    # time the receiving (ugly but works TT)
                    if self.timing != None and isinstance(self.timing, RequestTiming) and self.timing.receiveAt != None:
                        sleep(self.timing.receiveAt - time.time() - .1)
                        while 1:
                            if time.time() >= self.timing.receiveAt: 
                                socket_resp = mainsocket.recv(4096); recv=time.time(); break
                    else: socket_resp = mainsocket.recv(4096); recv=time.time() # no timing needed, do operation right away

                    end = time.perf_counter() # request has finished
        
                    # decode the received bytes & grab all response headers
                    str_resp = socket_resp.decode('utf-8'); headers = {}
                    for line in str_resp.split('\n'):
                        if line.replace('\r', '').replace('\n', '') == '': break # dont parse HTTP body, only headers

                        if 'HTTP/' not in line and ': ' in line: # also don't parse very first line/header of request
                            lineSplit = line.split(': '); headers[lineSplit[0]] = lineSplit[1].replace('\r', '')

                    # all should be good ^-^ 
                    # we now parse out HTTP body, response status code, the headers we grabbed and all timing info
                    # then we bottle it in a nice response object for easy usage
                    return HttpResponse(
                        str_resp.split('\r\n\r\n')[1],  # HTTP Body
                        int(str_resp[9:12]),            # status code
                        conn,                           # exact unix .connect() finished
                        send,                           # exact unix .send() finished 
                        recv,                           # exact unix .recv() finished 
                        end-start,                      # recv time - send time = ~round trip
                        connEnd-connStart,              # time(seconds) that .connect() took to complete
                        headers                         # pretty dictionary of all headers the server/response included
                    )
        except Exception as ex: # catch ANY error thrown during socket operations, package as socket error and return failure
            raise RequestRequestError(f'Request failed to complete: {ex}')