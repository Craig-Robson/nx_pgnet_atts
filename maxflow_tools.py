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

print_test_outputs = False

import networkx as nx
import random as r
import sys, ogr
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet')
import nx_pg
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet_atts')
sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet_atts')
import nx_pgnet_atts as nx_pgnet_atts
import error_classes


class topological_changes:
    '''
    Contains all functions for changing of the topology.
    '''
    
    def __init__(self,G):
        if G == None:
            exit()
        else:
            self.G = G
    
    def remove_added_nodes_edges(self,added_edges,added_nodes):
        '''
        Remove added nodes, ie. the super demand and super supply nodes.
        '''
        
        for ky in added_edges.keys():
            for eg in added_edges[ky]:
                self.G.remove_edge(eg[0],eg[1])
            for nd in added_nodes[ky]:
                self.G.remove_node(nd)
        return self.G
    
    def remove_super_nodes(self,supply_nodes,demand_nodes):
        '''
        Remove the super nodes from the network.
        '''
        G = self.G 
        for node in G.nodes():
            if node == 'ssupply':
                G.remove_node(node)
            elif node == 'sdemand':
                G.remove_node(node)
            elif G.node[node]['role'] == 'super_supply_supply':
                pass
            elif G.node[node]['role'] == 'super_supply_demand':
                pass
        return G
    
    def remove_node(self, node_to_remove):
        '''
        This is to specificaly handle the removal of a node from the network.
        '''
                
        '''
        print '----------------------------------------------------------------------'
        print 'Node asked to be removed:', node_to_remove
        print 'Node details:', G.node[node_to_remove]
        print '----------------------------------------------------------------------'
        '''
        self.G.remove_node(node_to_remove)    
    
        return self.G
    
    def create_superdemand_node(self,demand_nodes,added_edges,added_nodes):
        '''
        Create a super demand node and link it to the individual deamnd nodes,
        setting capacities as required.
        '''
        G = self.G
        
        G.add_node('sdemand',{'role':'super_demand','ref_nodes':demand_nodes})
        added_nodes['demand'].append('sdemand')
        #print demand_nodes
        for nd in demand_nodes:
            cap_sum = 0
            #print 'Edges in to nd:',G.in_edges(nd)
            for eg in G.in_edges(nd):
                #print eg[0],',',eg[1],';' ,G.edge[eg[0]][eg[1]]
                cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
            #print 'Adding edge:', nd,'sdemand'
            G.add_edge(nd,'sdemand',{'flow_capacity':cap_sum})    
            added_edges['demand'].append((nd,'sdemand'))
    
        #sum capacity of edges into super demand node to get capacity
        cap_sum = 0
        for eg in G.in_edges('sdemand'):
            cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
        G.node['sdemand']['flow_capacity'] = cap_sum
       
        return G,added_edges,added_nodes    
    
    
    def create_supersupply_node(self,supply_nodes,added_edges,added_nodes):
        '''
        Create a super supply node and link it to the individual supply nodes,
        setting capacities as required.
        '''
        
        # add super supply node
        self.G.add_node('ssupply',{'role':'super_supply','ref_nodes':supply_nodes})
        added_nodes['supply'].append('ssupply')
        
        # loop through list os supply nodes
        for nd in supply_nodes:
            '''
            cap_sum = 0
            # loop through all edges from supply node and sum capacity
            for eg in G.out_edges(nd):
                cap_sum += G.edge[eg[0]][eg[1]]['flow_capacity']
            ''' 
            # add edge to supply node from super supply with capacity of edges from supply node
            #G.add_edge('ssupply',nd,{'flow_capacity':cap_sum})
            self.G.add_edge('ssupply',nd,{'flow_capacity':self.G.node[nd]['flow_capacity']})
            added_edges['supply'].append(('ssupply',nd))
        
        #sum capacity of edges out of super supply node to get capacity
        cap_sum = 0
        for eg in self.G.out_edges('ssupply'):
            cap_sum += self.G.edge[eg[0]][eg[1]]['flow_capacity']
        self.G.node['ssupply']['flow_capacity'] = cap_sum
        
        return self.G,added_edges,added_nodes
        
    def check_for_demand_supply_nodes(self):
        '''
        Finds all nodes with a role set as demand or supply. Creates a super node 
        where required adn returns a warning if there are no nodes with either role.
        '''
        
        supply_nodes, demand_nodes = get(self.G).get_demand_supply_nodes()
        added_edges = {'supply':[],'demand':[]}  
        added_nodes = {'supply':[],'demand':[]}
        if len(supply_nodes) == 0:
            print "Error. No supply nodes nominated."
            exit()
        elif len(supply_nodes) > 1:
            #if more than one supply node create a super node with teh edge capacity being equal to teh capacity of the supply node
            #print "Need to create a super supply node as %s supply nodes found." %(len(supply_nodes))
            self.G,added_edges,added_nodes = self.create_supersupply_node(supply_nodes,added_edges,added_nodes)
            
        if len(demand_nodes) == 0:
            print "Error. No demand nodes nominated."
            exit()
        # i don't think we need super demand nodes so this is now not needed
        #elif len(demand_nodes) > 1:
        #    print "Need to create a super demand node as %s demand nodes found." %(len(demand_nodes))
        #    G,added_edges,added_nodes = create_superdemand_node(G,demand_nodes,added_edges,added_nodes)
        
        return self.G,supply_nodes, demand_nodes, added_nodes, added_edges     
    
    def convert_topo(self,demand = 'demand',supply = 'supply',transfer = 'intermediate',flow_capacity = 'flow_capacity'):
        '''
        Converts a network to a format where node capacities can be used in 
        standard flow algorithms. Replaces a node with two nodes, each with a 
        suffix, either A(inflow) or B (outflow), and adds a connecting edge which
        has the attributs of the replaced node. Edges affected are reconnected to 
        the repsective new node. This can be reverted using the revert_topo function.
        'demand','supply','intermediate','flow_capacity'
        '''
        
        G = self.G
        node_list = G.nodes()
        supply_nodes = []
        demand_nodes = []
        super_supply_node = False
        super_demand_node = False
        
        for nd in node_list:
            
            #add two nodes
            role = G.node[nd]['role']
            atts = G.node[nd]
            
            if nd == 'ssupply':
                # if the node is a super supply node
                d_atts = atts.copy()
                d_atts['role'] = role + '_demand'
                d_atts['ref_node'] = nd
                d_atts['flow'] = 0
                G.add_node(G.number_of_nodes()+1,d_atts)
                
                #add a second node
                s_atts = atts.copy()
                s_atts['role'] = role + '_supply'
                s_atts['ref_node'] = nd
                G.add_node(G.number_of_nodes()+1,s_atts)
                super_supply_node = G.number_of_nodes()
                
            elif nd == 'sdemand':
                # if the node is a super demand node
                d_atts = atts.copy()
                d_atts['role']=role  + '_demand'
                d_atts['ref_node']=nd
                G.add_node(G.number_of_nodes()+1,d_atts)         
                
                #add second node
                s_atts = atts.copy()
                s_atts['role']=role+'_supply'
                s_atts['ref_node']=nd
                G.add_node(G.number_of_nodes()+1,s_atts)
                super_demand_node = G.number_of_nodes()-1
                
            else:
                #new dest node
                if role == demand:
                    # if a demand node
                    d_atts = atts.copy()
                    d_atts['role']=role;d_atts['ref_node']=nd
                    G.add_node(G.number_of_nodes()+1,d_atts)
                    demand_nodes.append(G.number_of_nodes())
                    
                elif role == 'super_demand':
                    # if a super demand node
                    d_atts = atts.copy()
                    d_atts['role']=role
                    d_atts['ref_node']=nd
                    G.add_node(G.number_of_nodes()+1,d_atts)
                    demand_nodes = G.number_of_nodes()
                else:
                    #print 'Adding node', G.number_of_nodes()+1
                    s_atts = atts.copy()
                    s_atts['role'] = transfer
                    s_atts['ref_node'] = nd
                    G.add_node(G.number_of_nodes()+1,s_atts)
                
                #new origin node
                if role == supply:
                    # if a supply node
                    s_atts = atts.copy()
                    s_atts['role']=role;s_atts['ref_node']=nd
                    G.add_node(G.number_of_nodes()+1,s_atts)
                    supply_nodes.append(G.number_of_nodes())
                    
                    
                elif role == 'super_supply':
                    # if a super supply node
                    s_atts = atts.copy()
                    s_atts['role']=role
                    s_atts['ref_node']=nd
                    G.add_node(G.number_of_nodes()+1,s_atts)
                    supply_nodes = G.number_of_nodes()
                    
                else: 
                    #print 'Adding node', G.number_of_nodes()+1
                    s_atts = atts.copy()
                    s_atts['role']=transfer; 
                    s_atts['ref_node']=nd
                    G.add_node(G.number_of_nodes()+1,s_atts)
                
            #add connecting edge
            G.add_edge(G.number_of_nodes()-1,G.number_of_nodes(),{'id':nd,flow_capacity:G.node[nd][flow_capacity],'role':'transfer'})
    
            # find a way under ref_node tag to label but ref node original values - may make debugging easier
            
            #get edges flowing into node
            in_edges = []
            for eg in G.edges():
                if eg[1] == nd:
                    in_edges.append(eg)
    
            #assign edges to new destination       
            for eg in in_edges:
                atts = G.edge[eg[0]][eg[1]]
                atts['ref_node'] = nd
                atts['role'] = 'network_edge'
                #print 'Edge added:', eg[0], G.number_of_nodes()-1, '; Replaced:', eg[0],eg[1]
                G.add_edge(eg[0],G.number_of_nodes()-1,atts)
                G.remove_edge(eg[0],eg[1])
    
            #get edges flowing out of node
            out_edges = G.edges(nd)
    
            #assign edges to new origin
            for eg in out_edges:
                atts = G.edge[eg[0]][eg[1]]
                atts['ref_node'] = nd
                #print 'Edge added:', G.number_of_nodes()-1, eg[1]
                G.add_edge(G.number_of_nodes(),eg[1],atts)
                G.remove_edge(eg[0],eg[1])
            
        for nd in node_list:
            #remove node
            G.remove_node(nd)
        #return G, demand_nodes, supply_nodes, super_demand_node, super_supply_node
        return G, supply_nodes, demand_nodes, super_supply_node, super_demand_node
        
    def revert_topo(self,demand = 'demand', supply = 'supply', transfer = 'intermediate', flow = 'flow'):
        '''
        Allows a network which has been converted to handle node capacities to be 
        converted back to a standard topological network. Copies attributes across
        and handles attribute conflicts.
        deamnd,supply and transfer: role string name
        flow: flow attribute name
        '''
        G = self.G
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
        
    def get_trigger_edge(self,edge):
        '''
        Searches the edges of the network to identify the new start and end 
        nodes of the formally decalred trigger edge.
        '''
        start_nd, end_nd = edge        
        
        new_start_nd = False
        new_end_nd = False
        
        for node in self.G.nodes():
            #print self.G.node[node]['ref_node']
            if self.G.node[node]['ref_node'] == start_nd and new_start_nd == False :
                new_start_nd = node + 1 #need to add one here so it uses the supply node rather than the demand
            elif self.G.node[node]['ref_node'] == end_nd and new_end_nd == False:
                new_end_nd = node
        
        if new_start_nd != False and new_end_nd != False:
            edge = new_start_nd, new_end_nd
        else:
            print 'Could not find new edge.'
        
        return edge        


