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
sys.path.append('C:/a8243587_DATA/work_package_two')
import nx_pgnet_attribute_addon as nx_pgnet_av

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
        print "Need to create a supper supply node as %s supply nodes found."
        G,added_edges,added_nodes = create_supersupply_node(G, supply_nodes,added_edges,added_nodes)
        
    if len(demand_nodes) == 0:
        print "Error. No demand nodes nominated."
        exit()
    elif len(demand_nodes) > 1:
        print "Need to create a supper demand node as %s demand nodes found."
        G,added_edges,added_nodes = create_superdemand_node(G,supply_nodes,added_edges,added_nodes)
    
    return G,supply_nodes, demand_nodes, added_nodes, added_edges 

def get_check_supply_demand_nodes(G,supply_node,demand_node):
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

def replace_nodes(G):
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
        #print G.node[nd].keys()
        #exit()
        #new dest node
        if role == 'demand': G.add_node(G.number_of_nodes()+1,{'id':str(nd)+'A','role':role,'capacity':G.node[nd]['capacity'],'ref_nds':nd})
        else: G.add_node(G.number_of_nodes()+1,{'role':'transfer','ref_nds':nd})
        #new origin node
        if role == 'supply': G.add_node(G.number_of_nodes()+1,{'id':str(nd)+'B','role':role,'capacity':G.node[nd]['capacity'],'ref_nds':nd})
        else: G.add_node(G.number_of_nodes()+1,{'role':'transfer','ref_nds':nd})

        #add connecting edge
        G.add_edge(G.number_of_nodes()-1,G.number_of_nodes(),{'id':nd,'capacity':G.node[nd]['capacity']})

        #get edges flowing into node
        in_edges = []
        for eg in G.edges():
            if eg[1] == nd:
                in_edges.append(eg)

        #assign edges to new destination       
        for eg in in_edges:
            G.add_edge(eg[0],G.number_of_nodes()-1,{'capacity':G.edge[eg[0]][eg[1]]['capacity'],'ref_nds':nd})
            G.remove_edge(eg[0],eg[1])

        #get edges flowing out of node
        out_edges = G.edges(nd)

        #assign edges to new origin
        for eg in out_edges:
            G.add_edge(G.number_of_nodes(),eg[1],{'capacity':G.edge[eg[0]][eg[1]]['capacity'],'ref_nds':nd})
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
        role = G.node[node_list[i]]['role']
        if G.node[node_list[i+1]]['role'] == 'supply' or G.node[node_list[i+1]]['role'] == 'demand':
            role = G.node[node_list[i+1]]['role']
        
        #add new node
        G.add_node(G.node[node_list[i]]['ref_nds'],{'flow':G.node[node_list[i]]['flow'],'role':role,'capacity':G.edge[node_list[i]][node_list[i+1]]['capacity']})

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
    
conn = ogr.Open("PG:dbname='_new_schema_SB' host='localhost'port='5433' user='postgres' password='aaSD2011'")
name = 'sample'
attributes = [{'flow':False, 'capacity':True, 'storage':False, 'resistance':False, 'latency':False},{'flow':False, 'capacity':True, 'length':False, 'resistance':False, 'stacking':False}]
G = nx_pgnet_av.read(conn,name).read_from_db(attributes)

G = replace_nodes(G)

#check for supply and demand nodes. Needs to be at least one of each.
#if more than one need to create a super source/sink(demand) nodes.
G,supply_nodes, demand_nodes, added_nodes, added_edges = check_for_demand_supply_nodes(G)

#this line may not be needed as above returns possible solution
supply_nd,demand_nd = get_check_supply_demand_nodes(G,supply_nodes,demand_nodes)

#this returns the maximum flow and the flow on each edge by node
result = nx.ford_fulkerson(G, supply_nd,demand_nd,'capacity')
print "Ford fulkerson max flow:",result[0]
#print "Ford fulkerson edge flows:",result[1]
print '----------------------'

#assign flows to nodes and edges
G = assign_edge_node_flows(G, result[1])

#before running any analysis, need to remove the added nodes and edges
G = remove_added_nodes_edges(G,added_edges,added_nodes)

#find flow in nodes and edges
edge_flows, node_flows = get_flow_stats(G)

print "Node flow values:", node_flows
print "Edge flow values:",edge_flows

#get edge and node with max flow
node_flow_max, edge_flow_max = get_max_flows(G)

print "Node with greatest flow:",node_flow_max        
print "Edge with greatest flow:",edge_flow_max

#this allows a network to be converted back to original format
G = revert_topo(G) 

print G.node[2]
print G.edge[3][5]
"""
print 'Ref nodes (NewID, OriginalID):'
for nd in G.nodes():
    print nd,',',G.node[nd]['ref_nds']
"""

#can then run a cascading failure model over the network where flows are not rerouted

#model methods to be confirmed - read lit to find the best option
#can use topology based methods, or a flow based method
