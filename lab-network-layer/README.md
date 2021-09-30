# Network-Layer Lab

The objective of this assignment is to give you hands-on experience with the
network layer and how it interacts with the link layer.  To accomplish this,
you will implement the Address Resolution Protocol (ARP), forwarding tables,
and a router!


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
 - `host.py` - a file containing a stub implementation of a host (and router).
   This is where you will do your work!
 - `forwarding_table.py` - a file containing a stub implementation of an IP
   forwarding table.  You will also do your work here!
 - `scenario1.cfg`, `scenario2.cfg`, `scenario3.cfg` -
   [network configuration files](https://github.com/cdeccio/cougarnet/blob/main/README.md#network-configuration-file)
   describing three topologies for testing different aspects of functionality
   related to this lab.
 - `scenario1.py`, `scenario2.py`, `scenario3.py` -
   scripts that run various tests in conjunction with the network configuration
   files.


# Part 1 - Address Resolution Protocol (ARP)

## Scenario Description

The file `scenario1.cfg` describes a network with three hosts and one router:
`a`, `b`, and `r1` connected to switch `s1`, and `c` and `r1` connected to
switch `s2`.  The topology looks like this:

```
         +----+
          | a  |
          +----+
            |
            |
            |
+---+     +----+
| b | --- | s1 |
+---+     +----+
            |
            |
            |
          +----+
          | r1 | -+
          +----+  |
          +----+  |
          | c  |  |
          +----+  |
            |     |
            |     |
            |     |
          +----+  |
          | s2 | -+
          +----+
```

The switch is a working switch; you do not have to implement its functionality!  
Your focus is on the host/router functionality.


## Starter Commands

Take a look at the contents of `scenario1.cfg`.  Then run the following to
start it up:

Run the following command:

```
$ cougarnet --disable-ipv6 --display scenario1.cfg
```

After a few seconds of awkward silence, you will see output on the terminal
corresponding to Host `a`.  The output is made by placeholder code in
`host.py`.  Instead of sending packets, it simply prints out that that's what
it would do.  What is missing at this point is:

 - a mechanism to map the IP address of the next hop to a MAC address - ARP!;
 - an Ethernet frame header to encapsulate the IP packet;
 - some logic to determine which frames should be acted upon

When these things are added, you will be able to send IP packets across a local
area network (LAN), as long as you know the outgoing interface and the next-hop
IP address.  We will learn how to determine outgoing interface and next-hop in
the next part.


## Frames Issued

With `scenario1.cfg`, the `send_packet_on_int()` is called for the following
packets at the following times (note that times are approximate).  Each
sub-bullet describes the purpose of the primary bullet under which it is
listed.

 - 4 seconds: packet sent from `a` to `b`
   - There is initially no ARP entry for `b`'s IP address in `a`'s table.
   - `a`'s ARP request should be seen by all hosts on the same LAN.
   - After the ARP response is received by `a`, the ICMP packet from `a` should
     be seen by (only) `b`.
 - 6 seconds: packet sent from `a` to `b`
   - There is already an ARP entry for `b`'s IP address in `a`'s table.
   - The ICMP packet from `a` should be seen by (only) `b`.
 - 8 seconds: packet sent from `b` to `a`
   - There is already an ARP entry for `a`'s IP address in `b`'s table (from
     the previous ARP request).
   - The ICMP packet from `b` should be seen by (only) `a`.
 - 10 seconds: packet sent from `a` to `c` (next hop: `r1`)
   - There is initially no ARP entry for `r1`'s IP address in `a`'s table.
   - `a`'s ARP request should be seen by all hosts on the same LAN.
   - After the ARP response is received by `a`, the ICMP packet from `a` should
     be seen by (only) `b`.
   - The ICMP packet from `a` should be seen by (only) `r1`. Once IP forwarding
     is working (Part 3), then `c` will also see the packet.


## Instructions

In the file `host.py`, flesh out following the skeleton methods related to ARP:

 - `send_packet_on_int()`.  This method takes the following as as arguments:

   - `pkt`: an IP packet, complete with IP header.  Generally, this could be
     either an IPv4 or an IPv6 packet, but for the purposes of this lab, it
     will just be IPv4.
   - `intf`: the name of an interface on the host, on which the packet will be
     sent.
   - `next_hop`: the IP address of the next hop for to the packet, which is
     either the IP destination, if on the same subnet as the host, or the IP
     address of a router.
   
   The method should do the following:

   - Find the MAC address corresponding to `next_hop`, the next-hop IP address.
     To do this, it should check the host-wide ARP table to see if a mapping
     already exists.

     If a mapping exists, then it can simply build an Ethernet frame consisting
     of:

     - Destination MAC address: the MAC address corresponding to the next-hop
       IP address.
     - Source MAC address: the MAC address corresponding to the outgoing
       interface.  This can be found with the `int_to_info` attribute, which is
       documented
       [here](https://github.com/cdeccio/cougarnet/blob/main/README.md#baseframehandler).
     - Type IP (`ETH_P_IP = 0x0800`)
     - The IP packet as the Ethernet payload.

     Then it can send that frame by calling the `send_frame()` method (which is
     defined in the parent class).

     If no mapping exists, then it does the following:

     - queue the packet, along with interface and next hop, for later sending
     - create an ARP request, such that:
       - The sender IP address is the IP address associated with the outgoing
	 interface.  This can be found with the `int_to_info`
         [attribute](https://github.com/cdeccio/cougarnet/blob/main/README.md#baseframehandler)
         of the host.
       - The sender MAC address is the MAC address corresponding to the outgoing
         interface.
       - The target IP address is the next-hop IP address.
       - The target MAC address is all zeroes (this field is ignored by the receiver).
       - The MAC address of the incoming interface is used as the sender MAC
         address.
       - The opcode is request (`ARPOP_REQUEST = 1`).

     - build and send an Ethernet frame containing the ARP request, consisting
       of:
       - Destination MAC address: the Ethernet broadcast address:
         (`ff:ff:ff:ff:ff:ff`)
       - Source MAC address: the MAC address corresponding to the outgoing
         interface.
       - Type ARP (`ETH_P_ARP =  0x0806`)
       - The ARP request as the Ethernet payload.

     The IP packet will get sent later, when the ARP response is received.

 - `handle_arp()`.  This method takes the following as as arguments:

   - `pkt` - the ARP packet received
   - `intf` - the interface on which it was received

   This method is called when an Ethernet frame is received by a node, and the
   type field of the Ethernet frame header indicates that the Ethernet payload
   is an ARP packet (i.e., its `type` is `ETH_P_ARP`).

   The method should do the following:

   - Determine whether the ARP packet is an ARP request or an ARP response
     (i.e., using the opcode field), then call `handle_arp_response()` or
     `handle_arp_request()` accordingly.

 - `handle_arp_request()`.  This method takes the same arguments as
   `handle_arp()`:

   The method should do the following:

   - Parse out the IP address and MAC address of the sender.
   - Update its own ARP table with an entry that maps the IP address of the
     sender to the MAC address of the sender.
   - If the target IP address matches an IPv4 address on the incoming
     interface, `intf`, then create an ARP response such that:
     - The sender and target IP addresses are reversed.
     - The sender MAC address is used as the target MAC address.
     - The MAC address of the incoming interface is used as the sender MAC
       address.
     - The opcode is reply (`ARPOP_REPLY = 2`).
   - build and send an Ethernet frame containing the ARP response, consisting
     of:
     - Destination MAC address: the MAC address of the entity that sent the
       request sender (i.e., matching the target address in the ARP response).
     - Source MAC address: the MAC address corresponding to the interface on
       which the request was received (and which will also the outgoing
       interface).
     - Type ARP (`ETH_P_ARP = 0x0806`)
     - The ARP response packet as the Ethernet payload.

 - `handle_arp_response()`.  This method takes the same arguments as
   `handle_arp()`:

   The method should do the following:

   - Parse out the IP address and MAC address of the sender.
   - Update its ARP table with an entry that maps the IP address of the
     sender to the MAC address of the sender.
   - Go through its queue of packets that were waiting for this ARP response,
     i.e., those whose next hop corresponds to the sender IP address in the
     response. Send all the packets.

 - `_handle_frame()`.  This method takes the following as as arguments:

   - `frame` - the Ethernet frame received
   - `intf` - the interface on which it was received

   The method should do the following:

   - Parse out the destination MAC address in the frame.
   - If the destination MAC address either matches the MAC address
     corresponding to the interface on which it was received or is the
     broadcast MAC address (`ff:ff:ff:ff:ff:ff`), then call another method to
     handle the payload, depending on its type:
     - For type `ETH_P_IP`, extract the payload and call `handle_ip()`, passing
       the Ethernet payload and the interface on which it arrived.
     - For type `ETH_P_ARP`, extract the payload and call `handle_arp()`,
       passing the Ethernet payload and the interface on which it arrived.
     - For all other types, take no further action.
   - If the destination address does not match or is not the Ethernet
     broadcast, then call `not_my_frame()`.

 - `not_my_frame()`.  There is no need to flesh out this method.  It is simply
   a placeholder for debugging.


## Testing

Test your implementation against scenario 1.  Determine the appropriate
output--that is, which hosts should receive which frames--and make sure that
the cougarnet output matches appropriately.

When it is working properly, test also with the `--terminal=none` option:

```
$ cougarnet --disable-ipv6 --terminal=none scenario1.cfg
```

## Helps


## Helps

### Ethernet Frames

See the documentation for the Link-Layer lab for
[additional helps for Ethernet frames](#https://github.com/cdeccio/byu-cs460-f2021/blob/master/lab-link-layer/README.md#ethernet-frames).

Note that there are libraries for parsing Ethernet frames and higher-level
packets, but you may not use them for the lab.


### ARP Packets

| Offset | Byte 0 | Byte 1 |
| :---: | :---: | :---: |
| 0 |<td colspan="2"> Hardware Type |
| 2 |<td colspan="2"> Protocol Type |
| 4 | Hardware Address Length | Protocol Address Length |
| 6 |<td colspan="2">operation |
| 8 |<td colspan="2">Sender hardware address (bytes 0 - 1) |
| 10 |<td colspan="2">Sender hardware address (cont'd) (bytes 2 - 3) |
| 12 |<td colspan="2">Sender hardware address (cont'd) (bytes 4 - 5) |
| 14 |<td colspan="2">Sender protocol address (bytes 0 - 1) |
| 16 |<td colspan="2">Sender protocol address (cont'd) (bytes 2 - 3) |
| 18 |<td colspan="2">Target hardware address (bytes 0 - 1) |
| 20 |<td colspan="2">Target hardware address (cont'd) (bytes 2 - 3) |
| 22 |<td colspan="2">Target hardware address (cont'd) (bytes 4 - 5) |
| 24 |<td colspan="2">Target protocol address (bytes 0 - 1) |
| 26 |<td colspan="2">Target protocol address (cont'd) (bytes 2 - 3) |

Regarding the fields:
 - Hardware Type will always be Ethernet (`ARPHRD_ETHER = 1`)
 - Protocol Type will always be IPv4 (`ETH_P_IP = 0x0800`)
 - Hardware Address Length will always be 6 (MAC addresses are six bytes
   long)
 - Protocol Address Length will always be 4 (IPv4 addresses are four bytes
   long)
 - Operation (or opcode) will either be request (`ARPOP_REQUEST = 1`) or replay (`ARPOP_REPLY = 2`).
 - While "Hardware" and "Protocol" are the more generic terms for the fields,
   they are referred to in the instructions as "MAC" and "IP" since those are
   the protocols we are working with.


# Part 2 - Forwarding Table

# Part 3 - IP Forwarding

# Submission
