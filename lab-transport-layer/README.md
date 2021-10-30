# Transport-Layer Lab

The objective of this assignment is to give you hands-on experience with the
transport layer, including the creation of IPv4, UDP, and TCP headers,
transport-layer multiplexing, and the TCP three-way handshake.

# Table of Contents
TODO


# Getting Started

## Update Cougarnet

Make sure you have the most up-to-date version of Cougarnet installed by
running the following in your `cougarnet` directory:

```
$ git pull
$ python3 setup.py build
$ sudo python3 setup.py install
```

Remember that you can always get the most up-to-date documentation for
Cougarnet [here](https://github.com/cdeccio/cougarnet/blob/main/README.md).


## Resources Provided

The files given to you for this lab are the following:
 - `headers.py` - a file containing a stub implementation IPv4 and TCP header
   classes, as well as a working version of a UDP header class.  This is where
   you will do your work.
 - `test_headers.py` - a file containing unit tests, which will be used to test
   IPv4 and TCP header implementations.  You will also do your work here!
 - `host.py` - a file containing a basic implementation of a host.  Note that
   this is pared down version of the `Host` class you implemented in the
   [Network-Layer Lab](https://github.com/cdeccio/byu-cs460-f2021/lab-network-layer/)
   in which the `send_packet()` method simply picks an outgoing interface,
   creates a frame with the broadcast address as its destination, and sends the
   frame out the interface.
 - `transporthost.py` - a file containing a stub implementation of a host with
   transport-layer capabilities.  It inherits from `Host` and overrides the
   `handle_udp()` and `handle_tcp()` methods.  You will also do your work here!
 - `mysocket.py` - a file containing a stub code for both a UDP and a TCP
   socket.  You will also do your work here!
 - `echoserver.py` and `nc.py` - files containing classes for applications that
   use your UDP socket implementation, specifically, an echo server and a very
   simply Netcat, respectively.
 - `scenario1.cfg` and `scenario2.cfg` -
   [network configuration files](https://github.com/cdeccio/cougarnet/blob/main/README.md#network-configuration-file)
   for testing your implementations.  Both contain the same network topology,
   but they each run different scripts in which different packets are sent.
 - `scenario1.py` and `scenario2.py` - scripts that run various tests in
   conjunction with the network configuration files.


## Topology

The files `scenario1.cfg` and `scenario2.cfg` describe two different scenarios,
but the network topology is the same for both: host `a` is connected to host
`b` via a switch, `s1`

```
+----+
| a  |
+----+
  |
  |
  |
+----+
| s1 |
+----+
  |
  |
  |
+----+
| b  |
+----+
```

`s1` has switching functionality already built in, and `a` and `b` have the
basic functionality of taking a packet, encapusulating in an Ethernet frame,
and sending it to the appropriate host on its LAN/subnet.  What you will be
adding is the transport-layer functionality--building TCP and UDP headers for
application-layer data, adding an IPv4 header, and associating those packets
with their appropriate sockets.

## Starter Commands

Take a look at the contents of `scenario1.cfg`.  Then run the following to
start it up:

Run the following command:

```
$ cougarnet --disable-ipv6 --display scenario1.cfg
```

TODO


# Part 1 - IPv4, UDP, and TCP Headers

In this part of the lab, you will write the code that will build and parse
IPv4, UDP, TCP headers.  While you have been able to get by with poking
existing headers up to this point, you will want a reliable code base for
reading and writing headers because you will be using them a lot more.


## Instructions

Complete steps 1 and 2 below to develop a code base that correctly builds and
parses IPv4, UDP, and TCP headers.  Read both steps before you begin, as it
might be easier for you to do them at the same time.


### Step 1 - Write the Code for Building and Parsing Headers

In the file `headers.py`, flesh out the `from_bytes()` and `to_bytes()` methods
in both the `IPv4Header` class and the `TCPHeader` class.  This will allow you
to create headers for each protocol from raw `bytes` instances, i.e., as read
from the wire.  Note that `UDPHeader.from_bytes()` and `UDPHeader.to_bytes()`
are fleshed out for you, to give you an idea of how this should go.


#### IPv4 Header

Please note that the diagram describing the IPv4 header is 32 bits (columns)
wide.
<table border="1">
<tr>
<th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th>
<th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th>
<th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th>
<th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr>
<td colspan="4">Version</td>
<td colspan="4">IHL</td>
<td colspan="8">Differentiated Services</td>
<td colspan="16">Total length</td></tr>
<tr>
<td colspan="16">Identification</td>
<td colspan="3">Flags</td>
<td colspan="13">Fragment offset</td></tr>
<tr>
<td colspan="8">TTL</td>
<td colspan="8">Protocol</td>
<td colspan="16">Header checksum</td></tr>
<tr>
<td colspan="32">Source IP address</td></tr>
<tr>
<td colspan="32">Destination IP address</td></tr>
<tr>
<td colspan="32">Options and padding :::</td></tr>
</table>
(See also http://www.networksorcery.com/Enp/protocol/ip.htm)

 - Version - IP version.  This will always be 4 for the IPv4 header.
 - IHL - Internet header length in 4-byte words.  The IPv4 header is 20 bytes long without
   options, so this field will always be 5.
 - Differentiated Services - This will always be 0 for our purposes.
 - Total length - This is the length of the entire IP datagram, including IP header and payload.
 - Identification - The ID field for reassembling fragmented packets.  We will not be handling
   fragmentation in this, so this field can be 0.
 - Flags - Same.
 - Fragment offset - Same.
 - TTL - Time-to-live value.  We will initialize this to 64 for any newly-create IPv4 packets.
 - Protocol - The protocol associated with the next header.  For example TCP (`IPPROTO_TCP = 6`)
   or UDP (`IPPROTO_UDP = 17`).
 - Header checksum - The checksum of the IPv4 header.  For the purposes of this lab, we will not
   be calculating a checksum, so 0 can be used here.
 - Source IP address
 - Destination IP address
 - Options and padding ::: - Not used.

#### UDP Header

Please note that the diagram describing the UDP header is 32 bits (columns)
wide.
<table border="1">
<tr>
<th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th>
<th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th>
<th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th>
<th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr>
<td colspan="16">Source Port</td>
<td colspan="16">Destination Port</td></tr>
<tr>
<td colspan="16">Length</td>
<td colspan="16">Checksum</td></tr>
</table>
(See also http://www.networksorcery.com/Enp/protocol/udp.htm)

 - Source Port
 - Destination Port
 - Length - This is the length of the entire UDP datagram, including UDP header and payload.
 - Checksum - The checksum of a pseudo IPv4 header.  For the purposes of this lab, we will
   not be calculating a UDP checksum, so 0 can be used here.

#### TCP Header

Please note that the diagram describing the TCP header is 32 bits (columns)
wide.
<table border="1">
<tr>
<th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th>
<th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th>
<th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th>
<th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr>
<td colspan="16">Source Port</td>
<td colspan="16">Destination Port</td></tr>
<tr>
<td colspan="32">Sequence Number</td></tr>
<tr>
<td colspan="32">Acknowledgment Number</td></tr>
<tr>
<td colspan="4">Data Offset</td>
<td colspan="3">reserved</td>
<td colspan="3">ECN</td>
<td colspan="6">Control Bits</td>
<td colspan="16">Window</td></tr>
<tr>
<td colspan="16">Checksum</td>
<td colspan="16">Urgent Pointer</td></tr>
<tr>
<td colspan="32">Options and padding :::</td></tr>
</table>
(See also http://www.networksorcery.com/Enp/protocol/tcp.htm)

 - Source Port
 - Destination Port
 - Sequence Number
 - Acknowledgment Number
 - Data Offset - The length of the TCP header in 4-byte words.  The TCP header is
   20 bytes long without options, so this field will always be 5.
 - reserved - always 0
 - ECN - Explicit Congestion Notification.  This will not be used in this lab,
   so this field can always be 0.
 - Control Bits (flags) - Each flag is listed below from left to right (most
   significant to least significant).  However, note that only the `SYN` and `ACK`
   flags are likely to be used for this lab.
   - `URG`
   - `ACK`
   - `PSH`
   - `RST`
   - `SYN`
   - `FIN`
 - Window - the receive window advertised by the sending host
 - Checksum - The checksum of a pseudo IPv4 header.  For the purposes of this lab, we will
   not be calculating a TCP checksum, so 0 can be used here.
 - Urgent Pointer - Not used for this lab, so this field can always be 0.


### Step 2 - Complete and Tests Code against Unit Tests

The file `test_headers.py` contains a suite of tests that use python's
[unittest module](https://docs.python.org/3/library/unittest.html).  Like the
[doctest module](https://docs.python.org/3/library/doctest.html), the
`unittest` module provides a way for automated testing of different aspects of
your code.  For each header class, there is a `bytes` instance containing the
raw bytes of the header, to be converted to an object, as well as an
instantiated header object, to be converted to `bytes`.

Run the following to test your header-handling code:

```
python3 test_headers.py
```

or, alternatively:

```
python3 -m unittest test_headers.py
```

If you have made any changes to the code in `headers.py`, the tests will most
likely fail.  That is because `headers.py` must be populated with the correct
_expected_ values.  Each place in which `correct_value` is assigned a
placeholder value, that placeholder must be replaced with the correct value.
Note that the correct values of `correct_value` for testing the `UDPHeader`
class have already been included, to give you an idea of how this should go.


# Part 2 - UDP Sockets


# Part 3 - TCP Sockets and Three-Way Handshake


# General Helps

 - You can modify `scenario1.py`, `scenario2.py`, and the corresponding
   using only your `host.py`, `subnet.py`, and `forwarding_table.py`. The other
   files used will be the stock files [you were provided](#resources-provided).
 - Save your work often, especially after you move from part to part.  You are
   welcome (and encouraged) to use a version control repository, such as
   GitHub.  However, please ensure that it is a private repository!


# Submission

Use the following commands to create a directory, place your working files in
it, and tar it up:

```
$ mkdir transport-lab
$ cp headers.py test_headers.py transporthost.py mysocket.py transport-lab
$ tar -zcvf transport-lab.tar.gz transport-lab
```
