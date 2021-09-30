#!/usr/bin/python3

import argparse
import os
import socket
import sys
import traceback

from scapy.all import Ether, IP, ICMP, ARP
from scapy.data import IP_PROTOS 

from cougarnet.networksched import NetworkEventLoop

from host import Host, ETH_P_ARP, ARPOP_REQUEST, ARPOP_REPLY

class SimHost(Host):
    def __init__(self, *args, **kwargs):
        super(SimHost, self).__init__(*args, **kwargs)

    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_ARP:
                arp = eth.getlayer(ARP)
                if arp.op == ARPOP_REQUEST:
                    op = 'REQUEST'
                elif arp.op == ARPOP_REPLY:
                    op = 'REPLY'
                else:
                    op = 'UNKNOWN'
                self.log(f'Received ARP {op} from {arp.psrc}/{arp.hwsrc} for {arp.pdst} on {intf}.')
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def handle_ip(self, pkt, intf):
        try:
            ip = IP(pkt)
            if ip.proto == IP_PROTOS.icmp:
                self.log(f'Received ICMP packet from {ip.src} on {intf}.')
        except:
            traceback.print_exc()
        super(SimHost, self).handle_ip(pkt, intf)

    def send_icmp_echo(self, src, dst, next_hop, id, seq):
        ip = IP(src=src, dst=dst, proto=IP_PROTOS.icmp)
        icmp = ICMP(type=8, id=id, seq=seq)
        pkt = ip / icmp / b'0123456789'

        intf = self.get_first_interface()
        self.send_packet_on_int(bytes(pkt), intf, next_hop)

    def schedule_items(self, event_loop):
        pass

class SimHostA(SimHost):
    def schedule_items(self, event_loop):
        a_to_b = ('10.0.0.2', '10.0.0.3', '10.0.0.3', 1, 1)
        a_to_c = ('10.0.0.2', '10.0.1.2', '10.0.0.1', 1, 1)

        event_loop.schedule_event(4, self.send_icmp_echo, a_to_b)
        event_loop.schedule_event(6, self.send_icmp_echo, a_to_b)
        event_loop.schedule_event(10, self.send_icmp_echo, a_to_c)

class SimHostB(SimHost):
    def schedule_items(self, event_loop):
        b_to_a = ('10.0.0.3', '10.0.0.2', '10.0.0.2', 1, 1)

        event_loop.schedule_event(8, self.send_icmp_echo, b_to_a)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'b':
        cls = SimHostB
    else:
        cls = SimHost

    host = cls(args.router)
    event_loop = NetworkEventLoop(host._handle_frame)
    host.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
