'''
Test the Subnet.__contains__() method
>>> IPAddress('10.20.0.1') in Subnet(IPAddress('10.20.0.0'), 23)
None
>>> IPAddress('10.20.1.0') in Subnet(IPAddress('10.20.0.0'), 23)
None
>>> IPAddress('10.20.1.255') in Subnet(IPAddress('10.20.0.0'), 23)
None
>>> IPAddress('10.20.2.0') in Subnet(IPAddress('10.20.0.0'), 23)
None
>>> IPAddress('10.20.0.1') in Subnet(IPAddress('10.20.0.0'), 24)
None
>>> IPAddress('10.20.0.255') in Subnet(IPAddress('10.20.0.0'), 24)
None
>>> IPAddress('10.20.1.0') in Subnet(IPAddress('10.20.0.0'), 24)
None
>>> IPAddress('10.20.0.1') in Subnet(IPAddress('10.20.0.0'), 25)
None
>>> IPAddress('10.20.0.127') in Subnet(IPAddress('10.20.0.0'), 25)
None
>>> IPAddress('10.20.0.128') in Subnet(IPAddress('10.20.0.0'), 25)
None
>>> IPAddress('10.20.0.1') in Subnet(IPAddress('10.20.0.0'), 26)
None
>>> IPAddress('10.20.0.63') in Subnet(IPAddress('10.20.0.0'), 26)
None
>>> IPAddress('10.20.0.64') in Subnet(IPAddress('10.20.0.0'), 26)
None
>>> IPAddress('10.20.0.1') in Subnet(IPAddress('10.20.0.0'), 27)
None
>>> IPAddress('10.20.0.31') in Subnet(IPAddress('10.20.0.0'), 27)
None
>>> IPAddress('10.20.0.32') in Subnet(IPAddress('10.20.0.0'), 27)
None
>>> IPAddress('2001:db8:f00d::1') in Subnet(IPAddress('2001:db8::'), 32)
None
>>> IPAddress('2001:db8:f00d::1') in Subnet(IPAddress('2001:db8::'), 64)
None
>>> IPAddress('2001:db8::feed:1') in Subnet(IPAddress('2001:db8::'), 96)
None
'''

import binascii
import socket

int_type_int = type(0xff)
int_type_long = type(0xffffffffffffffff)

class IPAddress(object):
    '''
    An IP address object.  The `address` instance var is an int.  If it is an
    IPv6 address, then its length is 128 bits; otherwise, it is an IPv4
    address, and its length is 32 bits.  This length is contained in the
    `address_len` instance var.
    '''
    def __init__(self, address, family=None):
        if isinstance(address, (int_type_int, int_type_long)):
            assert family is not None, 'Address family must be specified'
            self.address_family = family
            if self.address_family == socket.AF_INET6:
                self.address_len = 128
            else:
                self.address_len = 32
            self.address = address
        else: # str
            if ':' in address:
                self.address_len = 128
                self.address_family = socket.AF_INET6
            else:
                self.address_len = 32
                self.address_family = socket.AF_INET
            self.address = self.__class__._str_to_int(address, self.address_family)

    @classmethod
    def _int_to_str(cls, address, family):
        '''Convert an integer value to an IP address string, in presentation format.'''
        if family == socket.AF_INET6:
            address_len = 128
        else:
            address_len = 32
        return socket.inet_ntop(family, binascii.unhexlify(('%x' % address).zfill(address_len >> 2)))

    @classmethod
    def _str_to_int(cls, address, family):
        '''Convert an IP address string, in presentation format, to an integer.'''
        return int_type_long(binascii.hexlify(socket.inet_pton(family, address)), 16)

    @classmethod
    def _all_ones(cls, n_bits):
        '''Return an int that is n_bits bits long and whose value is all ones.'''
        return 2**n_bits - 1

    def __hash__(self):
        return hash(self.address)

    def __str__(self):
        return self.__class__._int_to_str(self.address, self.address_family)

    def __eq__(self, other):
        return self.address == other.address

    def __lt__(self, other):
        return self.address < other.address

    def __add__(self, other):
        assert isinstance(other, (int_type_int, int_type_long))
        return IPAddress(self.address + other, self.address_family)

    def __sub__(self, other):
        assert isinstance(other, (int_type_int, int_type_long))
        return IPAddress(self.address - other, self.address_family)

    def mask(self, prefix_len):
        '''Return the mask for the given prefix length, as an integer.
        Specifically, the mask should be an integer in which the most
        significant prefix_len bits are 1 and the least significant
        (self.address_len - prefix_len) bits are 0.'''
        #FIXME
        pass

    def subnet(self, prefix_len):
        return Subnet(IPAddress(self.prefix(prefix_len), self.address_family), prefix_len)

class Subnet(object):
    def __init__(self, prefix, prefix_len):
        self.prefix = prefix
        self.prefix_len = prefix_len

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%s/%d' % (self.prefix, self.prefix_len)

    def __contains__(self, ip):
        '''Return True if the address corresponding to this IP instance is
        within this subnet, False otherwise.'''
        #FIXME
        return None

    def __hash__(self):
        return hash((self.prefix, self.prefix_len))

    def __eq__(self, other):
        return self.prefix == other.prefix and self.prefix_len == other.prefix_len

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
        #FIXME
        return None, None
