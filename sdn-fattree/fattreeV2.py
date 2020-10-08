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
					podedges.append(self.addSwitch('e' + str(ec), dpid='%x' & sdpid))
					ec += 1
				else:
					podaggs.append(self.addSwitch('a' + str(ac), dpid='%x' & sdpid))
					ac += 1
					
			for e in range(len(podedges)): #e = edge switch that hosts will connect to, IP = 10.p.e.x
				for x in range(2,k/2+1):
					hip = "10."+str(p)+"."+str(e)+"."+str(x)
					host = self.addHost('h' + str(hc))
					host.setIP(self,hip,prefixLen=24)
					podhosts.append(host)
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
				cdpid = "00:00:00:00:00:{:02}:{:02}:{:02}".format(j, k, i)
				corepod.append(self.addSwitch('c' + str(cc), dpid='%x' & cdpid))
				cc += 1
		
		'''
		Add links:
		Need to build links between:
		 - core switches and aggregation switch
			e.g., c0,c1->a0,a2,a4,a6; c2,c3->a1,a3,a5,a7
		 - every aggregation switch with every edge switch within a pod
		 - nth edge switch with nth set of k/2 hosts
			e.g., e0->h0,h1; e1->h2,h3; e2->h4,h5; e3->h6,h7

		#Core to Aggregation Links
		for p in range(len(pods)):
			coff = 0
			for agg in pods[p]["aggs"]:
				for i in range(k/2):
					self.addLink(agg,corepod[i+coff])
				coff += k/2
		
		#Aggregation to Edge Links
		for p in range(len(pods)):
			for agg in pods[p]["aggs"]:
				for edge in pods[p]["edges"]:
					self.addLink(agg,edge)
		
		#Edge to Host Links
		for p in range(len(pods)):
			hoff = 0
			for edge in pods[p]["edges"]:
				for j in range(k/2):
					self.addLink(edge, pods[p]["hosts"][j+hoff])
				hoff += k/2
		'''
		for pod in pods.values():
			coff = 0
			for agg in pod["aggs"]:
				for i in range(k/2):
					#Aggregation to Core links
					self.addLink(agg,corepod[i+coff])
				coff += k/2
        
				hoff = 0
				for edge in pod["edges"]:
					#Aggregation to Edge links
					self.addLink(agg,edge)
					for j in range(k/2):
						#Edge to Host links
						self.addLink(edge, pod["hosts"][j+hoff])
					hoff += k/2

topos = {'fattree': FatTree}
