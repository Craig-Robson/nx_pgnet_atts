# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 11:22:25 2015

@author: a8243587

#############################################################################
Using Networks and Algorithms - An introductory appraoch (Dolan and Aldous)

Use a maximum flow algorithm to find the max flow throgh the network between a source and a sink.
    Each edge needs to have a capacity.
    Returns the maximum flow between the specified nodes.

If nodes need to have a capacity:
    Replace each node with a new edge with two nodes.
    Edge has the capacity of the node.
    One node acts as the flow into the node, the other the outflow.
        This can surely only work on directed networks??
    If multiple sources/sinks:
        Create a new super sin, edges connect the sinks to and have a infinite capacity.
        Create a new super source, edges connect to the sources and have infinite capacity.

#############################################################################
"""



import networkx as nx
import random as r
import sys, ogr
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
import nx_pg
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet_atts')
import nx_pgnet_atts as nx_pgnet_atts
import error_classes

def check_for_demand_supply_nodes(G):
    '''
    Finds all nodes with a role set as demand or supply. Creates a super node 
    where required adn returns a warning if there are no nodes with either role.
    '''
    supply_nodes, demand_nodes = get_demand_supply_nodes(G)
    added_edges = {'supply':[],'demand':[]}  
    added_nodes = {'supply':[],'demand':[]}
    if len(supply_nodes) == 0:
        print "Error. No supply nodes nominated."
        exit()
    elif len(supply_nodes) > 1:
        #if more than one supply node create a super node with teh edge capacity being equal to teh capacity of the supply node
        print "Need to create a super supply node as %s supply nodes found." %(len(supply_nodes))
        G,added_edges,added_nodes = create_supersupply_node(G, supply_nodes,added_edges,added_nodes)
        
    if len(demand_nodes) == 0:
        print "Error. No demand nodes nominated."
        exit()
    elif len(demand_nodes) > 1:
        print "Need to create a super demand node as %s demand nodes found." %(len(demand_nodes))
        G,added_edges,added_nodes = create_superdemand_node(G,supply_nodes,added_edges,added_nodes)
    
    return G,supply_nodes, demand_nodes, added_nodes, added_edges 

def get_check_supply_demand_nodes(G,supply_nodes,demand_nodes,added_nodes):
    '''
    Identify the node keys for the source and demand nodes in the network.
    '''
    if len(demand_nodes)>1:
        demand_nd = added_nodes['demand'][0]
    elif len(demand_nodes) == 1 :
        demand_nd = demand_nodes[0]
    else:
        #this situation should have already been caught
        pass

    if len(supply_nodes)>1:
        supply_nd = added_nodes['supply'][0]
    elif len(supply_nodes) ==1 :
        supply_nd = supply_nodes[0]
    else:
        #this situation should have already been caught
        pass
    
    return supply_nd,demand_nd
    
def get_demand_supply_nodes(G):
    '''
    Return all nodes which are supply nodes and those which are demand nodes.
    '''
    supply_nodes = []
    demand_nodes = []
    for nd in G.nodes():
        if G.node[nd]['role'] == 'supply':
            supply_nodes.append(nd)
        elif G.node[nd]['role'] == 'demand':
            demand_nodes.append(nd)
    return supply_nodes,demand_nodes

def create_supersupply_node(G,supply_nodes,added_edges,added_nodes):
    '''
    Create a super supply node and link it to the individual supply nodes,
    setting capacities as required.
    '''
    G.add_node('ssupply',{'role':'super_suply','ref_nodes':supply_nodes})
    added_nodes['supply'].append('ssupply')
    for nd in supply_nodes:
        cap_sum = 0
        for eg in G.out_edges(nd):
            cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
        G.add_edge('ssupply',nd,{'flow_capacity':cap_sum})
        added_edges['supply'].append(('ssupply',nd))
    
    #sum capacity of edges out of super supply node to get capacity
    cap_sum = 0
    for eg in G.out_edges('ssupply'):
        cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
    G.node['ssupply']['flow_capacity'] = cap_sum
    return G,added_edges,added_nodes

def create_superdemand_node(G,demand_nodes,added_edges,added_nodes):
    '''
    Create a super demand node and link it to the individual deamnd nodes,
    setting capacities as required.
    '''
    G.add_node('sdemand',{'role':'super_demand','ref_nodes':demand_nodes})
    added_nodes['demand'].append('sdemand')
    for nd in demand_nodes:
        cap_sum = 0
        for eg in G.in_edges(nd):
            cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
        G.add_edge(nd,'sdemand',{'flow_capacity':cap_sum})    
        added_edges['demand'].append((nd,'sdemand'))

    #sum capacity of edges into super demand node to get capacity
    cap_sum = 0
    for eg in G.in_edges('sdemand'):
        cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
    G.node['sdemand']['flow_capacity'] = cap_sum
    
    return G,added_edges,added_nodes

def remove_added_nodes_edges(G,added_edges,added_nodes):
    '''
    Remove added nodes, ie. the super demand and super supply nodes.
    '''
    for ky in added_edges.keys():
        for eg in added_edges[ky]:
            G.remove_edge(eg[0],eg[1])
        for nd in added_nodes[ky]:
            G.remove_node(nd)
    return G

def get_flow_stats(G):
    '''
    Returns dicts of the flow values for edges and nodes respectively.
    '''
    node_flows={}
    edge_flows={}
    for nd in G.nodes():
        node_flows[nd] = G.node[nd]['flow']
    for eg in G.edges():
        edge_flows[eg] = G.edge[eg[0]][eg[1]]['flow']
    
    return edge_flows, node_flows
    
def get_max_flows(G,exclude=None):
    '''
    Returns the node and edge id's with the maximum flow and the respective 
    values.
    '''
    node_flow_max = {'node':-999,'flow':0}
    edge_flow_max = {'edge':-999,'flow':0}
    edge_flows, node_flows = get_flow_stats(G)
    
    for nd in node_flows:
        if node_flows[nd] > node_flow_max['flow']:
            node_flow_max['node']=nd
            node_flow_max['flow']=node_flows[nd]
    
    for eg in edge_flows:
        if eg[0] == 'ssupply': pass #stops edges from super supply nodes being included
        elif edge_flows[eg] > edge_flow_max['flow']:
            edge_flow_max['edge']=eg
            edge_flow_max['flow']=edge_flows[eg]
        
    return node_flow_max, edge_flow_max

def assign_edge_node_flows(G, data):
    '''
    Given a dict of flow values from a maximum flow algorithm, such as the 
    ford-fulkerson, assigns edge flows and calculates and assigns node flows.
    '''
    #assign calculated flow to the dges
    for eg in G.edges():
        G.edge[eg[0]][eg[1]]['flow']=data[eg[0]][eg[1]]
    
    #sums the flows along the edges which leave the node
    for nd in data:
        flowsum = 0
        for val in data[nd]:
            flowsum += data[nd][val]
        G.node[nd]['flow'] = flowsum
    
    return G

def convert_topo(G,demand,supply,transfer,flow_capacity):
    '''
    Converts a network to a format where node capacities can be used in 
    standard flow algorithms. Replaces a node with two nodes, each with a 
    suffix, either A(inflow) or B (outflow), and adds a connecting edge which
    has the attributs of the replaced node. Edges affected are reconnected to 
    the repsective new node. This can be reverted using the revert_topo function.
    '''
    node_list = G.nodes()
    for nd in node_list:
        #add two nodes
        role = G.node[nd]['role']
        atts = G.node[nd]
        
        #new dest node
        if role == demand:
            d_atts = atts.copy()
            d_atts['id']=str(nd)+'A';d_atts['role']=role;d_atts['ref_node']=nd
            G.add_node(G.number_of_nodes()+1,d_atts)
            #G.add_node(G.number_of_nodes()+1,{'id':str(nd)+'A','role':role,'capacity':G.node[nd]['capacity'],'ref_nds':nd})
        else:
            atts['role']=transfer;
            atts['ref_node']=nd
            G.add_node(G.number_of_nodes()+1,atts)
        #new origin node
        if role == supply:
            s_atts = atts.copy()
            s_atts['id']=str(nd)+'B';s_atts['role']=role;s_atts['ref_node']=nd
            G.add_node(G.number_of_nodes()+1,s_atts)
        else: 
            atts['role']=transfer; atts['ref_node']=nd
            G.add_node(G.number_of_nodes()+1,atts)

        #add connecting edge
        G.add_edge(G.number_of_nodes()-1,G.number_of_nodes(),{'id':nd,flow_capacity:G.node[nd][flow_capacity]})

        #get edges flowing into node
        in_edges = []
        for eg in G.edges():
            if eg[1] == nd:
                in_edges.append(eg)

        #assign edges to new destination       
        for eg in in_edges:
            atts = G.edge[eg[0]][eg[1]]
            atts['ref_node'] = nd
            G.add_edge(eg[0],G.number_of_nodes()-1,atts)
            G.remove_edge(eg[0],eg[1])

        #get edges flowing out of node
        out_edges = G.edges(nd)

        #assign edges to new origin
        for eg in out_edges:
            atts = G.edge[eg[0]][eg[1]]
            atts['ref_node'] = nd
            G.add_edge(G.number_of_nodes(),eg[1],atts)
            G.remove_edge(eg[0],eg[1])
    
    for nd in node_list:
        #remove node
        G.remove_node(nd)

    return G

def revert_topo(G,demand,supply,transfer,flow):
    '''
    Allows a network which has been converted to handle node capacities to be 
    converted back to a standard topological network. Copies attributes across
    and handles attribute conflicts.
    deamnd,supply and transfer: role string name
    flow: flow attribute name
    '''
    i = 0
    node_list = G.nodes()
    number_of_nodes = G.number_of_nodes()
    while i < number_of_nodes:
        #identify the role of the node, override first if secon is supply or demand
        atts = G.node[node_list[i]]
        if G.node[node_list[i+1]]['role'] == supply or G.node[node_list[i+1]]['role'] == demand:
            atts['role'] = G.node[node_list[i+1]]['role']

        #take the highest flow value from the two nodes - therefore we know it will include those flows which finish/start at the node as well as pass through
        if G.node[node_list[i+1]][flow] > atts[flow]:
            atts[flow] = G.node[node_list[i+1]][flow]
            
        #add new node
        G.add_node(G.node[node_list[i]]['ref_node'],atts)
        
        #go through all edges and create new ones - first those leading to the node        
        for eg in G.in_edges(node_list[i]):
            atts = G.edge[eg[0]][eg[1]]
            G.add_edge(eg[0],G.node[node_list[i]]['ref_node'],atts)
            G.remove_edge(eg[0],eg[1])
            
        #those edges going away from the node
        for eg in G.out_edges(node_list[i+1]):
            atts = G.edge[eg[0]][eg[1]]
            G.add_edge(G.node[node_list[i]]['ref_node'],eg[1],atts)
            G.remove_edge(eg[0],eg[1])
            
        #remove connecting edge
        G.remove_edge(node_list[i],node_list[i+1])
        #as nodes handled in pairs, use +2
        i += 2
    
    #remove nodes        
    for nd in node_list:
        G.remove_node(nd)
        
    return G
    
def get_max_flow_values(G,use_node_capacities=True,use_node_demands=False):
    '''
    This runs a ford-fulkerson maximum flow algrothim over the provided network
    and assigns the resulting flows to each edge. The flows for each node are 
    also calcualted and assigned.
    '''
    print G.edges()
    #print G.edges()
    
    
    if use_node_capacities == True:
        G = convert_topo(G)
        
    print G.edges()
    exit()
    
    #check for supply and demand nodes. Needs to be at least one of each.
    #if more than one need to create a super source/sink(demand) nodes.
    G,supply_nodes, demand_nodes, added_nodes, added_edges = check_for_demand_supply_nodes(G)
    
    #get supply node and demand node
    supply_nd,demand_nd = get_check_supply_demand_nodes(G,supply_nodes,demand_nodes,added_nodes)
    
    if use_node_capacities == True and use_node_demands == False:
        #this returns the maximum flow and the flow on each edge by node
        #first check a path is possible - ford-fulkerson would just return 0 otherwise
        path = nx.has_path(G,supply_nd,demand_nd)
        if path == False:
            raise error_classes.GeneralError('No path exists between the supply node (node %s) and the demand node (node %s).' %(supply_nd,demand_nd))

        max_flow, edge_flows = nx.ford_fulkerson(G, supply_nd,demand_nd,'flow_capacity')
        
    elif use_node_capacities == True and use_node_demands == True:
        #returns the flow on each edge given capacities and demands       
        #the sum of the demand needs to equal the sum of the supply (indicated by a negative demand value)
        edge_flows = nx.min_cost_flow(G,'demand','flow_capacity','weight')
    elif use_node_capacities == False and use_node_demands == True:
        #returns the flow on each edge given demands (capacities should be set at 9999999 (a very high number))
        edge_flows = nx.min_cost_flow(G,'demand','flow_capacity','weight')

    #assign flows to nodes and edges
    G = assign_edge_node_flows(G, edge_flows)

    #before running any analysis, need to remove the added nodes and edges - the super source/demand if used
    G = remove_added_nodes_edges(G,added_edges,added_nodes)
    
    node_flow_max, edge_flow_max = get_max_flows(G)
    
    return G, {'max_flow':max_flow,'max_node_flow':node_flow_max,'max_edge_flow':edge_flow_max}

def reset_flow_values(G):
    '''
    Reset the flow values in the network to 0. Allows the recomputation of 
    flows in the network.
    '''
    #reset flow values to zero before calculating new values
    for node in G.nodes(data=True): G.node[node[0]]['flow'] = 0
    for edge in G.edges(data=True): G.edge[edge[0]][edge[1]]['flow'] = 0
    
    return G
    
def set_demand_values(G):
    '''
    '''
    '''
    for node in G.nodes(data=True):
        if G.node[node[0]]['role'] == 'supply':
            G.node[node[0]]['demand'] = 0 - (G.node[node[0]]['flow'])
        elif G.node[node[0]]['role'] == 'demand':
            demand = 0
            for edge in G.in_edges(node[0]):
                demand += G[edge[0]][edge[1]]['flow']
            G.node[node[0]]['demand'] = demand
        else:
            G.node[node[0]]['demand'] = 0
    '''
    #need to sum up the flows through nodes with a 'supply' role
    supply_total = 0
    demand_total = 0
    '''
    for node in G.nodes(data=True):
        if G.node[node[0]]['role'] == 'supply':
            supply_total = supply_total + G.node[node[0]]['flow']
            G.node[node[0]]['demand'] = 0
        elif G.node[node[0]]['role'] == 'demand':
            print node
            for edge in G.in_edges(node[0]):
                print G[edge[0]][edge[1]]
                #print G[edge[0]][edge[1]]['flow']
                #print G[edge[0]][edge[1]]
                demand_total += G[edge[0]][edge[1]]['flow']
            G.node[node[0]]['demand'] = 0
        elif node[0] == 'sdemand':
            print node
            demand_total += G.node[node[0]]['demand']
        else:
            G.node[node[0]]['demand'] = 0
    '''
    print '-------------------------------------------'
    print 'Supply nodes'
    for node in G.nodes(data=True):
        if G.node[node[0]]['role'] == 'supply':
            print node
            supply_total = supply_total + G.node[node[0]]['flow']
            G.node[node[0]]['demand'] = 0
        elif node[0] == 'ssupply':
            print node
            supply_total += G.node[node[0]]['flow']
            
    print '-------------------------------------------'
    print 'Demand nodes'
    for node in G.nodes(data=True):
        print node
        if G.node[node[0]]['role'] == 'demand':
            #print node
            for edge in G.in_edges(node[0]):
                demand_total += G[edge[0]][edge[1]]['flow']
            G.node[node[0]]['demand'] = 0
        elif node[0] == 'sdemand':
            #print node
            demand_total += G.node[node[0]]['demand']
    exit()
    print '-------------------------------------------'                
    if demand_total != supply_total:
        print 'Totals do not match'
        print 'Demand total:',demand_total
        print 'Supply total:',supply_total
        #I think the current error is caused by flows not being assigned to the supper demand node
        #link edges, and instead stopping at the individual demand nodes.
        #Need to check demads are being assigned correctly to the supper demand node
        #from the original demand nodes - this may also be causing the problem
        
        #Also to do is to test for a single supply to single demand
        #Also to do is to test for a single supply to multiple demand
        exit()
    try:
        G.node['ssupply']['demand'] = 0 - supply_total
    except:
        for node in G.nodes(data=True):
            if G.node[node[0]]['role'] == 'supply':
                G.node[node[0]]['demand'] = 0 - supply_total
                break
    try:
        G.node['sdemand']['demand'] = demand_total
        print 'ran this line'
    except:
        for node in G.nodes(data=True):
            if G.node[node[0]]['role'] == 'demand':
                G.node[node[0]]['demand'] = demand_total

    return G
    
def set_capacity_values(G,multiplier,default_value,capacity):
    '''
    '''
    for edge in G.edges(data=True):
        if G[edge[0]][edge[1]]['flow'] != 0:
            G[edge[0]][edge[1]][capacity] = G[edge[0]][edge[1]]['flow'] * multiplier
        else: G[edge[0]][edge[1]][capacity] = default_value

    for node in G.nodes(data=True):
        if G.node[node[0]]['flow'] != 0:
             G.node[node[0]][capacity] = G.node[node[0]]['flow'] * multiplier
        else: G.node[node[0]][capacity] = default_value
    return G
    
def set_random_capacities(G,a,b,capacity):
    '''
    '''
    import random    
    for edge in G.edges(): G[edge[0]][edge[1]][capacity] = random.randint(a,b)
    for node in G.nodes(): G.node[node][capacity] = random.randint(a,b)
    
    return G
    
def check_over_capacity(G):
    '''
    '''
    edges_over = []
    nodes_over = []
    #print '-------;;;;;--------'
    for edge in G.edges():
        if G[edge[0]][edge[1]]['flow'] > G[edge[0]][edge[1]]['flow_capacity']:
            #print type(G[edge[0]][edge[1]]['flow']),G[edge[0]][edge[1]]['flow']
            #print type(G[edge[0]][edge[1]]['flow_capacity']),G[edge[0]][edge[1]]['flow_capacity']
            #print 'adding to list:',G[edge[0]][edge[1]]['flow'],G[edge[0]][edge[1]]['flow_capacity']
            edges_over.append(edge)
        '''
        if G[edge[0]][edge[1]]['flow'] < G[edge[0]][edge[1]]['flow_capacity']+0.1:
            print 'doing nothing:',G[edge[0]][edge[1]]['flow'],G[edge[0]][edge[1]]['flow_capacity']    
            pass
        elif G[edge[0]][edge[1]]['flow'] == G[edge[0]][edge[1]]['flow_capacity']+0.1:
            print 'doing nothing:',G[edge[0]][edge[1]]['flow'],G[edge[0]][edge[1]]['flow']
            pass
        elif G[edge[0]][edge[1]]['flow'] > G[edge[0]][edge[1]]['flow_capacity']:
            print 'adding to list:',G[edge[0]][edge[1]]['flow'],G[edge[0]][edge[1]]['flow']
            edges_over.append(edge)
        '''
    for node in G.nodes():
        if G.node[node]['flow'] > G.node[node]['flow']:
            nodes_over.append(node)
    #print '-------;;;;;--------'
    return edges_over,nodes_over
    
    
def network_simplex(G, demand = 'demand', capacity = 'flow_capacity',
                    weight = 'weight'):
    """Find a minimum cost flow satisfying all demands in digraph G.
    
    This is a primal network simplex algorithm that uses the leaving
    arc rule to prevent cycling.

    G is a digraph with edge costs and capacities and in which nodes
    have demand, i.e., they want to send or receive some amount of
    flow. A negative demand means that the node wants to send flow, a
    positive demand means that the node want to receive flow. A flow on
    the digraph G satisfies all demand if the net flow into each node
    is equal to the demand of that node.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    demand: string
        Nodes of the graph G are expected to have an attribute demand
        that indicates how much flow a node wants to send (negative
        demand) or receive (positive demand). Note that the sum of the
        demands should be 0 otherwise the problem in not feasible. If
        this attribute is not present, a node is considered to have 0
        demand. Default value: 'demand'.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    Returns
    -------
    flowCost: integer, float
        Cost of a minimum cost flow satisfying all demands.

    flowDict: dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

    Raises
    ------
    NetworkXError
        This exception is raised if the input graph is not directed,
        not connected or is a multigraph.

    NetworkXUnfeasible
        This exception is raised in the following situations:
            * The sum of the demands is not zero. Then, there is no
              flow satisfying all demands.
            * There is no flow satisfying all demand.

    NetworkXUnbounded
        This exception is raised if the digraph G has a cycle of
        negative cost and infinite capacity. Then, the cost of a flow
        satisfying all demands is unbounded below.

    Notes
    -----
    This algorithm is not guaranteed to work if edge weights
    are floating point numbers (overflows and roundoff errors can 
    cause problems). 
        
    See also
    --------
    cost_of_flow, max_flow_min_cost, min_cost_flow, min_cost_flow_cost
               
    Examples
    --------
    A simple example of a min cost flow problem.

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_node('a', demand = -5)
    >>> G.add_node('d', demand = 5)
    >>> G.add_edge('a', 'b', weight = 3, capacity = 4)
    >>> G.add_edge('a', 'c', weight = 6, capacity = 10)
    >>> G.add_edge('b', 'd', weight = 1, capacity = 9)
    >>> G.add_edge('c', 'd', weight = 2, capacity = 5)
    >>> flowCost, flowDict = nx.network_simplex(G)
    >>> flowCost
    24
    >>> flowDict # doctest: +SKIP
    {'a': {'c': 1, 'b': 4}, 'c': {'d': 1}, 'b': {'d': 4}, 'd': {}}

    The mincost flow algorithm can also be used to solve shortest path
    problems. To find the shortest path between two nodes u and v,
    give all edges an infinite capacity, give node u a demand of -1 and
    node v a demand a 1. Then run the network simplex. The value of a
    min cost flow will be the distance between u and v and edges
    carrying positive flow will indicate the path.

    >>> G=nx.DiGraph()
    >>> G.add_weighted_edges_from([('s','u',10), ('s','x',5), 
    ...                            ('u','v',1), ('u','x',2), 
    ...                            ('v','y',1), ('x','u',3), 
    ...                            ('x','v',5), ('x','y',2), 
    ...                            ('y','s',7), ('y','v',6)])
    >>> G.add_node('s', demand = -1)
    >>> G.add_node('v', demand = 1)
    >>> flowCost, flowDict = nx.network_simplex(G)
    >>> flowCost == nx.shortest_path_length(G, 's', 'v', weight = 'weight')
    True
    >>> [(u, v) for u in flowDict for v in flowDict[u] if flowDict[u][v] > 0]
    [('x', 'u'), ('s', 'x'), ('u', 'v')]
    >>> nx.shortest_path(G, 's', 'v', weight = 'weight')
    ['s', 'x', 'u', 'v']

    It is possible to change the name of the attributes used for the
    algorithm.

    >>> G = nx.DiGraph()
    >>> G.add_node('p', spam = -4)
    >>> G.add_node('q', spam = 2)
    >>> G.add_node('a', spam = -2)
    >>> G.add_node('d', spam = -1)
    >>> G.add_node('t', spam = 2)
    >>> G.add_node('w', spam = 3)
    >>> G.add_edge('p', 'q', cost = 7, vacancies = 5)
    >>> G.add_edge('p', 'a', cost = 1, vacancies = 4)
    >>> G.add_edge('q', 'd', cost = 2, vacancies = 3)
    >>> G.add_edge('t', 'q', cost = 1, vacancies = 2)
    >>> G.add_edge('a', 't', cost = 2, vacancies = 4)
    >>> G.add_edge('d', 'w', cost = 3, vacancies = 4)
    >>> G.add_edge('t', 'w', cost = 4, vacancies = 1)
    >>> flowCost, flowDict = nx.network_simplex(G, demand = 'spam',
    ...                                         capacity = 'vacancies',
    ...                                         weight = 'cost')
    >>> flowCost
    37
    >>> flowDict  # doctest: +SKIP
    {'a': {'t': 4}, 'd': {'w': 2}, 'q': {'d': 1}, 'p': {'q': 2, 'a': 2}, 't': {'q': 1, 'w': 1}, 'w': {}}

    References
    ----------
    W. J. Cook, W. H. Cunningham, W. R. Pulleyblank and A. Schrijver.
    Combinatorial Optimization. Wiley-Interscience, 1998.

    """
    sys.path.append('C:/Python27/Lib/site-packages/networkx/algorithms/flow')
    import mincost    
    
    if not G.is_directed():
        raise nx.NetworkXError("Undirected graph not supported.")
    if not nx.is_connected(G.to_undirected()):
        raise nx.NetworkXError("Not connected graph not supported.")
    if G.is_multigraph():
        raise nx.NetworkXError("MultiDiGraph not supported.")
    demand_sum = sum(d[demand] for v, d in G.nodes(data = True))
    #if demand in d) != 0:
    if demand_sum != 0:
        raise nx.NetworkXUnfeasible("Sum of the demands should be 0 (%s)." %demand_sum)

    # Fix an arbitrarily chosen root node and find an initial tree solution.
    H, T, y, artificialEdges, flowCost, r = \
            mincost._initial_tree_solution(G, demand = demand, capacity = capacity,
                                   weight = weight)

    # Initialize the reduced costs.
    c = {}
    for u, v, d in H.edges_iter(data = True):
        c[(u, v)] = d.get(weight, 0) + y[u] - y[v]

    # Main loop.
    while True:
        newEdge = mincost._find_entering_edge(H, c, capacity = capacity)
        if not newEdge:
            break # Optimal basis found. Main loop is over.
        cycleCost = abs(c[newEdge])

        # Find the cycle created by adding newEdge to T.
        path1 = nx.shortest_path(T.to_undirected(), r, newEdge[0])
        path2 = nx.shortest_path(T.to_undirected(), r, newEdge[1])
        join = r
        for index, node in enumerate(path1[1:]):
            if index + 1 < len(path2) and node == path2[index + 1]:
                join = node
            else:
                break
        path1 = path1[path1.index(join):]
        path2 = path2[path2.index(join):]
        cycle = []
        if H[newEdge[0]][newEdge[1]].get('flow', 0) == 0:
            path2.reverse()
            cycle = path1 + path2
        else: # newEdge is at capacity
            path1.reverse()
            cycle = path2 + path1

        # Find the leaving edge. Will stop here if cycle is an infinite
        # capacity negative cost cycle.
        leavingEdge, eps = mincost._find_leaving_edge(H, T, cycle, newEdge,
                                              capacity = capacity)

        # Actual augmentation happens here. If eps = 0, don't bother.
        if eps:
            flowCost -= cycleCost * eps
            if len(cycle) == 3:
                u, v = newEdge
                H[u][v]['flow'] -= eps
                H[v][u]['flow'] -= eps
            else:
                for index, u in enumerate(cycle[:-1]):
                    v = cycle[index + 1]
                    if (u, v) in T.edges() + [newEdge]:
                        H[u][v]['flow'] = H[u][v].get('flow', 0) + eps
                    else: # (v, u) in T.edges():
                        H[v][u]['flow'] -= eps

        # Update tree solution.
        T.add_edge(*newEdge)
        T.remove_edge(*leavingEdge)

        # Update distances and reduced costs.
        if newEdge != leavingEdge:
            forest = nx.DiGraph(T)
            forest.remove_edge(*newEdge)
            R, notR = nx.connected_component_subgraphs(forest.to_undirected())
            if r in notR.nodes(): # make sure r is in R
                R, notR = notR, R
            if newEdge[0] in R.nodes():
                for v in notR.nodes():
                    y[v] += c[newEdge]
            else:
                for v in notR.nodes():
                    y[v] -= c[newEdge]
            for u, v in H.edges():
                if u in notR.nodes() or v in notR.nodes():
                    c[(u, v)] = H[u][v].get(weight, 0) + y[u] - y[v]

    # If an artificial edge has positive flow, the initial problem was
    # not feasible.
    '''
    for u, v in artificialEdges:
        if H[u][v]['flow'] != 0:
            raise nx.NetworkXUnfeasible("No flow satisfying all demands.")
        H.remove_edge(u, v)
    '''
    over_edges = []
    for u, v in artificialEdges:
        if H[u][v]['flow'] != 0:
            over_edges.append((u,v,H[u][v]))
        H.remove_edge(u,v)            
            
    for u in H.nodes():
        if not u in G:
            H.remove_node(u)

    flowDict = mincost._create_flow_dict(G, H)

    return flowCost, flowDict, over_edges