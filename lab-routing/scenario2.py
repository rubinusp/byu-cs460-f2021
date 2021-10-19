#!/usr/bin/python3

import socket
import subprocess
import traceback

from scapy.all import Ether, IP
from scapy.data import IP_PROTOS 
from scapy.layers.inet import ETH_P_IP

from cougarnet.networksched import NetworkEventLoop

from dvrouter import DVRouter

class SimHost(DVRouter):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.proto == IP_PROTOS.icmp:
                    self.log(f'Received ICMP packet from {ip.src} on {intf}.')
        except:
            traceback.print_exc()

    def send_icmp_echo(self, dst):
        cmd = ['ping', '-W', '1', '-c', '1', dst]
        self.log(f'Sending ICMP packet to {dst}')
        subprocess.run(cmd)

    def drop_link(self, intf):
        cmd = ['sudo', 'iptables', '-A', 'INPUT', '-i', intf, '-j', 'DROP']
        self.log(f'Dropping link {intf}')
        subprocess.run(cmd)

    def schedule_items(self, event_loop):
        pass

class SimHost1(SimHost):
    def schedule_items(self, event_loop):
        event_loop.schedule_event(6, self.drop_link, ('r1-r5',))

class SimHost2(SimHost):
    def schedule_items(self, event_loop):
        event_loop.schedule_event(4, self.send_icmp_echo, ('r5',))
        event_loop.schedule_event(5, self.send_icmp_echo, ('r4',))
        event_loop.schedule_event(12, self.send_icmp_echo, ('r5',))
        event_loop.schedule_event(13, self.send_icmp_echo, ('r4',))

class SimHost5(SimHost):
    def schedule_items(self, event_loop):
        event_loop.schedule_event(6, self.drop_link, ('r5-r1',))

def main():
    hostname = socket.gethostname()
    if hostname == 'r1':
        cls = SimHost1
    elif hostname == 'r2':
        cls = SimHost2
    elif hostname == 'r5':
        cls = SimHost5
    else:
        cls = SimHost

    router = cls()
    event_loop = NetworkEventLoop(router._handle_frame)
    router.init_dv(event_loop)
    router.schedule_items(event_loop)
    event_loop.run()

if __name__ == '__main__':
    main()
