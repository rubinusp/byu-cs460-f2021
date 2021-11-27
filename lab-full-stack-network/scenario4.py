#!/usr/bin/python3

import argparse
import random
import socket
import sys
import traceback

from scapy.all import ARP, Ether, IP, Raw, TCP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from cougarnet.networksched import NetworkEventLoop

from echoserver import EchoServerTCP
from host import ETH_P_ARP, ARPOP_REQUEST, ARPOP_REPLY
from nc import NetcatTCP
from transporthost import TransportHost


B_PORT = 4567

class SimHost(TransportHost):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.dst == self.int_to_info[intf].ipv4addrs[0]:
                    if ip.proto == IP_PROTOS.tcp:
                        tcp = ip.getlayer(TCP)
                        data = ip.getlayer(Raw)
                        if data is not None:
                            data = bytes(data).decode('utf-8')
                            data = data[:20]
                            if len(data) > 20:
                                data += f'... Len={len(data)})'
                        else:
                            data = ''
                        flags = tcp.sprintf('%TCP.flags%')
                        self.log(f'Received TCP packet ({ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport})' + \
                                f'    Flags: {flags}, Seq={tcp.seq}, Ack={tcp.ack}, Data={data}')
            #elif eth.type == ETH_P_ARP:
            #    arp = eth.getlayer(ARP)
            #    if arp.op == ARPOP_REQUEST:
            #        op = 'REQUEST'
            #        self.log(f'Received ARP {op} from {arp.psrc}/{arp.hwsrc} for {arp.pdst} on {intf}.')
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def start_nc(self, remote_addr, remote_port, event_loop):
        intf = self.get_first_interface()
        local_addr = self.int_to_info[intf].ipv4addrs[0]
        local_port = random.randint(1024, 65536)

        nc = NetcatTCP(local_addr, local_port,
                remote_addr, remote_port,
                self.send_packet, event_loop)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, nc.sock)
        self.nc = nc

    def start_echo(self, local_port, event_loop):
        intf = self.get_first_interface()
        local_addr = self.int_to_info[intf].ipv4addrs[0]

        echo = EchoServerTCP(local_addr, local_port,
                self.install_socket_tcp,
                self.send_packet, event_loop)
        self.install_listener_tcp(local_addr, local_port, echo.sock)
        self.echo = echo

    def send_to_nc(self, msg):
        self.nc.send(msg)

    def schedule_items(self, event_loop):
        pass

class SimHostA(SimHost):

    def schedule_items(self, event_loop):
        args = ('10.0.2.2', B_PORT, event_loop)

        event_loop.schedule_event(12, self.start_nc, args)
        event_loop.schedule_event(13, self.send_to_nc, ('hello world (A)',))
        event_loop.schedule_event(16, self.send_to_nc, ('hello Provo (A)',))

class SimHostB(SimHost):

    def schedule_items(self, event_loop):
        args = ('10.0.2.2', B_PORT, event_loop)

        event_loop.schedule_event(14, self.start_nc, args)
        event_loop.schedule_event(15, self.send_to_nc, ('hello internet (B)',))
        event_loop.schedule_event(17, self.send_to_nc, ('hello BYU (B)',))

class SimHostD(SimHost):
    def schedule_items(self, event_loop):
        args = (B_PORT, event_loop)

        event_loop.schedule_event(10, self.start_echo, args)

def main():
    parser = argparse.ArgumentParser()

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'b':
        cls = SimHostB
    elif hostname == 'd':
        cls = SimHostD
    else:
        cls = SimHost

    host = cls(False)
    event_loop = NetworkEventLoop(host._handle_frame)
    host.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
