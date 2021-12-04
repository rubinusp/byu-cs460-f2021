#!/usr/bin/python3

import argparse
import os
import socket
import sys
import traceback

from scapy.all import IP, ICMP
from scapy.data import IP_PROTOS 

from cougarnet.networksched import NetworkEventLoop

from host import Host

class SimHost(Host):
    def __init__(self, *args, **kwargs):
        super(SimHost, self).__init__(*args, **kwargs)

    def handle_ip(self, pkt, intf):
        try:
            ip = IP(pkt)
            if ip.proto == IP_PROTOS.icmp:
                self.log(f'Received ICMP packet {ip.src} -> {ip.dst} on {intf}.')
        except:
            traceback.print_exc()
        super(SimHost, self).handle_ip(pkt, intf)

    def send_icmp_echo(self, src, dst, id, seq, ttl=None):
        ip = IP(src=src, dst=dst, proto=IP_PROTOS.icmp)
        if ttl is not None:
            ip.ttl = ttl
        icmp = ICMP(type=8, id=id, seq=seq)
        pkt = ip / icmp / b'0123456789'

        self.send_packet(bytes(pkt))

    def schedule_items(self, event_loop):
        pass

class SimHostA(SimHost):
    def schedule_items(self, event_loop):
        args = ('10.0.0.2', '10.0.2.2', 1, 1)

        event_loop.schedule_event(10, self.send_icmp_echo, args)
        
class SimHostD(SimHost):
    def schedule_items(self, event_loop):
        args = ('10.0.2.2', '10.0.0.2', 1, 1)

        event_loop.schedule_event(11, self.send_icmp_echo, args)
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'd':
        cls = SimHostD
    else:
        cls = SimHost

    host = cls(args.router)
    event_loop = NetworkEventLoop(host._handle_frame)
    host.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
