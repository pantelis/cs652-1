# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.  #
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

"""
Theodore Wagner
CS652
"""


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, tcp, udp, icmp
from ryu.ofproto import inet
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from math import sqrt
from random import randrange


class Playground(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Playground, self).__init__(*args, **kwargs)
        #self.mac_to_port = {}
	self.route_table = {}
        self.link_list = []

    '''
    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)
    '''

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        pkteth = pkt.get_protocol(ethernet.ethernet)
	
        if pkteth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        dpid = datapath.id

        dstmac = pkteth.dst
        srcmac = pkteth.src
        
        out_port = 0

	pktipv4 = pkt.get_protocol(ipv4.ipv4)
        if(pktipv4 is not None):
             dstip = pktipv4.dst
             srcip = pktipv4.src
             out_port = route_lookup(dpid,dstip)

        #self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, srcmac, dstmac, msg.in_port)
        '''
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dstmac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dstmac]
        else:
            out_port = ofproto.OFPP_FLOOD
        '''

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        '''
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dstmac, srcmac, actions)
        '''

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        #dp_out = self.get_pair_dpid(dpid,out_port)

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    '''
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)
    '''

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self, None)
        switches = [switch.dp.id for switch in switch_list]
        links_list = get_link(self, None)
        links = [(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]
        self.link_list = links
        #print "Switches:"
        #print switches
        #print "Links:"
        #print links
        self.build_route_table(len(switches))

    def build_route_table(self, swn):
        '''
        In a fat tree topology, number of switches swn, = k^2+k
        Therefore, k can be derived from swn, using quadratic formul a:

        k = [-b (+/-) sqrt(b^2 - 4*a*c)] / (2a)

        for formula's sake, swn=k^2+k --> s(k) = k^2+k-swn
        a = 1, b = 1, c = -swn
        '''
        a=1
        b=1
        c= 0-swn
        k = int(((0-b)+sqrt(b**2-(4*a*c)))/(2*a)) if int(((0-b)+sqrt(b**2)-(4*a*c))/(2*a))>0 else int(((0-b)-sqrt(b**2-(4*a*c)))/(2*a))
        #With known k, can compute the routing tables

        route_table = {}
        #Ensure route table is empty
        '''
        route_table entries
        DPID: {port:IP, port:IP}
        '''
        
        #Aggregation Switch Entries
        for p in range(k):
            for a in range(int(k/2),k):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:01".format(p,a)).replace(":",""),16)
                if dpid not in route_table:
                    route_table[dpid] = {}
                for e in range(int(k/2)):
                    route_table[dpid][e]="10.{}.{}.0/24".format(p,e)
                for i in range(k/2, k):
                    route_table[dpid][i]="10.0.0.0/8"

        #Edge Switch Entries
        for p in range(k):
            for e in range(int(k/2)):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:01".format(p,e)).replace(":",""),16)
                if dpid not in route_table:
                    route_table[dpid] = {}
                for x in range(2,int(k/2)+2):
                    route_table[dpid][x]="10.{}.{}.{}/32".format(p,e,x)
                for i in range(0, int(k/2)):
                    route_table[dpid][i]="10.0.0.0/8"
        
        #Core Switch Entries
        for j in range(1,int(k/2)+1):
            for i in range(1,int(k/2)+1):
                dpid = int(("00:00:00:00:00:{:02}:{:02}:{:02}".format(k,j,i)).replace(":",""),16)
                if dpid not in route_table:
                    route_table[dpid] = {}
                for p in range(k):
                    route_table[dpid][p]="10.{}.0.0/16".format(p)
       
        #for switch,entries in route_table.items():
        #    print(switch, entries)

    def route_lookup(dpid,ip):
        '''
        dpid = switch that received the packet
        ip = destination IP address
        '''
        paths = route_table(dpid)
        val = {}
        for port, addr in paths.items():
            val[port] = ip_mask(addr,ip)
        target = max(val.values())
        #represents the longest-matched prefix
        matches = []
        for port, weight in val.items():
            if weight == target:
                #get all ports which hold the longest-matched prefix
                matches.append(port)
        if(len(matches) == 1):
            #return the port corresponding to longest-matched prefix
            return matches[0]
        else:
            #use randrange to randomly select from the ports, to not monopolize any one port
            return matches[randrange(len(matches))] 

    def ip_mask(rip, pip):
        '''
        rip = route IP, format "10.p.s.x/n"
        pip = provided/packet IP, format "10.a.b.c"
        '''
        rip, mask = rip.split("/")
        otc = int(int(mask)/8)
        rip = rip.split(".")
        pip = pip.split(".")
        for o in range(otc):
            if(rip[o] != pip[o]):
                return 0
        return otc*8

    def get_pair_dpid(self,dpid,port):
        for link in self.link_list:
            if link[0] == dpid and link[2]['port']==port:
                return link[1]
