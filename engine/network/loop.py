import asyncio, base64, hashlib, functools, json
from .websocket import *

class WebSocketProtocol(asyncio.Protocol):
    MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, engine):
        self.engine = engine

    #
    # --- Interface methods begin ---
    #

    def debug_log(self, msg):
        self.engine.debug(msg, 'pwmud.network')
    
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        self.debug_log('Connection from {}'.format(peername))
        self.transport = transport
        self.message = None
        self.handshake_complete = False
        self.continuation = False
        self.closing_connection = False
        self.frame = None
        self.payload = None

        # FIXME: Deal with connections that never complete the websocket handshake

        
    def connection_lost(self, exc):
        self.debug_log('Connection lost from {}'.format(self.transport.get_extra_info('peername')))
        # We don't want to tell the engine about lost connections
        # unless they actually have completed the websocket handshake
        if self.handshake_complete:
            self.engine.network_disconnect(self)

        
    def pause_writing(self):
        # Called when we reach a high-water buffer mark (FIXME: What's the value?)
        self.debug_log('Pause writing called')

    
    def resume_writing(self):
        # Called to resume writing after writing has been previously paused
        self.debug_log('Resume writing called')

    
    def data_received(self, data):
        if self.handshake_complete:
            self.handle_frame(data)
        else:
            self.handle_handshake(data)
        
    def eof_received(self):
        # Called when the remote end wishes to close the connection
        # Should return a boolean false value to let the transport object close
        # itself as it pleases instead of relying on this object closing it
        self.debug_log('EOF received called')

    #
    # --- Interface methods end ---
    #
        
    def send_data(self, message):
        self.debug_log("Send data: %r" % message)
        self.transport.write(type(message) is str and message.encode() or message)

    def send_message(self, obj):
        self.send_data(WSTextFrame(json.dumps(obj).encode()).render())
        

    def handle_handshake(self, data):
        message = data.decode()
        if self.message is not None: # Continue a previously fragmented message?
            message = self.message + message # FIXME: Protect against infinite memory usage

        if not message.endswith("\r\n\r\n"): # Full HTTP header received?
            self.message = message
            return # FIXME: Protect against hanging connections

        self.debug_log('Data received: {!r}'.format(message))

        lines = message.split("\r\n")[:-2]
        parts = lines[0].split(" ")
        if len(parts) != 3 or parts[0] != "GET" or not parts[2].startswith("HTTP/"):
            return self.http_bad_request("Not a GET request or malformed request type.")
        try:
            version = float(parts[2].split("/")[1])
        except:
            return self.http_bad_request("HTTP version not a number")
        if version < 1.1:
            return self.http_bad_request("HTTP version < 1.1")

        try:
            headers = { h.lower(): v for h, v in [ t.split(": ") for t in lines[1:] ] }
        except:
            return self.http_bad_request("Malformed headers.")

        required = {
            'upgrade': 'websocket',
            'connection': 'upgrade',
            'sec-websocket-key': None,
            'sec-websocket-version': '13',
            'sec-websocket-protocol': 'pywebmud',
        }
        if not required.keys() <= headers.keys():
            return self.http_bad_request("WebSocket protocol specific headers missing.")
        for h, v in required.items():
            if h not in headers:
                return self.http_bad_request("Header '%s' missing." % h)
            if v is None:
                continue
            headers[h] = headers[h].lower().split(", ")
            if v not in headers[h]:
                return self.http_bad_request("Header '%s' must be '%s'." % (h, v))

        # FIXME: According to the RFC, if we abort due to
        # Sec-WebSocket-Version != 13, then we should return a header stating
        # we only want version 13
            
        # Everything looks good, calculate Accept hash
        accept = base64.standard_b64encode(hashlib.sha1((headers['sec-websocket-key'] + self.MAGIC_STRING).encode()).digest())

        # Tell the client to upgrade to WS
        self.send_data("\r\n".join([
            "HTTP/1.1 101 Switching Protocols",
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Sec-WebSocket-Protocol: pywebmud",
            "Sec-WebSocket-Accept: %s" % accept.decode(),
            "\r\n",
        ]))
        self.message = None
        self.handshake_complete = True

        self.engine.network_connect(self)
        

    def handle_opcode_0(self, frame): # continuation frame
        self.debug_log('[opcode 0] [frame payload] %r' % frame.payload)
        if not self.continuation:
            # We must be in continuation mode before opcode 0 frames are legal
            return self.abort_connection("got opcode 0 frame while not in continuation mode")

        self.payload += frame.payload
        if frame.fin:
            # Since we only allow text frames, we should test if payload is valid UTF-8
            try:
                utf8 = self.payload.decode('utf-8')
            except:
                return self.abort_connection("payload is not UTF-8")
            self.engine.network_message(utf8, self)
            self.continuation = False
            self.payload = None
        

    def handle_opcode_1(self, frame): # text frame
        self.debug_log('[opcode 1] [frame payload] %r' % frame.payload)
        if self.continuation:
            # Not legal to send opcode 1 frame while we are in continuation mode
            return self.abort_connection("got opcode 1 frame while in continuation mode")

        if frame.fin:
            # FIXME: Guard against non-valid JSON objects
            self.engine.network_message(json.loads(frame.payload.decode()), self)
        else:
            # Start continuation mode
            self.payload = frame.payload
            self.continuation = True

    def handle_opcode_8(self, frame): # ping
        self.debug_log('[opcode 8] [frame payload] %r' % frame.payload)
        self.send_data(WSPongFrame().render())

    def handle_opcode_9(self, frame): # pong
        self.debug_log('[opcode 9] [frame payload] %r' % frame.payload)
        # We don't need to do anything when we receive a pong

    def handle_opcode_10(self, frame): # connection close
        self.debug_log('[opcode 10] [frame payload] %r' % frame.payload)
        if self.closing_connection:
            self.debug_log('Closing connection')
            self.transport.close()
        else:
            self.closing_connection = True
            self.send_data(WSCloseFrame(frame.payload))

    def handle_frame(self, data):
        if self.frame is not None: # Continue partial frame
            data = self.frame + data # Protect against infinite mem usage

        wsf = WSFrame.parse(data)
        if wsf is None: # Incomplete frame
            self.frame = data
            return

        self.frame = None

        self.debug_log('[frame] Data received: {!r}'.format(data))
        
        # FIXME: Should raise exception instead of returning the error message
        err = wsf.validate()
        if err:
            return self.abort_connection(err)

        if self.closing_connection:
            # FIXME: Print error if the frame we just got is not a close frame
            self.transport.close()
            return

        # Validation will catch any unsupported opcodes so this is safe
        getattr(self, 'handle_opcode_%d' % wsf.opcode)(wsf)

        if wsf.extra_data:
            self.handle_frame(wsf.extra_data)
        

    def abort_connection(self, message):
        self.debug_log("Bad Frame: %s" % message)
        if self.closing_connection:
            # If we get an error while we are trying to close the connection
            # just close it silently
            self.transport.close()
        else:
            self.transport.write(WSCloseFrame('failing connection: %s' % message).render())
            self.closing_connection = True
        
    def http_bad_request(self, message):
        self.debug_log("Bad Request: %s" % message)
        self.send_data("HTTP/1.1 400 Bad Request\r\n\r\n")
        self.send_data(message)
        self.transport.close()

def run(engine):
    engine.debug('Setting up asyncio network loop', 'pwmud.network')
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(functools.partial(WebSocketProtocol, engine), engine.config.listen_ip, engine.config.listen_port)
    engine.network_server = server = loop.run_until_complete(coro)

    def tick():
        engine.housekeeping()
        loop.call_later(engine.config.housekeeping_interval, tick)

    # Serve requests until Ctrl+C is pressed
    engine.debug('Listening on {}'.format(server.sockets[0].getsockname()), 'pwmud.network')
    try:
        tick()
        loop.run_forever()
    except KeyboardInterrupt:
        print() # Clear 'ctrl-c'

    # Close the server
    engine.debug('Closing asyncio network loop', 'pwmud.network')
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    engine.debug('Asyncio network loop ended', 'pwmud.network')
