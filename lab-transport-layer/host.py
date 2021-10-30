#!/usr/bin/python3

import os
import socket
import struct

from cougarnet.rawpkt import BaseFrameHandler
from cougarnet.util import \
        mac_str_to_binary, mac_binary_to_str, \
        ip_str_to_binary, ip_binary_to_str

#From /usr/include/linux/if_ether.h:
ETH_P_IP = 0x0800 # Internet Protocol packet
ETH_P_ARP = 0x0806 # Address Resolution packet

#From /usr/include/net/if_arp.h:
ARPHRD_ETHER = 1 # Ethernet 10Mbps
ARPOP_REQUEST = 1 # ARP request
ARPOP_REPLY = 2 # ARP reply

#From /usr/include/linux/in.h:
IPPROTO_TCP = 6 # Transmission Control Protocol
IPPROTO_UDP = 17 # User Datagram Protocol

class Host(BaseFrameHandler):
    def __init__(self, ip_forward):
        super(Host, self).__init__()

        self._ip_forward = ip_forward

    def _handle_frame(self, frame, intf):
        pkt = frame[14:]
        self.handle_ip(pkt, intf)

    def handle_ip(self, pkt, intf):
        proto = pkt[9]
        if proto == IPPROTO_TCP:
            self.handle_tcp(pkt)
        elif proto == IPPROTO_UDP:
            self.handle_udp(pkt)

    def handle_tcp(self, pkt):
        pass

    def handle_udp(self, pkt):
        pass

    def send_packet_on_int(self, pkt, intf, next_hop):
        src = mac_str_to_binary(self.int_to_info[intf].macaddr)
        dst = b'\xff\xff\xff\xff\xff\xff'
        frame = dst + src + struct.pack('!H', ETH_P_IP) + pkt
        self.send_frame(frame, intf)

    def send_packet(self, pkt):
        intf = self.get_first_interface()
        self.send_packet_on_int(pkt, intf, None)
