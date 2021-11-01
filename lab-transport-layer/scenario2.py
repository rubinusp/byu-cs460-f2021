#!/usr/bin/python3

import argparse
import random
import socket
import sys
import traceback

from scapy.all import Ether, ICMP, IP, Raw, TCP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from cougarnet.networksched import NetworkEventLoop

from mysocket import TCPListenerSocket, TCPSocket, TCP_STATE_ESTABLISHED, TCP_FLAGS_ACK
from transporthost import TransportHost


B_PORT = 1234

class SimHost(TransportHost):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.dst == self.int_to_info[intf].ipv4addrs[0]:
                    if ip.proto == IP_PROTOS.tcp:
                        tcp = ip.getlayer(TCP)
                        flags = tcp.sprintf('%TCP.flags%')
                        self.log(f'Host received TCP packet ({ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport})' + \
                                f'    Flags: {flags}, Seq={tcp.seq}, Ack={tcp.ack}')
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def connect_and_install(self, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func, notify_on_data_func, event_loop1):

        sock = TCPSocket.connect(local_addr, local_port,
                remote_addr, remote_port,
                send_ip_packet_func, notify_on_data_func, event_loop1)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, sock)

    def send_packet_as_if_connected(self, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func, notify_on_data_func, event_loop1):

        sock = TCPSocket(local_addr, local_port,
                remote_addr, remote_port, TCP_STATE_ESTABLISHED,
                send_ip_packet_func, notify_on_data_func, event_loop1)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, sock)
        sock.send_packet(random.randint(0, 0xffffffff),
                random.randint(0, 0xffffffff), TCP_FLAGS_ACK, b'')

    def do_nothing(self):
        pass


class SimHostA(SimHost):
    def schedule_items(self, event_loop):
        args1 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing, event_loop)
        args2 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing, event_loop)
        args3 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing, event_loop)

        event_loop.schedule_event(5, self.connect_and_install, args1)
        event_loop.schedule_event(7, self.connect_and_install, args2)
        event_loop.schedule_event(8, self.send_packet_as_if_connected, args3)

class SimHostB(SimHost):
    def schedule_items(self, event_loop):

        def setup_server():
            sock = TCPListenerSocket('10.0.0.2', B_PORT,
                    self.install_socket_tcp,
                    self.send_packet, self.do_nothing, event_loop)
            self.install_listener_tcp('10.0.0.2', B_PORT, sock)

        event_loop.schedule_event(6, setup_server)

class SimHostC(SimHost):
    def schedule_items(self, event_loop):
        args = ('10.0.0.3', random.randint(1024, 65535), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing, event_loop)

        event_loop.schedule_event(9, self.connect_and_install, args)

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
    elif hostname == 'c':
        cls = SimHostC
    else:
        cls = SimHost

    host = cls(args.router)
    event_loop = NetworkEventLoop(host._handle_frame)
    host.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
