from mininet.topo import Topo

class FatTree(Topo):
	"Fat Tree topology"

	def build(self, k=4):
		"Build the Fat Tree topology"
		
		'''
		Define Pods:
		k total pods, each with:
		 - k/2 aggregation switches
		 - k/2 edge switches
		Switch DPID: 00:00:00:00:00:pod:switch:01 
		
		 - (k^2)/4 hosts
		Host IP: 10.pod.edge.x, x in [2,k/2+1]
		'''
		pods = {}
		ec = 0
		ac = 0
		hc = 0
		
		for p in range(k): #p = pod number
			pods[p]={}
			podaggs = []
			podedges = []
			podhosts = []
			
			for s in range(k): #s = switch number within pod, dpid = 00:00:00:00:00:p:s:01
				sdpid = "00:00:00:00:00:{:02}:{:02}:01".format(p,s)
				if(s<k/2):
					podedges.append(self.addSwitch('e' + str(ec), dpid=sdpid))
					ec += 1
				else:
					podaggs.append(self.addSwitch('a' + str(ac), dpid=sdpid))
					ac += 1
					
			for e in range(len(podedges)): #e = edge switch that hosts will connect to, IP = 10.p.e.x
				for x in range(2,k/2+2):
					hip = "10.{}.{}.{}".format(p,e,x)
					podhosts.append(self.addHost('h' + str(hc), ip=hip, prefixLen=24))
					hc += 1
			
			pods[p]["aggs"] = podaggs
			pods[p]["edges"] = podedges
			pods[p]["hosts"] = podhosts
		
		'''
		Create core switches:
		k total core switches
		Switch DPID: 00:00:00:00:00:k:j:i; j,i in [1,k/2]
		'''
		corepod = []
		cc = 0
		for j in range(1, k/2+1):
			for i in range(1, k/2+1):
				cdpid = "00:00:00:00:00:{:02}:{:02}:{:02}".format(k, j, i)
				corepod.append(self.addSwitch('c' + str(cc), dpid=cdpid))
				cc += 1
		
		'''
		Add links:
		Need to build links between:
		 - core switches and aggregation switch
			e.g., c0,c1->a0,a2,a4,a6; c2,c3->a1,a3,a5,a7
		 - every aggregation switch with every edge switch within a pod
		 - nth edge switch with nth set of k/2 hosts
			e.g., e0->h0,h1; e1->h2,h3; e2->h4,h5; e3->h6,h7
		
		Specifying the port numbers for the links:
		In pod p:
		 - aggA:ports<k/2 - coreC:port p
			equivalent to: coreC:port p - aggA:ports < k/2
			core switch connects to pod p on port p
			agg switch uses small number ports to connect to cores
			consecutive agg ports connect to the core switches in k/2 strides (e.g., a0:0-core, a0:1-core, a1:0-core, a1:1-core)
		 - aggA:ports>=k/2 - edgeE:port aggA
			agg switch uses large number ports to connect to edges
			edges connect using port A to connect to aggA
			each edge connection is the same (e.g., e0:0-a0, e1:0-a0, e0:1-a1, e1:1-a1)
		 - edgeE:ports>=k/2 - hostH (host port negligible)
			edge switch uses large number ports to connect to hosts
			host port negligible for generating the flow table, as flow table only needs to know what is connected to each switch port number (winds up being port 0, experimentally)
		'''
		for p in range(len(pods)):
			coff = 0
			for a in range(len(pods[p]["aggs"])):
				for i in range(k/2):
					#Aggregation to Core links
					self.addLink(pods[p]["aggs"][a],corepod[i+coff],i,p)
				coff += k/2
				
				for d in range(len(pods[p]["edges"])):
					#Aggregation to Edge links
					self.addLink(pods[p]["aggs"][a],pods[p]["edges"][d],d+k/2,a)
					
			hoff = 0
			for e in range(len(pods[p]["edges"])):
				for j in range(k/2):
					#Edge to Host links
					self.addLink(pods[p]["edges"][e],pods[p]["hosts"][j+hoff],j+k/2)
				hoff += k/2


topos = {'fattree': FatTree}
