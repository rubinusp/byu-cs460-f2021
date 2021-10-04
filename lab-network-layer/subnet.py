'''
Test the Subnet.__contains__() method
>>> '10.20.0.1' in Subnet('10.20.0.0/23')
None
>>> '10.20.1.0' in Subnet('10.20.0.0/23')
None
>>> '10.20.1.255' in Subnet('10.20.0.0/23')
None
>>> '10.20.2.0' in Subnet('10.20.0.0/23')
None
>>> '10.20.0.1' in Subnet('10.20.0.0/24')
None
>>> '10.20.0.255' in Subnet('10.20.0.0/24')
None
>>> '10.20.1.0' in Subnet('10.20.0.0/24')
None
>>> '10.20.0.1' in Subnet('10.20.0.0/25')
None
>>> '10.20.0.127' in Subnet('10.20.0.0/25')
None
>>> '10.20.0.128' in Subnet('10.20.0.0/25')
None
>>> '10.20.0.1' in Subnet('10.20.0.0/26')
None
>>> '10.20.0.63' in Subnet('10.20.0.0/26')
None
>>> '10.20.0.64' in Subnet('10.20.0.0/26')
None
>>> '10.20.0.1' in Subnet('10.20.0.0/27')
None
>>> '10.20.0.31' in Subnet('10.20.0.0/27')
None
>>> '10.20.0.32' in Subnet('10.20.0.0/27')
None
>>> '2001:db8:f00d::1' in Subnet('2001:db8::/32')
None
>>> '2001:db8:f00d::1' in Subnet('2001:db8::/64')
None
>>> '2001:db8::feed:1' in Subnet('2001:db8::/96')
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
        '''
        Return the mask for the given prefix length, as an integer.
        Specifically, the mask should be an integer in which the most
        significant prefix_len bits are 1 and the least significant
        (self.address_len - prefix_len) bits are 0.

        prefix_len: int
        '''
        #FIXME
        return 0

class Subnet(object):
    def __init__(self, prefix, prefix_len=None):
        '''
        Instantiate a Subnet from a prefix.

        prefix: str or IPAddress instance
        prefix_len: int (only used if prefix is IPAddress instance)
        '''
        if isinstance(prefix, str):
            ip, prefix_len = prefix.split('/')
            ip = IPAddress(ip)
            self.prefix_len = int(prefix_len)
            self.prefix = ip
        else: # prefix is instance of IPAddress
            assert prefix_len is not None
            self.prefix = prefix
            self.prefix_len = prefix_len

        # TODO make something to check that the prefix is a true prefix (i.e.,
        # no host bits), not just an IP address that we convert to a prefix.
        #
        # For now, convert it to a true prefix.
        self.prefix = IPAddress( \
                self.prefix.address & self.prefix.mask(self.prefix_len), \
                self.prefix.address_family)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%s/%d' % (self.prefix, self.prefix_len)

    def __contains__(self, ip):
        '''
        Return True if the address corresponding to this IP address is within
        this subnet, False otherwise.

        ip: str or IPAddress instance
        '''

        if isinstance(ip, str):
            ip = IPAddress(ip)

        #FIXME
        return None

    def __hash__(self):
        return hash((self.prefix, self.prefix_len))

    def __eq__(self, other):
        return self.prefix == other.prefix and self.prefix_len == other.prefix_len
