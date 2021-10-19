import socket
import subprocess

class ForwardingTableNative(object):
    def add_entry(self, prefix, intf, next_hop):
        '''
        Add forwarding entry mapping prefix to interface and next hop IP
        address.

        prefix: str instance
        '''

        cmd = ['sudo', 'ip', 'route', 'add', prefix]
        if next_hop is not None:
            cmd += ['via', next_hop]
        if intf is not None:
            cmd += ['dev', intf]
        subprocess.run(cmd, check=True)

    def remove_entry(self, prefix):
        '''
        Remove the forwarding entry matching prefix.

        prefix: str
        '''

        cmd = ['sudo', 'ip', 'route', 'del', prefix]
        subprocess.run(cmd, check=True)

    def flush(self):
        '''
        Flush the routing table.

        prefix: str
        '''

        cmd = ['sudo', 'ip', 'route', 'flush', 'scope', 'global']
        subprocess.run(cmd, check=True)

    def get_entry(self, ip_address):
        '''
        Return the subnet entry having the longest prefix match of ip_address.
        The entry is a tuple consisting of interface and next-hop IP address.
        If there is no match, return None, None.

        ip_address: str
        '''

        cmd = ['ip', 'route', 'get', ip_address]
        output = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8')

        try:
            route_str = output.splitlines()[0]
        except IndexError:
            return (None, None)

        cols = route_str.split()
        if len(cols) > 1 and cols[1] == 'via':
            next_hop, intf = cols[2], cols[4]
            return intf, next_hop

        return (None, None)

    def get_all_entries(self, resolve=False, global_only=True):
        output = ''
        for v in ('-4', '-6'):
            cmd = ['ip', v, 'route', 'show']
            if global_only:
                cmd += ['scope', 'global']
            output += subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8')
            output += '\n'

        entries = {}
        for entry_str in output.splitlines():
            cols = entry_str.split()
            if len(cols) > 1 and cols[1] == 'via':
                prefix, next_hop, intf = cols[0], cols[2], cols[4]
            elif len(cols) > 1 and cols[1] == 'dev':
                prefix, next_hop, intf = cols[0], None, cols[2]
            else:
                continue
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
            else:
                if prefix == 'default':
                    prefix = '0.0.0.0/0'
            entries[prefix] = (intf, next_hop)
        return entries