class flow:
    '''
    Contains all functions related to assignment of flows.
    '''

    def __init__(self,G):
        if G == None:
            exit()
        else:
            self.G = G
    
    def assign_edge_node_flows(self, data):
        '''
        Given a dict of flow values from a maximum flow algorithm, such as the 
        ford-fulkerson, assigns edge flows and calculates and assigns node flows.
        '''
        #assign calculated flow to the dges
        for eg in self.G.edges():
            self.G.edge[eg[0]][eg[1]]['flow']=data[eg[0]][eg[1]]
        
        #sums the flows along the edges which leave the node
        for nd in data:
            flowsum = 0
            for val in data[nd]:
                flowsum += data[nd][val]
            self.G.node[nd]['flow'] = flowsum
        
        return self.G
    
    def handle_subgraphs(self,supply_nodes,demand_nodes,super_supply_node,super_demand_node):
        '''
        Deals with issues around the network becoming fragmented and the potential
        issues that arise with supply and demand nodes and demands being met.
        
        NEED TO GO THROUGH THIS CAREFULLY AND IDENTIFY WHAT NEEDS DOING. IT JUST 
        ABOUT WORKS BUT NOT FULLY AS YET. TIME TO SORT THIS ONCE AND FOR ALL!!!!
        '''
        K = self.G
        # what happens when the network becomes disconnected???? (apart from the algorithm breaking!)
        # if a subgraph has no demand points in it can we throw it away?
        # if a subgraph has demand points in it and no supply, model should stop/throw away that subgraph.
        # if a subgraph has demand points and supply, then continue with each subgraph individualy
        
        # if more than one connected component (subgraphs) check demand for demand and supply points and act accordingly
        G = K.copy()
        G = G.to_undirected()
        graphs = nx.connected_component_subgraphs(G)
        
        graph_states2 = []
        graph_supply_demand_nds = []
        # test if supply in a differnet sub-network to demand
        for g in graphs:
            #store the nodes found for the sub graph        
            supply_nd = []; ssupply_nd = []
            demand_nd = []; sdemand_nd = []
            #store if nodes found in the sub graph - pre set as false
            supply_in = False; ssupply_in = False
            demand_in = False; sdemand_in = False
    
            #check if super supply connected to graph if uses a super supply graph        
            
            for nd in g.nodes():
                if super_supply_node != False:
                    if nd == super_supply_node:
                        ssupply_nd.append(nd)
                        ssupply_in = True
                for snd in supply_nodes:
                    if nd == snd:
                        supply_nd.append(nd)
                        supply_in = True
                if super_demand_node != False:
                    if nd == super_demand_node:
                        sdemand_nd.append(nd)
                        sdemand_in = True
                for dnd in demand_nodes:
                    if nd == dnd: 
                        demand_nd.append(nd)
                        demand_in = True
            
            graph_states2.append({'ssupply_in':ssupply_in,'sdemand_in':sdemand_in,'supply_in':supply_in,'demand_in':demand_in})
            graph_supply_demand_nds.append([ssupply_nd,sdemand_nd,supply_nd,demand_nd])
        
        # run a quick assessment of the network - quickly check if anything computable
        routing_possible = False
        for subgraph in graph_states2:
            # if there is a subgraph with a minimum of a single demand and supply node then continue this process
            if subgraph['supply_in'] == True and subgraph['demand_in'] == True:
                routing_possible = True
    
        # no subgraphs with both a supply and demand node so terminate        
        if routing_possible == False:
            return None, demand_nodes
        
        # first check if graph still works - check in subgraph for at least a supply and demand point
        terminate = True
        demand_value = 0
        graph = 0
        
        for lst in graph_states2:
            
            if lst['ssupply_in'] == False and lst['supply_in'] == False:
                # no supply nodes in sub graph
                if lst['sdemand_in'] == False and lst['demand_in'] == False:
                    # no supply or demand nodes - remove sub graph
                    for nde in graphs[graph].nodes():
                        K = topological_changes(K).remove_node(nde)
                else:
                    # no supply nodes in sub graph thus remove but some demand nodes
                    # need to find demand value in sub graph before removing
                    for nd in graphs[graph].nodes():
                        
                        if lst['sdemand_in'] != False:
                            
                            if nd == super_demand_node:
                                #add demand value to demand value
                                demand_value = demand_value + K.node[nd]['demand']
                        else:
                            
                            for dnd in demand_nodes:
                            
                                if nd == dnd:
                                    # need to reduce the supply in the network by this value
                                    if super_supply_node != False:
                                        # reduce the demand value from the super supply node
                                        K.node[super_supply_node]['demand'] += K.node[nd]['demand']
                                    else:
                                        # reduce the demand value for the single supply node
                                        K.node[supply_nodes[0]]['demand'] += K.node[nd]['demand']                                    
                                        
                                    # remove node from list of demand nodes
                                    demand_nodes.remove(dnd)
    
                    for nde in graphs[graph].nodes():
                        K = topological_changes(K).remove_node(nde)
        
            elif lst['sdemand_in'] == False and lst['demand_in'] == False:
                #no demand points in subgraph thus remove
                if lst['ssupply_in'] == False and lst['supply_in'] == False:
                    #no demand or supply nodes - remove sub graph #this is covered above already
                    for nde in graphs[graph].nodes():
                        K = topological_changes(K).remove_node(nde)
                        
                else:
                    # no demand nodes in sub graph thus remove but some supply
                    for nd in graphs[graph].nodes():
                        
                        if nd == super_supply_node:
                            # leave this subgraph in and handle separetly
                            # can only remove this if we know there is one other supply node in the network
                            # this needs thinking about
                            pass
                        
                        for dnd in supply_nodes:
                            if nd == dnd:
                                demand_value = demand_value - K.node[nd]['demand']
                    
                    for nde in graphs[graph].nodes():
                        K = topological_changes(K).remove_node(nde)
                
            else:
                # at least one supply (or supersupply) node and atleast one demand node
                # subgraph might be computable
                # subgraph has at least one of each in - need to check possible to compute still           
                # check sum of demands is still equal in subgraph
                # if not adjust accoridngly; if no demand terminate
                terminate = False
                
                # get total supply and demand in network and the related nodes           
                demand_in_g = 0
                supply_in_g = 0
                supply_n = []
                demand_n = []
                for nd in graphs[graph].nodes():
                    # if a positive demand, node is a demand node
                    if graphs[graph].node[nd]['demand'] > 0:
                        demand_n.append(nd)
                        demand_in_g += graphs[graph].node[nd]['demand']
                    # if a negative demand, node is a supply node
                    elif graphs[graph].node[nd]['demand'] < 0:
                        supply_n.append(nd)
                        supply_in_g += graphs[graph].node[nd]['demand']
                
                # dont need to adjust as supply and demand equal
                if demand_in_g - supply_in_g == 0:
                    pass
                else: 
                    # adjusting the supply and demand values in subgraph
                    
                    # if supply is greater than demand
                    if supply_in_g > demand_in_g:
                        
                        # find the supply nodes
                        #   done above -supply_n
                        
                        # get difference
                        diff = float(demand_in_g) - supply_in_g
                        
                        # get value to reduce
                        diff = diff/len(supply_n)
                        
                        # reduce by calaulted value
                        for nd in supply_n:
                            K.node[nd]['demand'] -= diff
                        
                    # if demand is greater than supply
                    elif demand_in_g < supply_in_g:
                    
                        # network should fail
                        # or should the demand be met by the supply node which will lead to failure anyway!
                        print 'Demand cannot be met in subgraph: This subgraph should be removed.'
            
            graph += 1
       
        # get total supply and demand in network            
        demand_in_g = 0
        supply_in_g = 0
        for nd in K.nodes():
            # if a positive demand, node is a demand node
            if K.node[nd]['demand'] > 0:
                demand_in_g += K.node[nd]['demand']
            # if a negative demand, node is a supply node
            elif K.node[nd]['demand'] < 0:
                supply_in_g += K.node[nd]['demand']
        
        # check supply and demand are in order
        if demand_in_g + supply_in_g != 0:                
            print 'dtotal is not zero:'
            print 'demand in g:', demand_in_g
            print 'supply in g:', supply_in_g
            print 'Nodes in network:'
            for nd in graphs[graph].nodes(data=True): print nd
            exit()                    
    
        # if no subgraph has both supply and demand nodes (super or not)
        if terminate == True:
            K = None
            # terminated as no subgraphs with both supply and demand nodes
            return None, demand_nodes
         
        G = G.to_directed()
        
        # check for supply or demand nodes are actually connected/can be reached
        # this is needed for directed network where though connected, a supply node 
        # may not be able to supply anything
        
        # check each supply node is connected to at least one demand node
        for s_nd in supply_nodes:
            
            for d_nd in demand_nodes:
                # if supply node is connected to 
                supply_path = nx.has_path(K,s_nd,dnd) 
            
            if supply_path == False:
                print 'No path available - remove supply node',s_nd
                # set supply as zero as node now redundant and not connected
                K.node[s_nd]['original_demand'] = K.node[s_nd]['demand']
                K.node[s_nd]['demand'] = 0
        
        for d_nd in demand_nodes:
            node_in = False
            for nd in K.nodes():
                if nd == d_nd: node_in = True
            # if demand node still in network
            # if not should I not remove it from the list of demand nodes......YESSSSSS
            if node_in == True:
                demand_path = False
                for s_nd in supply_nodes:
                    try:
                        nx.shortest_path(K,s_nd,d_nd)
                        demand_path = True
                        break
                    except:
                        pass
                if demand_path == False:
                    # no path availble to demand node
                    # set demand as zero as node now redundant and not connected
                    K.node[d_nd]['original_demand'] = K.node[d_nd]['demand']
                    K.node[d_nd]['demand'] = 0
        
        '''
        # run a final check to see what the supply and demand status is across the network
        print 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'
        for nd in K.nodes():
            if K.node[nd]['demand'] < 0:
                print 'Node %s is a supply node with a demand value is %s' %(nd,K.node[nd]['demand'])
            elif K.node[nd]['demand'] > 0:
                print 'Node %s is a demand node with a demand value is %s' %(nd,K.node[nd]['demand'])
        print 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'    
        '''
        
        return K, demand_nodes    
    
    
    def resolve_edge_flows(self,over_edges,demand_nodes, supply_nodes, super_supply_node,demand_supplied,supply_used):
        '''
        Should be able to combine this into the network simplex function later.
        Optimizes for the availble supply capacity the paths where the un-met
        demands are met.
        '''
        G = self.G
       
        # now need optimise the existing supply capacities for the unmet demands
        # this is simple where only one supply and one demand
        # with multiple supply nodes need to use the one with surplus capacity if possible
        #   if there is no route then use an alternative
        # with have to route from all supplied to all demands to find the least cost 
        # solution where all demands are met
        
        #  pre-processing on the supply nodes
        # calculate the supply value per supply node if a super supply node is used
        
        if print_test_outputs == True: print supply_used
        supply_available = []
        if supply_used[0]!={}: #this first entry is for a supper supply node, after is supply nodes
            demand_per_snode = (supply_used[0]['demand']/(len(supply_used)-1))*-1
        
            for i in range(1,len(supply_used)):
                supply_available.append({'node':supply_used[i]['node'],'available':demand_per_snode-supply_used[i]['flow']})
        else: #is no supper supply node only one supply node
            supply_available.append({'node':supply_used[1]['node'], 'available':(G.node[supply_used[1]['node']]['demand']*-1)-supply_used[1]['flow']})
            
        # print 'Available supply:', supply_available
    
        #  un-met demand - get nodes and the amount of demand un-met
        unmet_demand = []
        for i in range(0,len(demand_supplied)):
            unmet_demand.append({'node':demand_supplied[i]['node'],'unmet':demand_supplied[i]['demand']-demand_supplied[i]['flow']})
         
        # print 'Un-met demand:', unmet_demand
    
        pos_solutions = []
        optimal_solutions = []
    
        # identify those nodes with unmet demands and look for solutions
        for dnd in unmet_demand:
            # if a demand node has an umet demand
            if dnd['unmet'] != 0:
                check_another_source = False
                supply_with_cap = False
                pos_solutions.append({'demand_node':dnd['node'],'options':[],'unmet':dnd['unmet']})
                
                # get path to node from a source with suitable capacity
                for snd in supply_available:
                    
                    if snd['available'] >= dnd['unmet']:
                        supply_with_cap = True
                        
                        # find least cost path between the node pair
                        try:
                            path = nx.shortest_path(G,snd['node'],dnd['node'],'weight')
                        except: # no route possible
                            check_another_source = True
                            path = []
                        
                        # calculate the cost of the path
                        cost = 0.0
                        for nd in range(1, len(path)):
                            try:
                                cost += G[path[nd-1]][path[nd]]['weight']
                            except:
                                #in case no weight field - as with 'node edges'
                                cost += 0.0
                        
                        # if path found
                        if path != []:
                            
                            # populate pos_solutions list with found path                            
                            for i in range(0,len(pos_solutions)):
                                if pos_solutions[i]['demand_node'] == dnd['node']:                            
                                    pos_solutions[i]['options'].append({'supply_node':snd['node'],'path':path,'cost': cost, 'weight': dnd['unmet']})
                
                # if no route possible from a supply node with available
                # capacity check other supply nodes which will cause them to go 
                # over capacity
                if check_another_source == True or supply_with_cap == False:
                    
                    # get path to node from a source
                    for snd in supply_available:
    
                        # find least cost path between the node pair
                        try:
                            path = nx.shortest_path(G,snd['node'],dnd['node'],'weight')
                        except: # no route possible
                            check_another_source = True
                            path = []
    
                        # calculate the cost of the path
                        cost = 0.0
                        for nd in range(1, len(path)):
                            try:
                                cost += G[path[nd-1]][path[nd]]['weight']
                            except:
                                #in case no weight field - as with 'node edges'
                                cost += 0.0
                        
                        # if path found
                        if path != []:
                            
                            # populate pos_solutions list with found path                            
                            for i in range(0,len(pos_solutions)):
                                if pos_solutions[i]['demand_node'] == dnd['node']:                            
                                    pos_solutions[i]['options'].append({'supply_node':snd['node'],'path':path,'cost': cost, 'weight': dnd['unmet']})
        
        
        #print len(pos_solutions), 'possible solution(s) have been found.'
        #print pos_solutions
        for solution in pos_solutions:
            if solution['options'] == []:
                # no options found for demand node
                found_path = False
                for sd in supply_nodes:
                    if nx.has_path(G,sd,solution["demand_node"]) == True:
                        found_path = True
                        break
                if found_path == True:
                    print 'Path exists but no solution found. MAJOR ERROR!'
                else:
                    # demand node not reachable, but connected. Reduce demand to 
                    # zero. This should probably actually be a failure.
                    #print 'Demand node not reachable. It should be removed.'
                    #reduce supply by the demand being removed
                    #print solution["demand_node"]
                    #print super_supply_node
                    
                    # super_supply_node can be False for some reason here. Need to investigate this further
                    if super_supply_node == False:
                        for node in G.nodes(data = True):
                            if node[1]['role_type'] == 'supply':
                                #print node[1]
                                super_supply_node = node[0]
                        print super_supply_node
                        
                    G.node[super_supply_node]['demand'] -= G.node[solution["demand_node"]]['demand']*-1
                    #set demand as zero
                    G.node[solution["demand_node"]]['demand'] = 0
                    
        y = 0
        while y < len(pos_solutions):
            demand_node = pos_solutions[y]
            # if only one solution for each demand node then set those as the optimal solutions and remove from the list
            if len(demand_node['options']) == 1:
    
                # only a single solution found and thus this is the optimal solutions by default
                temp = {'demand_node':demand_node['demand_node'],'unmet':demand_node['unmet'],'path':demand_node['options'][0]['path'],'supply_node':demand_node['options'][0]['supply_node'],'cost':demand_node['options'][0]['cost'],'weight':demand_node['options'][0]['weight']}
                optimal_solutions.append(temp)
                
                # adjust the supply available in the supply nodes dict
                for i in range(0,len(supply_available)):
                    if supply_available[i]['node'] == demand_node['options'][0]['supply_node']:
                        supply_available[i]['available'] = supply_available[i]['available'] - demand_node['options'][0]['weight']
                
                # remove from pos solutions as now an optimal solution
                pos_solutions.pop(y) 
                y -= 1 
            
            # if no more solutions to be found stop
            if len(pos_solutions) == 0:
                break
            y += 1
        
        if print_test_outputs == True: print 'Supply node states:', supply_available   
        
        # moving on to nodes with multiple solutions
            
        #if there is more than one option available from some demand nodes
            # first try using for each demand node the option with the minimum cost
            # see the effect on the supply nodes (will have to make of copy of this dict for this)
            # this is the minimum that can be done I think
            # after this to make it more advanceed to to look at making sure a few as possible supply nodes are overloaded
        
        # make a copy of the supply_node dict
        supply_available_copy = []
        for item in supply_available:
            supply_available_copy.append(item.copy())        
        
        opt_solution = []
        # loop though each demand node
        for demand_node in pos_solutions:
            
            least_cost = {'cost': 9999999999999, 'counter': 9999999999, 'supply_node': 9999999999999999999, 'weight':99999999, 'path':[]}
            k = 0
            # loop through the options to identify the least cost option
            for path_option in demand_node['options']:
                if path_option['cost'] < least_cost['cost']:
                    least_cost['cost'] = path_option['cost']
                    least_cost['counter'] = k
                    least_cost['supply_node'] = path_option['supply_node']
                    least_cost['weight'] = path_option['weight']
                    least_cost['path'] = path_option['path']
                k += 1
                
            # adjust the supply available in the supply nodes dict
            for i in range(0,len(supply_available_copy)):
                if supply_available_copy[i]['node'] == least_cost['supply_node']:
                    supply_available_copy[i]['available'] = supply_available_copy[i]['available'] - least_cost['weight']
            
            # add least cost solution to a list to record chosen option
            least_cost['demand_node'] = demand_node['demand_node']
            least_cost['unmet'] = demand_node['unmet']
            opt_solution.append(least_cost)
        if print_test_outputs == True: print '----------------------'
        # up to this point routes for all demand nodes should be assigned
        # in either the opt_solution list of the optimal_solutions list
        # for the former these should then be adjusted to utilise any spare supply 
        # capacity is possible using the supply_available_copy list
            
        #   CODE TO GO HERE TO OPTIMSE USE OF SUPPLY CAPACITY
        
        # Now that optimal solutons have been found need to merge the two solution
        # lists and supply_available lists
        
        # merge opt_solutions and optimal_solutions
        for solution in opt_solution:
            temp = {'unmet':solution['unmet'],'weight':solution['weight'],'demand_node':solution['demand_node'],'cost':solution['cost'],'path':solution['path'],'supply_node':solution['supply_node']}
            optimal_solutions.append(temp)
            # update the pos_solution list to do full due-dilligence
            for i in range(0, len(pos_solutions)):
                if pos_solutions[i]['demand_node'] == solution['demand_node']:
                    pos_solutions.pop(i)
                    break
            # update supply_available
            for i in range(0, len(supply_available)):
                if supply_available[i]['node'] == solution['supply_node']:
                    supply_available[i]['available'] = supply_available[i]['available'] - solution['weight']
                    break
       
        # Finally add flows to network before returning
        
        for solution in optimal_solutions:
            weight = solution['weight']
            for i in range(1, len(solution['path'])):
                G[solution['path'][i-1]][solution['path'][i]]['flow'] = G[solution['path'][i-1]][solution['path'][i]]['flow'] + weight
                
        # Print off some results
        if print_test_outputs == True:
            print '-------------------------'
            print 'Optimal solutions:'
            for solution in optimal_solutions:
                print solution   
            print 'Demand nodes to resolve:'
            print pos_solutions
            print 'Supply node states:'
            print supply_available
            print '-------------------------'
        
        demand_supplied = []
        for i in range(0, len(demand_nodes)):
            # will fail here if demand node has been removed from the network
            demand_supplied.append({'node':demand_nodes[i],'flow':0,'demand':G.node[demand_nodes[i]]['demand']})
            
            in_edges = G.in_edges(demand_nodes[i])
            for ed in in_edges:
                demand_supplied[i]['flow'] += G[ed[0]][ed[1]]['flow'] 
            
        supply_used = []
        if super_supply_node != False:
            supply_used.append({'node':super_supply_node,'flow':G.node[super_supply_node]['flow'],'demand':G.node[super_supply_node]['demand']})  
        else:
            supply_used.append({})
        for i in range(0, len(supply_nodes)):
            supply_used.append({'node':supply_nodes[i],'flow':G.node[supply_nodes[i]-1]['flow'],'demand':G.node[supply_nodes[i]-1]['demand']}) 
        
        unmet_demand = []
        for i in range(0,len(demand_supplied)):
            unmet_demand.append({'node':demand_supplied[i]['node'],'unmet':demand_supplied[i]['demand']-demand_supplied[i]['flow']})
    
        # check all demands have been met                       
        for node in unmet_demand:
            if node['unmet'] != int(0):
                print 'Error code: 1999'
                #print 'For some reason there are still unmet demands. This should not be the case.'
                #print 'Final Un-met demand:', unmet_demand 
                exit()
                
        return G, demand_supplied, supply_used
    
    
    def network_simplex(self, demand_nodes, supply_nodes, super_supply_node, demand = 'demand', capacity = 'flow_capacity',
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
        demand: string
        capacity: string
        weight: string
    
        Returns
        -------
        flowCost: integer, float
        flowDict: dictionary
    
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
        
        References
        ----------
        W. J. Cook, W. H. Cunningham, W. R. Pulleyblank and A. Schrijver.
        Combinatorial Optimization. Wiley-Interscience, 1998.
    
        """
        
        G = self.G
        
        sys.path.append('C:/Python27/Lib/site-packages/networkx/algorithms/flow')
        import mincost    
        #print 'In simplex function'
        if not G.is_directed():
            raise nx.NetworkXError("Undirected graph not supported.")
        if not nx.is_connected(G.to_undirected()):
            raise nx.NetworkXError("Not connected graph not supported.")
        if G.is_multigraph():
            raise nx.NetworkXError("MultiDiGraph not supported.")
        
        demand_sum = 0
        for nd in G.nodes(data=True):
            demand_sum += nd[1]['demand']
            
        #print '#### Demand sum:', demand_sum
        
        if demand_sum != 0:
            raise nx.NetworkXUnfeasible("Sum of the demands should be 0 (%s)." %demand_sum)
        
        # Fix an arbitrarily chosen root node and find an initial tree solution.
        '''
        H, T, y, artificialEdges, flowCost, r = \
                mincost._initial_tree_solution(G, demand = demand, capacity = capacity,
                                       weight = weight)
        '''
        H, T, y, artificialEdges, flowCost, r = mincost._initial_tree_solution(G, demand = demand, capacity = capacity,
                                       weight = weight)
        if r != None: 
            #print ' r is none'
            pass
        ##print 'H:'#,H.edges() #this is the network/tree
        ##print 'T:',T.edges() #tree solution
        ##print 'y:',y #node flow costs
        ##print 'artificial edges:', artificialEdges
        #print 'flowcost:',flowCost 
        ##print 'r:',r #is this the length of the route? or the root node
        
        # Initialize the reduced costs.
        c = {}
        for u, v, d in H.edges_iter(data = True):
            c[(u, v)] = d.get(weight, 0) + y[u] - y[v]
    
        # Main loop.
        while True:
            newEdge = mincost._find_entering_edge(H, c, capacity = capacity)
            ##print '---------------'
            ##print 'New edge:', newEdge
            
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
            ##print 'Leaving edge:',leavingEdge
            ##print 'eps:',eps #the flow value along the edge
            
            # Actual augmentation happens here. If eps = 0, don't bother.
            if eps:
                flowCost -= cycleCost * eps
                if len(cycle) == 3:
                    u, v = newEdge
                    #subtract the flow value from the capacity of the edge
                    H[u][v]['flow'] -= eps
                    H[v][u]['flow'] -= eps
                else:
                    for index, u in enumerate(cycle[:-1]):
                        v = cycle[index + 1]
                        if (u, v) in T.edges() + [newEdge]:
                            H[u][v]['flow'] = H[u][v].get('flow', 0) + eps
                        else: # (v, u) in T.edges():
                            #subtract the flow value from the capacity of the edge
                            ##print H[v][u]['flow']
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
                ##print 'over flow edge:', u,',',v
                over_edges.append((u,v,H[u][v]))
            H.remove_edge(u,v)            
                
        for u in H.nodes():
            if not u in G:
                H.remove_node(u)
        #print '#### Creating flow dict'
        flowDict = mincost._create_flow_dict(G, H)
      
        # would help to return the flow supplied - i.e. the demands met
        # need to work out how to do this
      
        #print '#### Assign flows to edges'
        # assign flow values to network
        self.G = self.assign_edge_node_flows(flowDict)  
        G = self.G
        demand_supplied = []
        for i in range(0, len(demand_nodes)):
            demand_supplied.append({'node':demand_nodes[i],'flow':0,'demand':G.node[demand_nodes[i]]['demand']})
            
            in_edges = G.in_edges(demand_nodes[i])
            for ed in in_edges:
                demand_supplied[i]['flow'] += G[ed[0]][ed[1]]['flow'] 
            
        supply_used = []
        if super_supply_node != False:
            supply_used.append({'node':super_supply_node,'flow':G.node[super_supply_node]['flow'],'demand':G.node[super_supply_node]['demand']})  
        else:
            supply_used.append({})
        for i in range(0, len(supply_nodes)):
            supply_used.append({'node':supply_nodes[i],'flow':G.node[supply_nodes[i]-1]['flow'],'demand':G.node[supply_nodes[i]-1]['demand']})                
        
        if print_test_outputs == True:
            print 'demand supplied:', demand_supplied
            print 'supply used:', supply_used
        
        return G, flowCost, flowDict, over_edges, demand_supplied, supply_used

class get:
    '''
    Contains all functions used to return nodes/edges/values.
    '''
    
    def __init__(self,G):
        if G == None:
            exit()
        else:
            self.G = G
            
    def get_demand_supply_nodes(self,supply='supply',demand='demand'):
        '''
        Return all nodes which are supply nodes and those which are demand nodes.
        '''
        
        supply_nodes = []
        demand_nodes = []
        
        for nd in self.G.nodes():
            if self.G.node[nd]['role'] == 'supply':
                supply_nodes.append(nd)
            elif self.G.node[nd]['role'] == 'demand':
                demand_nodes.append(nd)
        
        return supply_nodes,demand_nodes


    def get_check_supply_demand_nodes(self,supply_nodes,demand_nodes,added_nodes):
        '''
        Identify the node keys for the source and demand nodes in the network.
        '''
        if len(demand_nodes) > 1:
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

    
    def get_demand_supply_nodes_byvalues(self):
        '''
        Return the demand ans supply values as identified by thier demand 
        values.
        '''
        
        supply_nodes = []
        demand_nodes = []
    
        for nd in self.G.nodes():
            
            if self.G.node[nd]['demand'] < 0:
                supply_nodes.append(nd)
            elif self.G.node[nd]['demand'] > 0:
                demand_nodes.append(nd)
                
        return supply_nodes,demand_nodes


    def get_flow_stats(self):
        '''
        Returns dicts of the flow values for edges and nodes respectively.
        '''
        
        node_flows={}
        edge_flows={}
        for nd in self.G.nodes():
            node_flows[nd] = self.G.node[nd]['flow']
        for eg in self.G.edges():
            edge_flows[eg] = self.G.edge[eg[0]][eg[1]]['flow']
        
        return edge_flows, node_flows
    
    def get_max_flows(self,super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes):
        '''
        Returns the node and edge id's with the maximum flow and the respective 
        values.
        '''
        
        # create empty containers
        node_flow_max = {'node':[],'flow':0}
        edge_flow_max = {'edge':[],'flow':0}
        edge_flows, node_flows = self.get_flow_stats()
        
        # add super nodes to invalid nodes list
        invalid_nodes = []
        if super_supply_node != False: invalid_nodes.append(super_supply_node)
        if super_demand_node != False: invalid_nodes.append(super_demand_node)
        
        # add supply demand node to the invalid list
        for nd in supply_nodes:
            invalid_nodes.append(nd-1)
        
        # add supply demand node to the invalid list
        # adding the actual demand node won't work, this will
        for nd in demand_nodes:
            invalid_nodes.append(nd+1)
        
        #print 'Invalid nodes are:', invalid_nodes
        # get node with maximum flow
        # loop through nodes in network
        for nd in node_flows:
            consider_node = True
            # if node invalid ignore
            for node in invalid_nodes:
                if nd == node: 
                    consider_node = False
                    break
            if consider_node == True:
                # if flow greater then previous maximum
                if node_flows[nd] > node_flow_max['flow']:
                    node_flow_max['node'] = [nd]
                    node_flow_max['flow'] = node_flows[nd]
                # if flow greater then previous maximum
                elif node_flows[nd] == node_flow_max['flow']:
                    node_flow_max['node'].append(nd)
        
        # if more than one node with max value pick one at random
        if len(node_flow_max['node']) > 1:
            import random
            node_flow_max['node'] = node_flow_max['node'][random.randint(0,len(node_flow_max['node'])-1)]
        #if only one edge with max value select it
        else:
            node_flow_max = node_flow_max['node'][0]          
        
        # get edge with maximum flow
        for eg in edge_flows:
            
            consider_edge = True
            # check if edge uses an invalid node
            for node in invalid_nodes:
                if eg[0] == node or eg[1] == node:
                    consider_edge = False
                    break
            
            if consider_edge == True:
                # if edge flow is greater than the previous maximum
                if edge_flows[eg] > edge_flow_max['flow']:
                    edge_flow_max['edge'] = [eg]
                    edge_flow_max['flow'] = edge_flows[eg]
                #if edge flow is equal to the previous maximum
                elif edge_flows[eg] == edge_flow_max['flow']:
                    edge_flow_max['edge'].append(eg)
       
        # if more than one edge with max value pick one at random
        if len(edge_flow_max['edge']) > 1:
            import random
            edge_flow_max['edge'] = edge_flow_max['edge'][random.randint(0,len(edge_flow_max['edge'])-1)]
        #if only one edge with max value select it
        else:
            edge_flow_max['edge'] = edge_flow_max['edge'][0]
        
        return node_flow_max, edge_flow_max


    def get_demand_supplied_supply_used(self):
        '''
        Find the supply used from each supply node and the value of flow sent to 
        each demand node.
        '''    
        
        supply_nodes, demand_nodes = self.get_demand_supply_nodes_byvalues()
        
        #print '------------------'
        #print 'Supply nodes:', supply_nodes
        #print 'Demand nodes:', demand_nodes
        #print '------------------'    
    
        demand_supplied = []
    
        for i in range(0, len(demand_nodes)):
            demand_supplied.append({'node':demand_nodes[i],'flow':0,'demand':self.G.node[demand_nodes[i]]['demand']})
            
            in_edges = self.G.in_edges(demand_nodes[i])
            #print 'Edges flowing into demand node:', in_edges
            for ed in in_edges:
                demand_supplied[i]['flow'] += self.G[ed[0]][ed[1]]['flow'] 
            
        supply_used = []
        
        for i in range(0, len(supply_nodes)):
            supply_used.append({'node':supply_nodes[i],'flow':self.G.node[supply_nodes[i]-1]['flow'],'demand':self.G.node[supply_nodes[i]]['demand']}) 
            
            out_edges = self.G.out_edges(supply_nodes[i])
            for ed in out_edges:
                supply_used[i]['flow'] += self.G[ed[0]][ed[1]]['flow']
            
        #print 'demand supplied:', demand_supplied
        #print 'supply used:', supply_used
        
        return demand_supplied, supply_used
    
    def get_max_flow_values(self,use_node_capacities=True,use_node_demands=False):
        '''
        This runs a ford-fulkerson maximum flow algrothim over the provided network
        and assigns the resulting flows to each edge. The flows for each node are 
        also calcualted and assigned.
        '''
        
        #print self.G.nodes()
        #print self.G.edges()
        d_nd, s_nd = get(self.G).get_demand_supply_nodes()
        #print d_nd
        #print s_nd        
        
        if use_node_capacities == True:
            self.G, supply_nodes, demand_nodes, super_supply_node, super_demand_node = topological_changes(self.G).convert_topo()
        
        #check for supply and demand nodes. Needs to be at least one of each.
        #if more than one need to create a super source/sink(demand) nodes.
        self.G,supply_nodes, demand_nodes, added_nodes, added_edges = topological_changes(self.G).check_for_demand_supply_nodes()
        
        #get supply node and demand node
        supply_nd,demand_nd = get(self.G).get_check_supply_demand_nodes(supply_nodes,demand_nodes,added_nodes)
        
        if use_node_capacities == True and use_node_demands == False:
            #this returns the maximum flow and the flow on each edge by node
            #first check a path is possible - ford-fulkerson would just return 0 otherwise
            path = nx.has_path(self.G,supply_nd,demand_nd)
            if path == False:
                raise error_classes.GeneralError('No path exists between the supply node (node %s) and the demand node (node %s).' %(supply_nd,demand_nd))
    
            max_flow, edge_flows = nx.ford_fulkerson(self.G, supply_nd,demand_nd,'flow_capacity')
            
        elif use_node_capacities == True and use_node_demands == True:
            #returns the flow on each edge given capacities and demands       
            #the sum of the demand needs to equal the sum of the supply (indicated by a negative demand value)
            edge_flows = nx.min_cost_flow(self.G,'demand','flow_capacity','weight')
        elif use_node_capacities == False and use_node_demands == True:
            #returns the flow on each edge given demands (capacities should be set at 9999999 (a very high number))
            edge_flows = nx.min_cost_flow(self.G,'demand','flow_capacity','weight')
    
        #assign flows to nodes and edges
        self.G = flow(self.G).assign_edge_node_flows(edge_flows)
    
        #before running any analysis, need to remove the added nodes and edges - the super source/demand if used
        self.G = topological_changes(self.G).remove_added_nodes_edges(added_edges,added_nodes)
        
        node_flow_max, edge_flow_max = self.get_max_flows(super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes)
        
        return self.G, {'max_flow':max_flow,'max_node_flow':node_flow_max,'max_edge_flow':edge_flow_max}
    
            
class other:
    '''
    Contains all functions related to assignment of flows.
    '''
    def __init__(self,G):
        if G == None:
            exit()
        else:
            self.G = G
    
    def set_random_capacities(self,a,b,capacity):
        '''
        Assign a random capacity to both the nodes and the dges in the network.
        '''
    
        import random    
        for edge in self.G.edges(): self.G[edge[0]][edge[1]][capacity] = random.randint(a,b)
        for node in self.G.nodes(): self.G.node[node][capacity] = random.randint(a,b)
        
        return self.G
    
    
    def reset_flow_values(self):
        '''
        Reset the flow values in the network to 0. Allows the recomputation of 
        flows in the network.
        '''
        
        #reset flow values to zero before calculating new values
        for node in self.G.nodes(data=True): self.G.node[node[0]]['flow'] = 0
        for edge in self.G.edges(data=True): self.G.edge[edge[0]][edge[1]]['flow'] = 0
        
        return self.G
        
    def set_demand_values(self):
        '''
        Set demand values in the network based on the current flow values.
        '''
        G = self.G
        #need to sum up the flows through nodes with a 'supply' role
        supply_total = 0
        demand_total = 0
        
        # set demand values at 0 - default value
        for node in G.nodes():
            G.node[node]['demand'] = 0
            
        # get supply and demand totals from the assigned flows
        supply_nodes = []
        for node in G.nodes(data=True):
            if G.node[node[0]]['role'] == 'supply':
                supply_total += G.node[node[0]]['flow']
                G.node[node[0]]['demand'] = 0
                supply_nodes.append(node)
            elif node[0] == 'ssupply' or G.node[node[0]]['role'] == 'super_supply_supply':
                # if a super supply node no need to sum those which meet the above
                supply_total = G.node[node[0]]['flow']
                supply_nodes = [node]
                break
                
        #print 'Demand nodes'
        demand_nodes = []
        for node in G.nodes(data=True):
            if G.node[node[0]]['role'] == 'demand':
                for edge in G.in_edges(node[0]):
                    demand_total += G[edge[0]][edge[1]]['flow']
                G.node[node[0]]['demand'] = 0
                demand_nodes.append(node)
            elif node[0] == 'sdemand' or G.node[node[0]]['role'] == 'super_demand_demand':
                demand_total = 0
                # if a supper demand node no need to sum those which meet the above
                for edge in G.in_edges(node[0]):
                    demand_total += G[edge[0]][edge[1]]['flow']
                demand_nodes = [node]
                break
            
        # check for consistancy errors in supply and demand values                
        if demand_total != supply_total or len(supply_nodes) == 0 or len(demand_nodes) == 0:
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
            
        # assign supply and demand values to appropraite nodes in network
        #print 'Supply nodes'
        print supply_nodes
        exit()
        if len(supply_nodes) == 1:
            for nd in supply_nodes:
                G.node[nd[0]]['demand'] = 0 - supply_total
        else:
            for nd in supply_nodes:
                G.node[nd[0]]['demand'] = 0 - G.node[nd[0]]['flow']
        
        if len(demand_nodes) == 1:
            for nd in demand_nodes:
                G.node[nd[0]]['demand'] = demand_total
        else:
            for nd in demand_nodes:
                G.node[nd[0]]['demand'] = G.node[nd[0]]['flow']
      
        return G
        
    def set_capacity_values(self,supply_node,multiplier,default_value,capacity):
        '''
        Sets the initial capacity value for nodes and edges using tbhe flow passing
        through them and the multiplier value.
        '''
    
        # loop through edges
        for edge in self.G.edges(data=True):
            # if the flow value is greater than zero add a capacity
            if self.G[edge[0]][edge[1]]['flow'] != 0:
                self.G[edge[0]][edge[1]][capacity] = self.G[edge[0]][edge[1]]['flow'] * multiplier
            # if there is a flow of zero or less use the default value
            else: self.G[edge[0]][edge[1]][capacity] = default_value
        
        # loop through the nodes
        for node in self.G.nodes(data=True):
            # if the flow value is greater than zero add a capacity
            if self.G.node[node[0]]['flow'] != 0:
                 self.G.node[node[0]][capacity] = self.G.node[node[0]]['flow'] * multiplier
            # if there is a flow of zero or less use the default value
            else: self.G.node[node[0]][capacity] = default_value
        
        # make sure the capacity on supply nodes is correct when from a super supply node
        if supply_node == 'ssupply':
            # get edges from super supply node to find supply nodes
            out_edges = self.G.out_edges('ssupply')
            
            # loop through out edges to assign capacity to supply nodes
            for u,v in out_edges:
                #print 'Assigning a value of:', G.node['ssupply']['flow']/len(out_edges)
                self.G.node[v]['flow_capacity'] = self.G.node['ssupply']['flow']/len(out_edges)
        
        return self.G
        
    def check_over_capacity(self,super_supply_node,super_demand_node,supply_node,demand_node):
        '''
        Identify those nodes which are over capacity. Ignores supply and demand nodes.
        '''
        # in here need to account for nodes/edges which should be excluded e.g. 16-17,31-16,28-29 and 29-32.
        # eg those with a transfer role, only select those with a role as 'network_edge'
        
        edges_over = []
        nodes_over = []
        
        # add super nodes to invalid nodes list
        invalid_nodes = []
        if super_supply_node != False: invalid_nodes.append(super_supply_node)
        if super_demand_node != False: invalid_nodes.append(super_demand_node)
        
        # add supply demand node to the invalid list
        for nd in supply_node:
            invalid_nodes.append(nd-1)
        
        # add supply demand node to the invalid list
        # adding the actual demand node won't work, this will
        for nd in demand_node:
            invalid_nodes.append(nd+1)
        
        #print 'Invalid nodes are:', invalid_nodes
        # loop through edges to check for being over capacity
        
        for edge in self.G.edges():
            pass_edge = False
            for nd in invalid_nodes:
                if edge[0] == nd or edge[1] == nd:
                    pass_edge = True
            if pass_edge == False:
                if self.G[edge[0]][edge[1]]['flow'] > self.G[edge[0]][edge[1]]['flow_capacity']:
                    edges_over.append(edge)
        
        # loop through nodes checking for those over capacity
        for node in self.G.nodes():
            if self.G.node[node]['flow'] > self.G.node[node]['flow']:
                nodes_over.append(node)
        
        return edges_over,nodes_over
    
    def find_alternative_route(self):
        '''
        To find an alternative route when an edge is overloaded.
        '''
        # this should take an overloaded edge and look for a route where no edges
        # will be overloaded. This then has implications as where do you stop with 
        # this. The process could go on forever.
        
        K = self.G.copy()
        
        #loop through network and remove any edges at capacity
        # for those not reduce capacity based on flow
        # record those which are over cpacity
        edge_to_reduce = []
        for edge in K.edges():
            if  K[edge[0]][edge[1]]['flow_capacity'] ==  K[edge[0]][edge[1]]['flow']:
                # edge at capacity
                K.remove_edge(edge[0],edge[1])
            elif K[edge[0]][edge[1]]['flow_capacity'] <  K[edge[0]][edge[1]]['flow']:
                # edge over cacpacity - record and remove
                edge_to_reduce.append(edge)
                K.remove_edge(edge[0],edge[1])
            else:
                #set available capacity
                K[edge[0]][edge[1]]['available_capacity'] =  K[edge[0]][edge[1]]['flow_capacity']- K[edge[0]][edge[1]]['flow']
        
        
        #print 'Edges to reduce capacity on:', edge_to_reduce
        #print 'Edges in G:', G.number_of_edges()
        #print 'Edges in K:', K.number_of_edges()
        
        for edge in edge_to_reduce:
            try:
                path = nx.shortest_path(K,edge[0],edge[1],'weight')
            except nx.exception.NetworkXNoPath:
                #print 'no path exists'
                pass
            else:
                #print 'A path exists:',path
                pass
                ok = True
                weight_needed = self.G[edge[0]][edge[1]]['flow'] - self.G[edge[0]][edge[1]]['flow_capacity']
                #print weight_needed
                for i in range(1, len(path)):
                    if K[path[i-1]][path[i]]['available_capacity'] < weight_needed:
                        pass
                    else:
                        ok = False
                        break
                    
                if ok == True:
                    #print 'path works!'
                    pass
                else:
                    #print 'Path cannot handle the capacity.'
                    pass
        
        return self.G
    
        
    def track_flows(self, super_supply_node, supply_nodes, demand_nodes):
        '''
        Track a flow where it appears that a flow which starts does not reacch
        a demand node.
        
        This is not really needed. Was just added for testing purposes.
        '''    
        
        supply = 0
        demand = 0
        if super_supply_node == False:
            for nd in supply_nodes:
                supply += self.G.node[nd]['demand']*-1
        else:
            supply = self.G.node[super_supply_node]['demand']*-1
            
        for nd in demand_nodes:
            demand += self.G.node[nd]['demand']
        
        if supply != demand:
            print 'Need to track %s missing flow(s)' %(demand-supply)
           
        return self.G
    
    def simulation_completed(self,text,graph_edges_removed,print_edges,print_nodes):
        '''
        '''        
        print 'Reason for termination:', text
        print 'Edges removed:', graph_edges_removed
        if print_edges == True:
            print self.G.edges()
        if print_nodes == True:
            print self.G.nodes()       
