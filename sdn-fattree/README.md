## SDN Fat Tree Project
In this repository, you will find the following files:
1. fattree.py
2. L3Match_switch.py
3. playground.py
3. ryu_setup.sh

### fattree.py
This file contains the code to generate the fat tree topology.
To test the topology, use the following command:
`sudo mn --custom fattree.py --topo fattree[,k=4] --controller remote --switch ovsk,protocols=OpenFlow13 --mac`

Note that the `k` value is optional, with a default value of 4

In general, the following naming mechanisms for switches and hosts are used:
- Core Switches (DPID): 00:00:00:00:00:k:j:i; j<k/2; i<k/2
- Aggregation Switches (DPID): 00:00:00:00:00:p:s:01; p=pod number, p<k; s=aggregation switch number, k/2<=s<k
- Edge Switches (DPID): 00:00:00:00:p:s:01; p=pod number, p<k; s=edge switch number, s<k/2
  - *Note: within a pod p, the edge switches and aggregation switches number consecutively, with the edge switches receiving the lower numbers and the aggregation switches receiving the higher numbers, such that s<k*
- Hosts (IP address): 10.p.e.x; p=pod number, p<k; e=edge switch number that the host is connected to (e=s); 2<=x<k/2+2

In general, the following port/link standard is used. Additional comments may be found in comment blocks within the file:
- Core Switches
  - Port `p` connects to an aggregation switch in pod `p`
- Aggregation Switches
  - Ports `e`, such that e<k/2, connect to edge switches in order in the same pod
  - Ports `i`, such that k/2<=i<k, connect to core switches in order
- Edge Switches
  - Ports `a`, such that a<k/2, connect to aggregation switches in order in the same pod
  - Ports `x`, such that k/2<=x<k, connect to hosts

Therefore, in general, the following link behavior is observed:
- Core switch at port `p` connects to *an* aggregation switch in pod `p`
- Within a pod:
  - Aggregation switch number `a` connects on port `e` to edge switch number `e` on port `a`; that is, the port number connects to that switch number
  - Edge switches connect to host `x` with IP address `10.p.e.x` on port `x`

### L3Match_switch.py
This file is the furthest I was able to get to implement the Ryu controller. This is adapted in part from [KNetSolutions ex2_L3Match_Switch.py](https://github.com/knetsolutions/ryu-exercises/blob/master/ex2_L3Match_switch.py) file.

My logic is as follows:
- As the topology is built (triggered by a switch entering the topology), the `get_topology_data` function gets the list of switches and links between switches in the topology, and calls `build_route_table` to build the routing table.
- `build_route_table` derives the `k` value, and builds the routing table based on the predefined arrangement of ports/links from the topology (see above), which will always be true, provided this controller is run with `fattree.py`
- After initialization, a packet comes in at a switch with unique DPID.
- The `_packet_in_handler` function would parse out the source and destination IP addresses. Then, the `route_lookup` function is called based on the destination IP address and the switch DPID.
- The `route_lookup` function looks up the switch by DPID in the route table. For each entry, it calls the `ip_mask` function to perform a simple IP masking comparison.
- `ip_mask` returns the number of matching bits.
- Back in the execution of `route_lookup`, the longest-matching prefix is used. For all links at DPID, the weight of the matched prefix is evaluated. If there is only one port which has the longest match, this port is returned as the `outport` on which the packet should be forwarded. If there is more than one port, then a simple randomization is used to avoid monopolizing any one output port.
- With the evaluated `outport` returned from `route_lookup`, the `_packet_in_handler` would forward the packet out on that port of the receiving switch.

However, the functionality is not proper. Currently, the only connections that work are pings on the same /24 subnet, i.e., hosts that are attached to the same edge switch can ping each other, but no hosts which are intra- or inter-pod can ping each other.

### playground.py
This file is an early attempt at the Ryu controller. This file contains the same logic as `L3Match_switch.py` and may be ignored. I have not deleted it in case I choose to return to it.

### ryu_setup.sh
This is a simple script I wrote to handle the installation of Ryu on a fresh installation of the Mininet VM. Simply trying to install ryu via `pip` or by cloning the GitHub repo and running the contained `setup.py` encountered some dependency errors. Therefore, I wrote this script to work through each dependency and install a suitable version of the dependent packages. The execution of the script takes about 9 minutes to run, but the outcome is a proper Ryu environment.

## Remarks
Please note, as I explained above, that this prototype does *not* work properly. I am unable to support communication intra- or inter-pod, except for communication across the same edge switch. However, I wanted to explain the logic behind my work to demonstrate the understanding that I had of the project, despite being unable to properly implement all the functionality.
