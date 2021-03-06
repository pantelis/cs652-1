## Topology
<!---Theodore Wagner CS652--->
One of the defining characteristics of a Clos topology is *disaggregation* of the network. Traditional cluster architectures present limitations on performance and cost, usually requiring a lot more cabling and building in redundancy to cover the event of a failure. Furthermore, to meet desired bandwidth increases, the cost may be very significant to purchase higher powered equipment. Rather than scaling up (i.e., buying a beefier box to provide more processing on the network), a Clos topology allows for the network to scale out, adding more switches to easily spread out the load across the network, and providing for multiple redundant paths to the same nodes.

Both Google and Facebook employ a multi-tier Clos topology, but they implement their topologies in different ways.

### Google
Google has sequenced through to their fifth generation of a fabric architecture, which they have named Jupiter. Originally deployed in 2012, Jupiter is the first iteration of their fabric architecture to support speeds of 40G, thanks to denser merchant fabric. Jupiter was also slated to scale to more than six times the size of their then-current largest fabric, an upgrade which could not happen all at once. Therefore, unique to Jupiter was that the fabric needed to support heterogeneous hardware and speeds, as well as be able to react robustly and gracefully to events in the now very broad network. 

Building out Jupiter would require approaching it through individual building blocks, instead of treating the network holistically and applying the fabric-wide decisions to each individual component. Eventually, they decided to bridge between the approaches in Firehose (first- and second-generation fabric network, with each switch cabled to others) and Watchtower and Saturn (third- and fourth-generation fabric networks, with the largest possible chassis). The building blocks are seen here, discussed each in turn below:

![Building blocks used in the Jupiter topology](./images/Jupiter_building_blocks.png)

The unit of deployment, named Centauri, had four switch chips with 16x40G ports (see top left box). The ports could be configured as 4x10G or 40G mode, with all ports accessible on the front panel of the chassis. Employed as a ToR, the Centauri switch was configured with each switch chip as a separate subnet of machines, for organizational purposes. Each chip was configured with 48x10G for server-facing ports and 16x10G for fabric-facing ports. 

Four Centauri comprised a Middle Block (see bottom left box) for use in the aggregation block, which was designed as a 2-stage blocking network with 256x10G available for ToR and 64x40G available for the fabric. Each ToR chip connected to eight Middle Blocks, with dual redundant links. Each aggregation block (see bottom right) exposed 40G ports to the spine blocks, at either *full pop* with 512 ports available or *depop*, which had half of this number, 256.

Six Centauri created a spine block, which exposed 128x40G to the aggregation blocks (see top right). Jupiter was limited to 64 aggregation blocks to allow for full dual redundancy from each spine block to each aggregation block. In its largest configuration, Jupiter supports 1.3 Pbps bisection bandwidth among servers.

#### External Connectivity
Google takes an intentional approach to incorporating and isolating connectivity to external networks (i.e., the Internet) from their fabric topology, seeking a way to connect their external routers directly to the fabric. They explored four options, depicted graphically below: (i) reserve some links from each ToR, (ii) reserve ports in each aggregation block, (iii) reserve ports in each spine block, or (iv) build a separate aggregation block for external connectivity.

![Four options to connect to the external network](./images/Jupiter_external_connect.png)

The decision Google went with was option (iv), to build out an isolated layer of switches to peer with external routers, so as to limit the domain against which external-facing configurations needed to be applied and against which they would need to integrate their in-house routing protocols with external routing protocols. They allocated 10% of aggregate intra-cluster bandwidth for external connectivity using one to three aggregation blocks, which are identical to the aggregation blocks used for ToR connectivity, just with the ports reallocated for external connections.

### Facebook

Where Google went with a chassis-style Clos architecture, Facebook built their fabric network based on pods, and connecting the pods across the network. They define a "pod" simply as the unit of their network; it carries no physical definitions. However, the way Facebook designed their network based on these pods allowed them to take advantage of the architecture that they already had in place, using four fabric switches to support 48 ToRs in one pod. This pod unit is smaller than the previous cluster unit, allowing for easy integration into the datacenter floor plan. Furthermore, the architecture requires only mid-size switches to aggregate the ToRs into these pods, again citing the ease of scaling out over scaling up.

![A sample pod](./images/Facebook_sample_pod.png)

Facebook designed their network with an equal amount of uplink capacity for each downlink port to a ToR, meaning that the oversubscription ratio is 1:1 and the network is non-blocking. On the whole, the network is built of four independent planes of spine switches, with up to 48 switches available per spine plane. The fabric switches of the pods connect to each of the spine switches on its local plane. Finally, the spine switches connect to edge pods, which contain a flexible number of edge switches. These edge pods allow for external connectivity to outside the datacenter network. The edge pods are each capable of providing up to 7.68Tbps to the backbone, and are scalable to 100G and higher port speeds. The complete arrangement of the different pods and planes can be seen here, illustrated in three-dimensions:

![Complete schematic of fabric network topology](./images/Facebook_complete_topology.png)

This topology may be abstracted in two dimensions similar to below.

![2D Abstraction of Facebook topology](./images/Facebook_2d_abstract.png)

In this abstraction, it is important to note that the diagrammed components are "pod-ified" according to color: the edge switches all belong to the same edge pod; the spine switches and fabric switches each belong to different spine planes; and all of the ToRs which would be connected to the fabric switches belong to the same server pod. Therefore, this 2D abstraction depicts one edge pod, four spine planes, and one server pod. Any edge switch connects to all of the spine switches on that spine plane. Within the individual spine planes, the spine switches connect to each of the fabric switches on that spine plane. The connections that are omitted from this abstraction, for simplicity's sake, are the fabric switches connecting to each of the ToR switches in that server pod. Therefore, the bottom layer of this abstraction would have connections from *every* fabric switch, regardless of spine plane, to *every* ToR switch. 

As both the 3D schematic and this 2D abstraction show, the architecture distinguishes logical groupings among the switches. By "pod-ifying" their network, the modularity in the design allows for easy scaling in any dimension:

|Capacity to Scale|Component to Scale|
|-----------------|---------------|
|Compute Capacity|Add additional Server Pods|
|Intra-fabric Network Capacity|Add spine switches to Spine Planes|
|Extra-fabric Connectivity Capacity|Add Edge Pods or scale uplinks to existing edge switches|

#### External Connectivity
As mentioned in the above description, Facebook's architecture handles external connectivity through the edge switches. This model is similiar to choice (iii) from the above diagram, although the unit for external connectivity is essentially folded up and out of the rest of the topology, unlike in the depiction above. However, Facebook did not detail much more about their external connectivity.

### Conclusion
As we can see, Google and Facebook diverged in their approaches to implementing a Clos architecture in their datacenter networks. Google focused on the chassis, determining how to connect the switches at the upper layers of their topology to spread the traffic across the entire network, irrespective of what was at the edge of the network (i.e., ToR switches or external-connecting routers). Facebook, on the other hand, took a pod-based approach, grouping the switches in different layers of their topology to establish the new unit of the network. The two companies also chose different approaches to incorporating external connections to the fabric, with Google building out a separate aggregation block to isolate external traffic and Facebook connecting this external traffic directly to the edge switches.
