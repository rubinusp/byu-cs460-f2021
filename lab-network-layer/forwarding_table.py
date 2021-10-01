'''
>>> from subnet import IPAddress, Subnet
>>> table = ForwardingTable()
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 23), 'r1-c', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 24), 'r1-d', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 25), 'r1-e', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 26), 'r1-f', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 27), 'r1-g', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 28), 'r1-h', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 29), 'r1-i', None)
>>> table.add_entry(Subnet(IPAddress('10.20.0.0'), 30), 'r1-j', None)
>>> table.add_entry(Subnet(IPAddress('0.0.0.0'), 0), 'r1-k', None)

Test the ForwardingTable.get_entry() method
>>> table.get_entry(IPAddress('10.20.0.25'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.34'))
(None, None)
>>> table.get_entry(IPAddress('10.20.1.20'))
(None, None)
>>> table.get_entry(IPAddress('10.20.3.1'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.2'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.11'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.150'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.7'))
(None, None)
>>> table.get_entry(IPAddress('10.20.0.75'))
(None, None)
'''

from subnet import IPAddress

class ForwardingTable(object):
    def __init__(self):
        self.entries = {}

    def add_entry(self, prefix, intf, next_hop):
        self.entries[prefix] = (intf, next_hop)

    def remove_entry(self, subnet):
        if subnet in self.entries:
            del self.entries[subnet]

    def get_entry(self, ip_address):
        '''
        Return the subnet entry having the longest prefix match of ip_address.
        The entry is a tuple consisting of interface and next-hop IP address.
        If there is no match, return None, None.
        '''
        if isinstance(ip_address, str):
            ip_address = IPAddress(ip_address)
        
        #FIXME - complete the rest of the method
        return None, None
