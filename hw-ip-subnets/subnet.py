'''
Populate a forwarding table:
>>> table = ForwardingTable()
>>> table.add_entry(Subnet(IPAddress('0.0.0.0'), 0), 0)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 22), 1)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 23), 2)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 24), 3)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 30), 4)

Test the IPAddress.__contains__() method
>>> IPAddress('128.187.0.1') in Subnet(IPAddress('128.187.0.0'), 24)
None
>>> IPAddress('128.187.1.0') in Subnet(IPAddress('128.187.0.0'), 24)
None
>>> IPAddress('128.187.2.0') in Subnet(IPAddress('128.188.0.0'), 16)
None
>>> IPAddress('128.187.0.0') in Subnet(IPAddress('128.187.0.0'), 23)
None
>>> IPAddress('128.187.1.0') in Subnet(IPAddress('128.187.0.0'), 23)
None
>>> IPAddress('128.187.2.0') in Subnet(IPAddress('128.187.0.0'), 23)
None
>>> IPAddress('2001:db8:f00d::1') in Subnet(IPAddress('2001:db8::'), 32)
None
>>> IPAddress('2001:db8:f00d::1') in Subnet(IPAddress('2001:db8::'), 64)
None
>>> IPAddress('2001:db8::feed:1:1') in Subnet(IPAddress('2001:db8::'), 96)
None

Populate a forwarding table:
>>> table = ForwardingTable()
>>> table.add_entry(Subnet(IPAddress('0.0.0.0'), 0), 0)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 22), 1)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 23), 2)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 24), 3)
>>> table.add_entry(Subnet(IPAddress('128.187.0.0'), 30), 4)

Now test the ForwardingTable.get_forwarding_entry() method:
>>> table.get_forwarding_entry(IPAddress('128.187.0.1'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.0.3'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.0.4'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.1.1'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.2.1'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.3.1'))
None
>>> table.get_forwarding_entry(IPAddress('128.187.4.1'))
None
'''

import binascii
import socket

int_type_int = type(0xff)
int_type_long = type(0xffffffffffffffff)

class IPAddress(object):
    '''
    An IP address object.  The address instance var is an int.  If it is an
    IPv6 address, then its length is 128 bits; otherwise, it is an IPv4
    address, and its length is 32 bits.
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
        return 0

    def prefix(self, prefix_len):
        '''Return the prefix for the given prefix length, as an integer.
        Specifically, the prefix should be an integer in which the most
        significant prefix_len bits match the bits in self.address, and the
        least significant (self.address_len - prefix_len) bits are 0.'''
        #FIXME
        return 0

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
        return False

    def __hash__(self):
        return hash((self.prefix, self.prefix_len))

    def __eq__(self, other):
        return self.prefix == other.prefix and self.prefix_len == other.prefix_len

class ForwardingTable(object):
    def __init__(self):
        self.entries = {}

    def add_entry(self, subnet, intf):
        self.entries[subnet] = intf

    def remove_entry(self, subnet):
        if subnet in self.entries:
            del self.entries[subnet]

    def get_forwarding_entry(self, ip_address):
        '''
        Return the subnet entry having the longest prefix match of ip_address.
        If there is no match, return None.
        '''
        #FIXME
        return None

def main():
    import sys

    def usage():
        sys.stderr.write('''Usage: %s <prefix>/<prefix_len> <ip>\n''')

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    prefix, prefix_len = sys.argv[1].split('/')
    prefix = IPAddress(prefix)
    prefix_len = int(prefix_len)
    subnet = Subnet(prefix, prefix_len)
    ip = IPAddress(sys.argv[2])
    if ip in subnet:
        sys.stdout.write('TRUE (%s is in %s)\n' % (ip, subnet))
    else:
        sys.stdout.write('FALSE (%s is not in %s)\n' % (ip, subnet))

if __name__ == '__main__':
    main()
