import socket
import subprocess

from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import rtscopes
from pyroute2.netlink.exceptions import NetlinkError

class ForwardingTableNative(object):
    def __init__(self):
        self._ip = IPRoute()

    def add_entry(self, prefix, intf, next_hop):
        '''
        Add forwarding entry mapping prefix to interface and next hop IP
        address.

        prefix: str instance
        '''

        if '/' not in prefix:
            if ':' in prefix:
                prefix += '/128'
            else:
                prefix += '/32'
        kwargs = { 'dst': prefix }
        if next_hop is not None:
            kwargs['gateway'] = next_hop
        if intf is not None:
            idx = self._ip.link_lookup(ifname=intf)[0]
            kwargs['oif'] = idx

        self._ip.route('add', **kwargs)

    def remove_entry(self, prefix):
        '''
        Remove the forwarding entry matching prefix.

        prefix: str
        '''

        if '/' not in prefix:
            if ':' in prefix:
                prefix += '/128'
            else:
                prefix += '/32'
        self._ip.route('del', dst=prefix)

    def flush(self, family=None, global_only=True):
        '''
        Flush the routing table.

        prefix: str
        '''

        routes = self.get_all_entries(family=family, \
                resolve=False, global_only=global_only)

        for prefix in routes:
            self.remove_entry(prefix)


    def get_entry(self, ip_address):
        '''
        Return the subnet entry having the longest prefix match of ip_address.
        The entry is a tuple consisting of interface and next-hop IP address.
        If there is no match, return None, None.

        ip_address: str
        '''

        try:
            route = self._ip.route('get', dst=ip_address)[0]
        except (NetlinkError, IndexError):
            return None, None

        if 'attrs' not in route:
            return None, None
        attrs = dict(route['attrs'])
        if 'RTA_GATEWAY' in attrs:
            next_hop = attrs['RTA_GATEWAY']
        else:
            next_hop = None
        if 'RTA_OIF' in attrs:
            intf = socket.if_indextoname(attrs['RTA_OIF'])
        else:
            intf = None
        return intf, next_hop

    def get_all_entries(self, family=None, resolve=False, global_only=True):
        routes = self._ip.get_routes()
        entries = {}
        for route in routes:
            if 'attrs' not in route or \
                    'dst_len' not in route:
                continue
            if global_only and \
                    'scope' in route and \
                    route['scope'] != rtscopes['RT_SCOPE_UNIVERSE']:
                continue
            if family is not None and route['family'] != family:
                continue
            prefix_len = route['dst_len']
            attrs = dict(route['attrs'])
            if prefix_len == 0:
                if route['family'] == socket.AF_INET:
                    prefix = '0.0.0.0/0'
                else:
                    prefix = '::/0'
            elif route['family'] == socket.AF_INET and prefix_len == 32:
                prefix = attrs['RTA_DST']
            elif route['family'] == socket.AF_INET6 and prefix_len == 128:
                prefix = attrs['RTA_DST']
            else:
                prefix = f"{attrs['RTA_DST']}/{prefix_len}"
            if 'RTA_GATEWAY' in attrs:
                next_hop = attrs['RTA_GATEWAY']
            else:
                next_hop = None
            if 'RTA_OIF' in attrs:
                intf = socket.if_indextoname(attrs['RTA_OIF'])
            else:
                intf = None
            if resolve:
                if '/' not in prefix:
                    try:
                        prefix = socket.getnameinfo((prefix, 0), 0)[0]
                    except:
                        pass
                if next_hop is not None:
                    try:
                        next_hop = socket.getnameinfo((next_hop, 0), 0)[0]
                    except:
                        pass
            entries[prefix] = (intf, next_hop)
        return entries
