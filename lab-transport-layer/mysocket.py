import random

TCP_FLAGS_SYN = 0x02
TCP_FLAGS_RST = 0x04
TCP_FLAGS_ACK = 0x10

TCP_STATE_LISTEN = 0
TCP_STATE_SYN_SENT = 1
TCP_STATE_SYN_RECEIVED = 2
TCP_STATE_ESTABLISHED = 3
TCP_STATE_FIN_WAIT_1 = 4
TCP_STATE_FIN_WAIT_2 = 5
TCP_STATE_CLOSE_WAIT = 6
TCP_STATE_CLOSING = 7
TCP_STATE_LAST_ACK = 8
TCP_STATE_TIME_WAIT = 9
TCP_STATE_CLOSED = 10

from headers import IPv4Header, UDPHeader, TCPHeader, \
        IP_HEADER_LEN, UDP_HEADER_LEN, TCP_HEADER_LEN, \
        TCPIP_HEADER_LEN, UDPIP_HEADER_LEN


#From /usr/include/linux/in.h:
IPPROTO_TCP = 6 # Transmission Control Protocol
IPPROTO_UDP = 17 # User Datagram Protocol


class UDPSocket:
    def __init__(self, local_addr, local_port,
            send_ip_packet_func, notify_on_data_func):

        self._local_addr = local_addr
        self._local_port = local_port
        self._send_ip_packet = send_ip_packet_func
        self._notify_on_data = notify_on_data_func

        self.buffer = []

    def handle_packet(self, pkt):
        self.buffer.append((b'', '0.0.0.0', 0))
        self._notify_on_data()

    @classmethod
    def create_packet(cls, src, sport, dst, dport, data=''):
        pass

    def send_packet(self, remote_addr, remote_port, data):
        pass

    def recvfrom(self):
        return self.buffer.pop(0)

    def sendto(self, data, remote_addr, remote_port):
        self.send_packet(remote_addr, remote_port, data)


class TCPListenerSocket:
    def __init__(self, local_addr, local_port, handle_new_client_func,
            send_ip_packet_func, notify_on_data_func, event_loop):

        # These are all vars that are saved away for instantiation of TCPSocket
        # objects when new connections are created.
        self._local_addr = local_addr
        self._local_port = local_port
        self._handle_new_client = handle_new_client_func

        self._send_ip_packet_func = send_ip_packet_func
        self._notify_on_data_func = notify_on_data_func
        self._event_loop = event_loop


    def handle_packet(self, pkt):
        ip_hdr = IPv4Header.from_bytes(pkt[:IP_HEADER_LEN])
        tcp_hdr = TCPHeader.from_bytes(pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN])
        data = pkt[TCPIP_HEADER_LEN:]

        if tcp_hdr.flags & TCP_FLAGS_SYN:
            sock = TCPSocket(self._local_addr, self._local_port,
                    ip_hdr.src, tcp_hdr.sport,
                    TCP_STATE_LISTEN,
                    send_ip_packet_func=self._send_ip_packet_func,
                    notify_on_data_func=self._notify_on_data_func,
                    event_loop=self._event_loop)

            self._handle_new_client(self._local_addr, self._local_port,
                    ip_hdr.src, tcp_hdr.sport, sock)

            sock.handle_packet(pkt)


class TCPSocket:
    def __init__(self, local_addr, local_port,
            remote_addr, remote_port, state,
            send_ip_packet_func, notify_on_data_func, event_loop):

        # The local/remote address/port information associated with this
        # TCPConnection
        self._local_addr = local_addr
        self._local_port = local_port
        self._remote_addr = remote_addr
        self._remote_port = remote_port

        # The current state (TCP_STATE_LISTEN, TCP_STATE_CLOSED, etc.)
        self.state = state

        # Helpful methods for helping us send IP packets and
        # notifying the application that we have received data.
        self._send_ip_packet = send_ip_packet_func
        self._notify_on_data = notify_on_data_func

        # The event loop
        self._event_loop = event_loop

        # Base sequence number
        self.base_seq_self = self.initialize_seq()

        # Base sequence number for the remote side
        self.base_seq_other = None


    @classmethod
    def connect(cls, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func, notify_on_data_func, event_loop):
        sock = cls(local_addr, local_port,
                remote_addr, remote_port,
                TCP_STATE_CLOSED,
                send_ip_packet_func, notify_on_data_func, event_loop)

        sock.initiate_connection()

        return sock


    def handle_packet(self, pkt):
        ip_hdr = IPv4Header.from_bytes(pkt[:IP_HEADER_LEN])
        tcp_hdr = TCPHeader.from_bytes(pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN])
        data = pkt[TCPIP_HEADER_LEN:]

        if self.state != TCP_STATE_ESTABLISHED:
            self.continue_connection(pkt)

        if self.state == TCP_STATE_ESTABLISHED:
            if data:
                # handle data
                self.handle_data(pkt)
            if tcp_hdr.flags & TCP_FLAGS_ACK:
                # handle ACK
                self.handle_ack(pkt)


    def initialize_seq(self):
        return random.randint(0, 65535)


    def initiate_connection(self):
        pass

    def handle_syn(self, pkt):
        pass

    def handle_synack(self, pkt):
        pass

    def handle_ack_after_synack(self, pkt):
        pass

    def continue_connection(self, pkt):
        if self.state == TCP_STATE_LISTEN:
            self.handle_syn(pkt)
        elif self.state == TCP_STATE_SYN_SENT:
            self.handle_synack(pkt)
        elif self.state == TCP_STATE_SYN_RECEIVED:
            self.handle_ack_after_synack(pkt)

    @classmethod
    def create_packet(cls, src, sport, dst, dport,
            seq, ack, flags, data=b''):
        return b''

    def send_packet(self, seq, ack, flags, data=b''):
        pass

    def handle_data(self, pkt):
        pass

    def handle_ack(self, pkt):
        pass
