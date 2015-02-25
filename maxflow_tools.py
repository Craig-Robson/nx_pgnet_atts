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
    G.add_node('ssupply',{'role':'super_suply','ref_nds':supply_nodes})
    added_nodes['supply'].append('ssupply')
    for nd in supply_nodes:
        cap_sum = 0
        for eg in G.out_edges(nd):
            cap_sum += G.edge[eg[0]][eg[1]]['capacity']
        G.add_edge('ssupply',nd,{'capacity':cap_sum})
        added_edges['supply'].append(('ssupply',nd))
    
    #sum capacity of edges out of super supply node to get capacity
    cap_sum = 0
    for eg in G.out_edges('ssupply'):
        cap_sum += G.edge[eg[0]][eg[1]]['capacity']
    G.node['ssupply']['capacity'] = cap_sum
    return G,added_edges,added_nodes

def create_superdemand_node(G,demand_nodes,added_edges,added_nodes):
    '''
    Create a super demand node and link it to the individual deamnd nodes,
    setting capacities as required.
    '''
    G.add_node('sdemand',{'role':'super_demand','ref_nds':demand_nodes})
    added_nodes['demand'].append('sdemand')
    for nd in demand_nodes:
        cap_sum = 0
        for eg in G.in_edges(nd):
            cap_sum += G.edge[eg[0]][eg[1]]['capacity']
        G.add_edge(nd,'sdemand',{'capacity':cap_sum})    
        added_edges['demand'].append((nd,'sdemand'))

    #sum capacity of edges into super demand node to get capacity
    cap_sum = 0
    for eg in G.in_edges('sdemand'):
        cap_sum += G.edge[eg[0]][eg[1]]['capacity']
    G.node['sdemand']['capacity'] = cap_sum
    
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
    
def get_max_flows(G):
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
        if edge_flows[eg] > edge_flow_max['flow']:
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

def convert_topo(G):
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
        if role == 'demand':
            d_atts = atts.copy()
            d_atts['id']=str(nd)+'A';d_atts['role']=role;d_atts['ref_nds']=nd
            G.add_node(G.number_of_nodes()+1,d_atts)
            #G.add_node(G.number_of_nodes()+1,{'id':str(nd)+'A','role':role,'capacity':G.node[nd]['capacity'],'ref_nds':nd})
        else:
            atts['role']='transfer';atts['ref_nds']=nd
            G.add_node(G.number_of_nodes()+1,atts)
        #new origin node
        if role == 'supply':
            s_atts = atts.copy()
            s_atts['id']=str(nd)+'B';s_atts['role']=role;s_atts['ref_nds']=nd
            G.add_node(G.number_of_nodes()+1,s_atts)
        else: 
            atts['role']='transfer';atts['ref_nds']=nd
            G.add_node(G.number_of_nodes()+1,atts)

        #add connecting edge
        G.add_edge(G.number_of_nodes()-1,G.number_of_nodes(),{'id':nd,'capacity':G.node[nd]['capacity']})

        #get edges flowing into node
        in_edges = []
        for eg in G.edges():
            if eg[1] == nd:
                in_edges.append(eg)

        #assign edges to new destination       
        for eg in in_edges:
            atts = G.edge[eg[0]][eg[1]]
            atts['ref_nds'] = nd
            G.add_edge(eg[0],G.number_of_nodes()-1,atts)
            G.remove_edge(eg[0],eg[1])

        #get edges flowing out of node
        out_edges = G.edges(nd)

        #assign edges to new origin
        for eg in out_edges:
            atts = G.edge[eg[0]][eg[1]]
            atts['ref_nds'] = nd
            G.add_edge(G.number_of_nodes(),eg[1],atts)
            G.remove_edge(eg[0],eg[1])
    
    for nd in node_list:
        #remove node
        G.remove_node(nd)

    return G

def revert_topo(G):
    '''
    Allows a network which has been converted to handle node capacities to be 
    converted back to a standard topological network. Copies attributes across
    and handles attribute conflicts (well should do!).
    '''
    i = 0
    node_list = G.nodes()
    number_of_nodes = G.number_of_nodes()
    while i < number_of_nodes:
        #identify the role of the node, override first if secon is supply or demand
        atts = G.node[node_list[i]]
        if G.node[node_list[i+1]]['role'] == 'supply' or G.node[node_list[i+1]]['role'] == 'demand':
            atts['role'] = G.node[node_list[i+1]]['role']
        #take the highest flow value from the two nodes - therefore we know it will include those flows which finish/start at the node as well as pass through
        if G.node[node_list[i+1]]['flow'] > atts['flow']:
            atts['flow'] = G.node[node_list[i+1]]['flow']
            
        #add new node
        G.add_node(G.node[node_list[i]]['ref_nds'],atts)
        
        #go through all edges and create new ones - first those leading to the node        
        for eg in G.in_edges(node_list[i]):
            atts = G.edge[eg[0]][eg[1]]
            G.add_edge(eg[0],G.node[node_list[i]]['ref_nds'],atts)
            G.remove_edge(eg[0],eg[1])
        #those edges going away from the node
        for eg in G.out_edges(node_list[i+1]):
            atts = G.edge[eg[0]][eg[1]]
            G.add_edge(G.node[node_list[i]]['ref_nds'],eg[1],atts)
            G.remove_edge(eg[0],eg[1])
            
        #remove connecting edge
        G.remove_edge(node_list[i],node_list[i+1])
        #as nodes handled in pairs, use +2
        i += 2
    
    #remove nodes        
    for nd in node_list:
        G.remove_node(nd)
        
    return G
    
def get_max_flow_values(G,use_node_capacities=True):
    '''
    This runs a ford-fulkerson maximum flow algrothim over the provided network
    and assigns the resulting flows to each edge. The flowws for each node are 
    also calcualted and assigned.
    '''
    
    if use_node_capacities == True:
        G = convert_topo(G)
    
    #check for supply and demand nodes. Needs to be at least one of each.
    #if more than one need to create a super source/sink(demand) nodes.
    G,supply_nodes, demand_nodes, added_nodes, added_edges = check_for_demand_supply_nodes(G)
    
    #get supply node and demand node
    supply_nd,demand_nd = get_check_supply_demand_nodes(G,supply_nodes,demand_nodes,added_nodes)
    
    #this returns the maximum flow and the flow on each edge by node
    max_flow, edge_flows = nx.ford_fulkerson(G, supply_nd,demand_nd,'capacity')

    #assign flows to nodes and edges
    G = assign_edge_node_flows(G, edge_flows)

    #before running any analysis, need to remove the added nodes and edges - the super source/demand if used
    G = remove_added_nodes_edges(G,added_edges,added_nodes)
    
    node_flow_max, edge_flow_max = get_max_flows(G)
    
    return G, {'max_flow':max_flow,'max_node_flow':node_flow_max,'max_edge_flow':edge_flow_max}
