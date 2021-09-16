#!/usr/bin/python3

import os
import socket

from scapy.all import Ether, IP, ICMP
from scapy.data import ETH_P_IP, IP_PROTOS 

from cougarnet.networksched import NetworkEventLoop
from cougarnet.rawpkt import BaseFrameHandler

class Host(BaseFrameHandler):
    def __init__(self):
        super(Host, self).__init__()

    def _handle_frame(self, frame, intf):
        frame = Ether(frame)
        self.log(f'Received frame on %7s: {frame.src} -> {frame.dst}' % intf)

    def send_icmp_echo(self, src, dst, srcmac, dstmac, id, seq):
        frame = Ether(src=srcmac, dst=dstmac, type=ETH_P_IP)
        ip = IP(src=src, dst=dst, proto=IP_PROTOS.icmp)
        icmp = ICMP(type=8, id=id, seq=seq)
        response = frame / ip / icmp / b'0123456789'

        intf = self.get_first_interface()
        self.send_frame(bytes(response), intf)

    def schedule_items(self, event_loop):
        pass

class HostA(Host):
    def schedule_items(self, event_loop):
        a_to_c = ('10.0.0.1', '10.0.0.3',
                        '00:00:00:aa:aa:aa', '00:00:00:cc:cc:cc', 1, 1)
        a_to_broadcast = ('10.0.0.1', '255.255.255.255',
                        '00:00:00:aa:aa:aa', 'ff:ff:ff:ff:ff:ff', 1, 1)
        a_to_e = ('10.0.0.1', '10.0.0.5',
                        '00:00:00:aa:aa:aa', '00:00:00:ee:ee:ee', 1, 1)

        # send packet from a to c at time 4 and time 6
        # send packet from a to broadcast at time 7
        # send packet from a to e at time 9 and time 11
        event_loop.schedule_event(4, self.send_icmp_echo, a_to_c)
        event_loop.schedule_event(6, self.send_icmp_echo, a_to_c)
        event_loop.schedule_event(7, self.send_icmp_echo, a_to_broadcast)
        event_loop.schedule_event(9, self.send_icmp_echo, a_to_e)
        event_loop.schedule_event(11, self.send_icmp_echo, a_to_e)
        event_loop.schedule_event(15, self.send_icmp_echo, a_to_c)

class HostC(Host):
    def schedule_items(self, event_loop):
        c_to_a = ('10.0.0.3', '10.0.0.1',
                        '00:00:00:cc:cc:cc', '00:00:00:aa:aa:aa', 1, 1)
        e_to_a = ('10.0.0.5', '10.0.0.1',
                        '00:00:00:ee:ee:ee', '00:00:00:aa:aa:aa', 1, 1)
        event_loop.schedule_event(5, self.send_icmp_echo, c_to_a)
        event_loop.schedule_event(10, self.send_icmp_echo, e_to_a)

class HostE(Host):
    def schedule_items(self, event_loop):
        e_to_a = ('10.0.0.5', '10.0.0.1',
                        '00:00:00:ee:ee:ee', '00:00:00:aa:aa:aa', 1, 1)
        event_loop.schedule_event(8, self.send_icmp_echo, e_to_a)
        event_loop.schedule_event(14, self.send_icmp_echo, e_to_a)


def main():
    hostname = socket.gethostname()
    if hostname == 'a':
        cls = HostA
    elif hostname == 'c':
        cls = HostC
    elif hostname == 'e':
        cls = HostE
    else:
        cls = Host

    host = cls()
    event_loop = NetworkEventLoop(host._handle_frame)
    host.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
