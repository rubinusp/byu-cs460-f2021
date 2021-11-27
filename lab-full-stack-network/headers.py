import struct

from cougarnet.util import \
        ip_str_to_binary, ip_binary_to_str


IP_HEADER_LEN = 20
UDP_HEADER_LEN = 8
TCP_HEADER_LEN = 20
TCPIP_HEADER_LEN = IP_HEADER_LEN + TCP_HEADER_LEN
UDPIP_HEADER_LEN = IP_HEADER_LEN + UDP_HEADER_LEN

TCP_RECEIVE_WINDOW = 64

class IPv4Header:
    def __init__(self, length, ttl, protocol, checksum, src, dst):
        self.length = length
        self.ttl = ttl
        self.protocol = protocol
        self.checksum = checksum
        self.src = src
        self.dst = dst

    @classmethod
    def from_bytes(cls, hdr):
        return cls(0, 0, 0, 0, '0.0.0.0', '0.0.0.0')

    def to_bytes(self):
        return b''


class UDPHeader:
    def __init__(self, sport, dport, length, checksum):
        self.sport = sport
        self.dport = dport
        self.checksum = checksum
        self.length = length

    @classmethod
    def from_bytes(cls, hdr):
        sport, = struct.unpack('!H', hdr[:2])
        dport, = struct.unpack('!H', hdr[2:4])
        length, = struct.unpack('!H', hdr[4:6])
        checksum, = struct.unpack('!H', hdr[6:8])
        return cls(sport, dport, length, checksum)

    def to_bytes(self):
        hdr = b''
        hdr += struct.pack('!H', self.sport)
        hdr += struct.pack('!H', self.dport)
        hdr += struct.pack('!H', self.length)
        hdr += struct.pack('!H', self.checksum)
        return hdr


class TCPHeader:
    def __init__(self, sport, dport, seq, ack, flags, checksum):
        self.sport = sport
        self.dport = dport
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.checksum = checksum

    @classmethod
    def from_bytes(cls, hdr):
        return cls(0, 0, 0, 0, 0, 0)

    def to_bytes(self):
        return b''
