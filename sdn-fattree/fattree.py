from mininet.topo import Topo

class FatTree(Topo):
	"Fat Tree topology"

	def build(self, k=4):
		"Build the Fat Tree topology"

		#Topo.__init__(self)
	
		#self.k=k

		'''
		addSwitch()
		 - k total core switches
		 - (k^2)/2 total aggregation switches
		 - (k^2)/2 total edge switches
		'''
		cores = []
		aggs = []
		edges = []
		for i in range((k**2)/2):
			if i<k:
				cores.append(self.addSwitch('c' + str(i)))
			aggs.append(self.addSwitch('a' + str(i)))
			edges.append(self.addSwitch('e' + str(i)))			
		
		'''
		addHost()
		 - (k^3)/4 total hosts
		'''
		hosts = []
		for i in range((k**3)/4):
			hosts.append(self.addHost('h' + str(i)))

		'''
		Defining Pods:
		k total pods, each with:
		 - k/2 aggregation switches
		 - k/2 edge switches
		 - (k^2)/4 hosts
		'''
		pods = {}
		swc = 0
		hc = 0

		#Define k pods
		for i in range(k):
			pods[i]={}
			podaggs = []
			podedges = []
			podhosts = []
			
			#Group k/2 aggregation switches and k/2 edge switches to the ith pod
			for j in range(k/2):
				if(swc<len(aggs)):
					podaggs.append(aggs[swc])
					podedges.append(edges[swc])
					swc+=1
			
			#Group (k^2)/4 hosts to the ith pod
			for j in range((k**2)/4):
				if(hc<len(hosts)):
					podhosts.append(hosts[hc])
					hc+=1
			
			#Add the sets of aggregation switches, edge switches, and hosts to the pod
			pods[i]["aggs"]=podaggs
			pods[i]["edges"]=podedges
			pods[i]["hosts"]=podhosts
		
		'''
		addLink()
		Need to build links between:
		 - core switches and aggregation switch
			e.g., c0, c1->a0,a2,a4,a6; c2, c3->a1,a3,a5,a7 --> modulus operator
		 - every aggregation switch with every edge switch within a pod
		 - nth edge switch with nth set of k/2 hosts
			e.g., e0->h0,h1; e1->h2,h3; e2->h4,h5; e3->h6,h7
		'''
		#Core switch to Aggregation switch links
		'''
		 - Core switches in the first half of the topology connect to all the "first" aggs
		 - Core switches in the second half of the topology to all the "second" aggs
		'''
		for core in cores:
			for agg in aggs:
			#	if((cores.index(core)%2)==(aggs.index(agg)%2)):
			#		self.addLink(core,agg)
				if((cores.index(core)<(len(cores)/2)) and ((aggs.index(agg))%2==0)):
					self.addLink(core,agg)
				elif((cores.index(core)>=(len(cores)/2)) and ((aggs.index(agg))%2==1)):
					self.addLink(core,agg)
				
		
		#Aggegration switch to Edge switch links
		for i in range(len(pods)):
			for agg in pods[i]["aggs"]:
				for edge in pods[i]["edges"]:
					self.addLink(agg,edge)
		
		#Edge switch to Host links
		'''
		 - Find out how many edge switches there are, e
		 - Connect e hosts to each edge
		 - k/2 edges per pod; e=k/2
		 - k/2 hosts per edge switch per pod; = e
		'''
		for i in range(len(pods)):	
			ho = 0
			keynum = len(pods[i]["edges"])
			for edge in pods[i]["edges"]:
				if(ho<len(pods[i]["hosts"])):
					for j in range(keynum):
						self.addLink(edge, pods[i]["hosts"][ho+j])
					ho+=2
	
	
topos = {'fattree': FatTree}
