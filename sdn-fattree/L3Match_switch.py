# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Theodore Wagner
CS652
Adapted from KNET Solutions/ryu-exercises/ex2_L3Match_switch.py
'''

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from math import sqrt
from random import randrange


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        #self.mac_to_port = {}
        self.route_table = {}
        self.link_list=[]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
	
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        #self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # check IP Protocol and create a match for IP
        outport = 0
	data = None
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip = pkt.get_protocol(ipv4.ipv4)
            srcip = ip.src
            dstip = ip.dst
            #self.logger.info("IP packet from %s to %s", srcip, dstip)
            #match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,ipv4_src=srcip,ipv4_dst=dstip)
            #srcmask = str(srcip) + "/24"
            #if(self.ip_mask(srcmask,dstip)==0):
            outport = self.route_lookup(dpid,dstip)
        
        elif eth.ethertype == ether_types.ETH_TYPE_ARP:
            pktarp = pkt.get_protocol(arp.arp)
            srcip = pktarp.src_ip
            dstip = pktarp.dst_ip
            #srcmask = str(scrip) + "/24"
            #if(self.ip_mask(srcmask,dstip)==0):
            outport = self.route_lookup(dpid,dstip)

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        actions = [parser.OFPActionOutput(outport)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self, None)
        switches = [switch.dp.id for switch in switch_list]
        links_list = get_link(self, None)
        self.link_list = [(link.src.dpid,link.dst.dpid,{'srcport':link.src.port_no},{'dstport':link.dst.port_no}) for link in links_list]
        #print "Switches:"
        #print switches
        #print "Links:"
        #print self.link_list
        self.build_route_table(len(switches))

    def build_route_table(self, swn):
        '''
        In a fat tree topology, number of switches swn = k^2+k
        Therefore, given swn, can derive k using the quadratic formula:

        k = [-b (+/-) sqrt(b^2 - 4*a*c)] / (2a)

        swn = k^2+k --> s(k) = k^2+k-swn
        a = 1, b = 1, c = -swn
        '''
        a=1
        b=1
        c=0-swn
        k = int(((0-b)+sqrt((b**2)-(4*a*c)))/(2*a)) if int(((0-b)+sqrt((b**2)-(4*a*c)))/(2*a))>0 else int(((0-b)-sqrt((b**2)-(4*a*c)))/(2*a))

        #With known k value, can now populate routing table
        self.route_table = {}

        '''
        Structure of entries in route_table:
        {DPID: {port:IP, port:IP}, DPID: {port:IP, port:IP},}
        '''
        
        #Aggregation Switch Entries
        for p in range(k):
            for a in range(int(k/2),k):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:01".format(p,a)).replace(":",""),16)
                if dpid not in self.route_table:
                    self.route_table[dpid] = {}
                for e in range(int(k/2)):
                    self.route_table[dpid][e]="10.{}.{}.0/24".format(p,e)
                for i in range(k/2, k):
                    self.route_table[dpid][i]="10.0.0.0/8"

        #Edge Switch Entries
        for p in range(k):
            for e in range(int(k/2)):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:01".format(p,e)).replace(":",""),16)
	        if dpid not in self.route_table:
                    self.route_table[dpid] = {}
                for x in range(2, int(k/2)+2):
                    self.route_table[dpid][x]="10.{}.{}.{}/32".format(p,e,x)
                for i in range(int(k/2)):
                    self.route_table[dpid][i]="10.0.0.0/8"

        #Core Switch Entries
        for j in range(1,int(k/2)+1):
            for i in range(1, int(k/2)+1):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:{:02}".format(k,j,i)).replace(":",""),16)
                if dpid not in self.route_table:
                    self.route_table[dpid] = {}
                for p in range(k):
                    self.route_table[dpid][p]="10.{}.0.0/16".format(p)

    def route_lookup(self,dpid,ip):
        '''
        dpid = switch that received the packet
        ip = destination IP address
        '''
        paths = self.route_table[dpid]
        evals = {}
        for port, addr in paths.items():
            evals[port] = self.ip_mask(addr, ip)
        target = max(evals.values())#Represents the length of the longest-matched prefix
        matches = []
        for port, length in evals.items():
            if length == target:#Get all ports which hold the longest-matched prefix
                matches.append(port)
        if(len(matches) == 1):
                return matches[0]#return port of longest-matched prefix
        else:
                #use randrange to randomly select from ports, to not monopolize any one port
                return matches[randrange(len(matches))]

    def ip_mask(self, rip, pip):
        '''
        rip = route IP, format "10.p.s.x/n"
        pip = provided/packet IP, format "10.a.b.c"
        '''
        rip,mask = rip.split("/")
        otc = int(int(mask)/8)#octets to check for masking
        rip = rip.split(".")
        pip = pip.split(".")
        for o in range(otc):
            if(rip[o] != pip[o]):
                 return 0
        return otc*8

    '''
    def get_pair_dpid(self,dpid,port):
        for link in self.link_list:
            if link[0] == dpid and link[2]['srcport'] == port:
                return link[1]
    '''
