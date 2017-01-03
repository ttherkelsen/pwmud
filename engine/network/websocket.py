import struct

class WSFrame(object):
    @classmethod
    def parse(cls, frame):
        if len(frame) < 2:
            return None

        byte1, byte2 = struct.unpack("BB", frame[0:2])
        wsf = cls(None, None)
        wsf.fin = (byte1 & 128) >> 7
        wsf.rsv1 = (byte1 & 64) >> 6
        wsf.rsv2 = (byte1 & 32) >> 5
        wsf.rsv3 = (byte1 & 16) >> 4
        wsf.opcode = byte1 & 15
        wsf.mask = (byte2 & 128) >> 7
        wsf.payload_len = plen = byte2 & 127
        

        i = 2
        if plen < 126:
            pass
        elif plen == 126:
            i += 2
            if i > len(frame):
                return None
            wsf.extended_payload_len = plen = struct.unpack("!H", frame[i-2:i])
        else: # plen == 127:
            i += 8
            if i > len(frame):
                return None
            wsf.extended_payload_len = plen = struct.unpack("!Q", frame[i-8:i])

        if wsf.mask:
            i += 4
            if i > len(frame):
                return None
            wsf.masking_key = struct.unpack("BBBB", frame[i-4:i])

        i += plen
        if i > len(frame):
            return None
        
        if wsf.mask:
            payload = bytearray(frame[i-plen:i])
            key = wsf.masking_key
            for idx in range(plen):
                payload[idx] = payload[idx] ^ key[idx % 4]
            wsf.payload = payload
        else:
            wsf.payload = frame[i-plen:i]

        if i < len(frame):
            wsf.extra_data = frame[i:]
        return wsf
    
    def __init__(self, opcode, payload):
        self.fin = 1
        self.rsv1 = self.rsv2 = self.rsv3 = 0
        self.mask = 0
        self.opcode = opcode
        self.payload = payload
        self.payload_len = None
        self.extended_payload_len = None
        self.masking_key = None
        self.extra_data = None
        self.decoded_payload = None

    def decode_payload(self):
        if self.decoded_payload is None:
            self.decoded_payload = self.payload.decode('utf-8')
        return self.decoded_payload
        
    def validate(self):
        # RFC Rules
        if not self.mask:
            return "mask must be 1"

        if self.rsv1 or self.rsv2 or self.rsv3:
            # We never allow any extensions so abort if any is set
            return "rsv1, rsv2 and rsv3 must all be 0"

        if (self.payload_len == 126 and (self.extended_payload_len < 126)) \
           or (self.payload_len == 127 and (self.extended_payload_len < 65536)):
            return "must use smallest payload len encoding possible"

        if self.payload_len == 127 and (self.extended_payload_len >> 63):
            return "when 64-bit payload len is used, most significant bit must be 0"

        if self.opcode in (3, 4, 5, 6, 7, 11, 12, 13, 14, 15):
            return "opcode %s is reserved for future use" % self.opcode

        if (self.opcode & 8) and not self.fin:
            return "control frames cannot be fragmented"

        if self.opcode == 1 and self.fin:
            try:
                self.decode_payload()
            except:
                return "payload is not UTF-8 encoded text"

        # pywebmud protocol rules
        if self.opcode == 2:
            return "pywebmud protocol does not support binary frames"

        
        return None


    def render(self):
        data = bytearray()
        data.append((self.fin << 7) | (self.rsv1 << 6) | (self.rsv2 << 4) | (self.rsv3 << 4) | self.opcode)

        plen = len(self.payload)
        if plen < 126:
            data.append((self.mask << 7) | plen)
        elif plen < 65537:
            data.append((self.mask << 7) | 126)
            data.extend(struct.pack('!H', plen))
        else:
            data.append((self.mask << 7) | 127)
            data.extend(struct.pack('!Q', plen))
        if self.mask:
            data.extend(self.masking_key)
        data.extend(self.payload)
        return data

class WSTextFrame(WSFrame):
    def __init__(self, text=b''):
        super().__init__(1, text)

class WSCloseFrame(WSFrame):
    def __init__(self, reason):
        super().__init__(8, reason)

class WSPingFrame(WSFrame):
    def __init__(self, data=b''):
        super().__init__(9, data)

class WSPongFrame(WSFrame):
    def __init__(self, data=b''):
        super().__init__(10, data)

