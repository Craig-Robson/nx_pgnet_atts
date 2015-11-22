# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:04:04 2015

@author: Craig
"""
import sys, ogr
import random
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet_atts') #desktop
sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet_atts') #laptop
import nx_pgnet_atts
import maxflow_tools as maxflow_tools
import networkx as nx
#import testing_networks #contains the networks used for testing
import error_classes

def load_network_from_db(name, db_params):
    '''
    '''

    '''Database connection details and network name'''
    conn = ogr.Open("PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (db_params['host'], db_params['dbname'], db_params['user'], db_params['password'], db_params['port']))
     
    #srid_a = 27700; srid_b = 27700; spatial_a = True; spatial_b = True
    #save_a = True; save_b = True; net_name_b = ''
    #db_parameters = conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b
    
    '''read network from database'''
    #name = 'sample'
    #name = 'test_new_write'
    attributes = [{'flow':True, 'buffer':True, 'resistance':False, 'latency':False},{'flow':True, 'length':False, 'resistance':True, 'stacking':False}]
    G = nx_pgnet_atts.read(conn,name).read_from_db(attributes)
    
    #print G.node[1].keys()
    
    '''convert network to directed'''
    if nx.is_directed(G) == False:
        G = G.to_directed()
        #print "Converted network to a directed network."
    
    '''run max flow algorithm'''
    #get max flows - capacities set, no demands (network,capacities,demands)
    G,results = maxflow_tools.get(G).get_max_flow_values(True,False)
    #G,results = max_flow.get_max_flow_values(G,True,True) #has not been tested yet. Demands should = 0 (negative for supply nodes).
    
    #print results
    """              
    """
    '''revert the topology of the network to standard topological representation'''
    #this allows a network to be converted back to original format
    G = maxflow_tools.topological_changes(G).revert_topo() 
 
    return G
    
def write_result_file_simulation_end(results_file,text,trigger_edges,graph_edges_removed,graph_nodes_removed):
    '''
    Write results at end of simualtion to the results file.
    '''
    results_file.write('\nSimulation completed. %s.' %text)
    results_file.write('\nTrigger edges: %s' %trigger_edges)
    results_file.write('\nEdges removed: %s' %graph_edges_removed)
    results_file.write('\nNodes removed: %s' %graph_nodes_removed)
    results_file.close()
    return
    
def set_single_supply_demand_randomly(G):
    '''
    Select at random a single supply and demand node.
    '''
    nodes = G.nodes()
    
    # reset the role of any node to transfer
    for node in G.nodes():
        if G.node[node]['role'] == 'supply':
            G.node[node]['role_id'] = 1
            G.node[node]['role'] = 'transfer'
            G.node[node]['role_type'] = 'transfer'
        elif G.node[node]['role'] == 'demand':
            G.node[node]['role_id'] = 1
            G.node[node]['role'] = 'transfer'
            G.node[node]['role_type'] = 'transfer'
        
    # select at random the demand and supply node
    demand = nodes[random.randint(0,len(nodes)-1)]
    supply = nodes[random.randint(0,len(nodes)-1)]

    # ensure the same node is not selected as demand and supply
    while supply==demand:
        supply = nodes[random.randint(0,len(nodes)-1)]
    
    # set attributes for selected supply and demand node
    G.node[demand]['role'] = 'demand'
    G.node[demand]['role_id'] = 2
    G.node[demand]['role_type'] = 'demand'
    G.node[supply]['role'] = 'supply'
    G.node[supply]['role_id'] = 3
    G.node[supply]['role_type'] = 'supply'
    
    return G    
    
def func_check_demands_met(G,fail_print_nodes,fail_print_edges,terminate):
    '''
    Check that the demands in the network are met.
    '''
    if G != None:
        a,b = maxflow_tools.get(G).get_demand_supplied_supply_used()
        for node in a:
            if node['flow'] != node['demand']:
                raise error_classes.DemandError(G, 'Demand has not been met. This should be done in all cases.',fail_print_nodes,fail_print_edges)
        #if trigger_until_cascading == False:
        #    if terminate == True:
                #break
    else:
        if trigger_until_cascading == False:
            terminate == True
            print 'Fatal Error!'
            #break
        
    return G, terminate
    

def func_calculate_edge_flows(G,demand_nodes, supply_nodes, super_supply_node,checking_flow_demand,fail_print_nodes,fail_print_edges):
    '''
    Calculate the flows over the network as required.
    '''
    # reset flows to zero
    G = maxflow_tools.other(G).reset_flow_values()
    # find flows over network
    G, cost,edge_flows,over_edges,demand_supplied,supply_used = maxflow_tools.flow(G).network_simplex(demand_nodes, supply_nodes, super_supply_node, demand = 'demand',capacity = 'flow_capacity',weight='weight')
    
    # here we can record the degree to which the demands can be met within the limits of the network i.e. how much spare capacity?
    
    
    # uses a shortest path to assign flows to network where supply and demand values are not met
    print '### Calculated flows over network'  
            
    demand_supplied_2,b = maxflow_tools.get(G).get_demand_supplied_supply_used()
    for node in demand_supplied_2:
        if checking_flow_demand == True:
            if node['demand'] < node['flow']:
                raise error_classes.DemandError(G,'Demand has not been met. This should be done in all cases.',fail_print_nodes,fail_print_edges)
    
    # take the over edges from network simplex and add flows to network
    # now just uses the demand not delivered to identify routes with the supply capacity
    G, demand_supplied, supply_used = maxflow_tools.flow(G).resolve_edge_flows(over_edges,demand_nodes, supply_nodes, super_supply_node,demand_supplied,supply_used)
    
    
    return G, cost,edge_flows,over_edges,demand_supplied,supply_used
        
def func_set_edge_capacities(G,net_name):
    '''
    Sets the edge capacity of a network based on its type. Applies only to synthetic networks.
    '''    
    multiplier = 1000
    if net_name == 'gnm522' or net_name == 'er198':
        for edge in G.edges():
            G[edge[0]][edge[1]]['flow_capacity'] = random.randint(1,4)
        for node in G.nodes():
            G.node[node]['flow_capacity'] = random.randint(1,4)
        
    elif net_name == 'ba119' or net_name == 'ws989':
        degree = nx.degree(G)
        degree = sum(degree.values())/nx.number_of_nodes(G)            
        
        node_dict = nx.betweenness_centrality(G)
        
        for node in G.nodes():
            G.node[node]['flow_capacity'] = node_dict[node] * multiplier
            
        edge_dict = nx.edge_betweenness_centrality(G)
    
        for edge in edge_dict:
            G[edge[0]][edge[1]]['flow_capacity'] = edge_dict[edge] * multiplier
        
    elif net_name == 'hr577' or net_name == 'ahr72' or net_name == 'tree5':
        #need to assign node levels, and then capacities.
        #capacities for edges can then be worked out thereafter
        max_val = 8
        node_level_counts = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        for node in G.nodes():
            node_level_counts[int(G.node[node]['level'])] = node_level_counts[int(G.node[node]['level'])]+1
        
        for node in G.nodes():
            G.node[node]['flow_capacity'] = max_val/node_level_counts[int(G.node[node]['level'])]
    
        edge_level_counts = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        for edge in G.edges():
            edge_level_counts[G.edge[edge[0]][edge[1]]['level_from']] = edge_level_counts[G.edge[edge[0]][edge[1]]['level_from']]+1
        
        for edge in G.edges():
            G.edge[edge[0]][edge[1]]['flow_capacity'] = max_val/edge_level_counts[G.edge[edge[0]][edge[1]]['level_from']]
    elif net_name == 'hc7':
        pass
    else:
        exit()

    return G



def func_trigger_edge(G,trigger_edge,trigger_edges,super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes,results_file):
    '''
    Takes the network and trigger variables and selects the node or edge to remove as a trigger to a cascading failure.
    '''
    
    if trigger_edge == []:
        
        # remove edge with greatest flow as a trigger for cascading failure
        node_flow_max, edge_flow_max = maxflow_tools.get(G).get_max_flows(super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes)
        trigger_edges.append(edge_flow_max)
        print '#### Removed edge with greatest flow:', edge_flow_max
        print '#### Removed edge with greatest flow:', G[edge_flow_max['edge'][0]][edge_flow_max['edge'][1]]['flow_capacity']
        try:
            G.remove_edge(edge_flow_max['edge'][0],edge_flow_max['edge'][1])
            results_file.write('\nEdge removed as trigger: %s' %(edge_flow_max))
        except: 
            print 'Could not remove selected edge, %s' %(edge_flow_max)
            exit()
            
       
        trigger_edge = ([edge_flow_max['edge']])
    else:
        
        # need to find the new edge which was originaly the trigger before topology was converted
        trigger_edge = maxflow_tools.topological_changes(G).get_trigger_edge(trigger_edge)        
        
        G.remove_edge(trigger_edge[0],trigger_edge[1])
        print '#### Removed trigger edge:', trigger_edge
        
    return G,trigger_edges, trigger_edge

def flow_fail_sim(G,demand_value,capacity_factor,default_capacity,trigger_edge,g_name,result_file_path,run,adjust_capacities,net_name,set_edge_capacities_by_type,select_supply_demand_at_random,trigger_until_cascading):
    
    ### variables for removing nodes and edges
    remove_nodes_over = False
    remove_edges_over = True
    
    ### variables for testing
    print_test_outputs = False
    find_alt_routes = False
    
    checking_flow_demand = True   
    
    ### what to do on failure
    fail_print_nodes = False
    fail_print_edges = True
    
    ### what to do on completion
    print_nodes = False
    print_edges = False
    
    ## set result file path
    if run != None:
        result_file_path = result_file_path+'\\result_%s_run_%s.txt' %(g_name,run)
    else:
        result_file_path = result_file_path+'\\result_%s.txt' %g_name
    
    ### open results file
    results_file = open(result_file_path,'w')
    
    ### set demand value based on the number of nodes in the network
    #demand_value = nx.number_of_nodes(G)/2.0
    #default_capacity = nx.number_of_nodes(G)/30.0
    #default_capacity = nx.number_of_edges(G)/100.0
    
    ### start of model    
    
    #create containers to store removed edges and nodes    
    graph_edges_removed = []; graph_nodes_removed = []
    
    # add a random capacity value to all nodes and edges
    #G = maxflow_tools.set_random_capacities(G,3,8,'flow_capacity')
    
    if print_test_outputs == True: print '## Creating super nodes if needed'
    # create super nodes for supply and demand
    G,supply_nodes,demand_nodes,added_nodes,added_edges = maxflow_tools.topological_changes(G).check_for_demand_supply_nodes()
    
    
    if set_edge_capacities_by_type == True:
        #set edge capacities based on the network type (given the name)
        G = func_set_edge_capacities(G,net_name)
    else:
        #set flow capacity for edges
        for edge in G.edges():
            G[edge[0]][edge[1]]['flow_capacity'] = default_capacity
            #print G[edge[0]][edge[1]]['flow_capacity']
        for node in G.nodes():
            G.node[node]['flow_capacity'] = default_capacity
            
    if select_supply_demand_at_random == True:
        #select a single supply and demand node at random
        #reseats the roles of all other nodes adn edges as well
        G = set_single_supply_demand_randomly(G)
 
    # convert topology
    G,supply_nodes,demand_nodes,super_supply_node,super_demand_node = maxflow_tools.topological_changes(G).convert_topo('demand','supply','intermediate','flow_capacity')
    '''    
    print '--------------------------------'
    print 'Supply node(s):', supply_nodes
    print 'Demand node(s):', demand_nodes
    print '--------------------------------'
    '''
    
    #reset flow values to zero
    G = maxflow_tools.other(G).reset_flow_values()        
    
    #set demand values
    # set value of zero for all nodes
    for nd in G.nodes():G.node[nd]['demand'] = 0
    
    #set demand values for demand node(s)
    if super_demand_node != False:
        G.node[super_demand_node]['demand'] = demand_value
    else:        
        split_demand_value = demand_value/len(demand_nodes)
        for nd in demand_nodes:
            print 'Assigning a demand to node',nd,'of', split_demand_value
            G.node[nd]['demand'] = split_demand_value
    
    # set demand values for supply node(s)        
    if super_supply_node != False:
        supply_nd = super_demand_node
        G.node[super_supply_node]['demand'] = -demand_value
    else:
        split_demand_value = demand_value/len(supply_nodes)
        for nd in supply_nodes:
            print 'Assinging a demand to node',nd,'of', -split_demand_value
            supply_nd = nd
            G.node[nd]['demand'] = -split_demand_value
            
    #set flow capacity for edges
    #set capacities as equal to the demand in the network for all nodes and egdes            
    #for edge in G.edges(): G[edge[0]][edge[1]]['flow_capacity'] = default_capacity 
    
      
    #print 'A supply of %s is available from node %s.' %(G.node[supply_nodes[0]]['demand'],supply_nodes[0])
    #print 'A demand of %s must be met for node %s.' %(G.node[demand_nodes[0]]['demand'],demand_nodes[0])
    
    #print 'Running network simplex'
    # run network simplex
    try:
        cost,edge_flows = nx.network_simplex(G,demand = 'demand',capacity = 'flow_capacity',weight='weight')
    except:
        print 'Probably no flow satisfying all demands'
        return
    print 'b'
    for edge in G.edges():
        if int(G[edge[0]][edge[1]]['flow_capacity']) != 4:
            print 'some edges have wrong capacity'
            break
    # assign flow values to network
    G = maxflow_tools.flow(G).assign_edge_node_flows(edge_flows)
    
    #print 'Setting capacities based on flows'
    if adjust_capacities == True:
        print '### Adjusting capacities based on flow values'
        # set capacities based on flow values
        G = maxflow_tools.other(G).set_capacity_values(supply_nd,capacity_factor,default_capacity,'flow_capacity') 
            
    # initiate cascading failure    
    trigger_edges = []
    G,trigger_edges,graph_edges_removed = func_trigger_edge(G,trigger_edge,trigger_edges,super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes,results_file)
        
    print '## Running cascading failure'
    terminate = False
    step_count = 1
    trigger_step = 1
    graph_nodes_removed.append([])

    for edge in G.edges():
        if int(G[edge[0]][edge[1]]['flow_capacity']) != 4:
            print 'some edges have wrong capacity'
            break
            #print G[edge[0]][edge[1]]['flow_capacity']    
    
    while terminate == False and step_count < 100:
        print '-------------------------------------'
        print 'Trigger step:', trigger_step
        print 'Step:', step_count
        results_file.write('\nCascading failure: step %s' %step_count)
        
        try:
            if print_test_outputs == True: print '### Calculate flows'
            '''
            # reset flows to zero
            G = maxflow_tools.other(G).reset_flow_values()
            # find flows over network
            G, cost,edge_flows,over_edges,demand_supplied,supply_used = maxflow_tools.flow(G).network_simplex(demand_nodes, supply_nodes, super_supply_node, demand = 'demand',capacity = 'flow_capacity',weight='weight')
            
            # here we can record the degree to which the demands can be met within the limits of the network i.e. how much spare capacity?
            
            
            # uses a shortest path to assign flows to network where supply and demand values are not met
            print '### Calculated flows over network'  
                    
            demand_supplied_2,b = maxflow_tools.get(G).get_demand_supplied_supply_used()
            for node in demand_supplied_2:
                if checking_flow_demand == True:
                    if node['demand'] < node['flow']:
                        raise error_classes.DemandError(G,'Demand has not been met. This should be done in all cases.',fail_print_nodes,fail_print_edges)
            
            # take the over edges from network simplex and add flows to network
            # now just uses the demand not delivered to identify routes with the supply capacity
            G, demand_supplied, supply_used = maxflow_tools.flow(G).resolve_edge_flows(over_edges,demand_nodes, supply_nodes, super_supply_node,demand_supplied,supply_used)
            '''
            G, cost,edge_flows,over_edges,demand_supplied,supply_used = func_calculate_edge_flows(G,demand_nodes, supply_nodes, super_supply_node,checking_flow_demand,fail_print_nodes,fail_print_edges)
            
            if print_test_outputs == True: print '### Resolved edge flows - (demand supplied: %s, supply_used: %s)' %(demand_supplied, supply_used)
                
            G = maxflow_tools.other(G).track_flows(super_supply_node, supply_nodes, demand_nodes)                
            
            # check after the routing of flows that all demands are met
            G, terminate = func_check_demands_met(G,fail_print_nodes,fail_print_edges,terminate)
            if terminate == True: break
            '''
            if G != None:
                a,b = maxflow_tools.get(G).get_demand_supplied_supply_used()
                for node in a:
                    if node['flow'] != node['demand']:
                        raise error_classes.DemandError(G, 'Demand has not been met. This should be done in all cases.',fail_print_nodes,fail_print_edges)
                if trigger_until_cascading == False:
                    if terminate == True:
                        break
            else:
                if trigger_until_cascading == False:
                    terminate == True
                    print 'Fatal Error!'
                    break
            '''
            print '### Checking for edges over capacity'
            # check for edges over capacity
            edges_over, nodes_over = maxflow_tools.other(G).check_over_capacity(super_supply_node,super_demand_node,supply_nodes,demand_nodes)
            print 'Edges over:', edges_over
            print 'trigger until cascading:', trigger_until_cascading
            #this is optional at the moment until sure this is needed
            if find_alt_routes == True:
                G = maxflow_tools.find_alternative_route(G)

            if len(edges_over) > 0:
                trigger_until_cascading = False
            else:
                G, trigger_edges, trigger_edge = func_trigger_edge(G,trigger_edge,trigger_edges,super_supply_node,super_demand_node,supply_nodes,demand_nodes,added_nodes,results_file)
                trigger_edge = []
                trigger_step += 1
            
            if remove_nodes_over == True and len(nodes_over) > 0:
                print '### Remove nodes over capacity'            ParkRun Replacement - icy
                for u in nodes_over:
                    print 'Removed node: %s' %u
                    G.remove_node(u)

            if remove_edges_over == True and len(edges_over) > 0:
                print '### Remove edges over capacity'
                # remove edges which are over capacity
                for u,v in edges_over:
                    print 'Removed edge: (%s,%s)' %(u,v)
                    G.remove_edge(u,v)
                
            # record the edges and nodes removed at each time step            
            graph_edges_removed.append(edges_over) # only really interested in this
            graph_nodes_removed.append(nodes_over)
            results_file.write('\nEdges removed: %s' %edges_over)
            results_file.write('\nNodes removed: %s' %nodes_over)
            
            # need to look at subgraph methods - this is where it breaParkRun Replacement - icyks at the moment
            # need to think about creating super demand and supply nodes for subgraphs
            if print_test_outputs == True: print '### Check subgraphs in network'

            # need to remove subgraphs which cannot be computed
            G,demand_nodes =  maxflow_tools.flow(G).handle_subgraphs(supply_nodes,demand_nodes,super_supply_node,super_demand_node)
            
            if G == None:
                # no subgraph has both a supply and demand node so run terminated
                text = 'No graphs with both supply and demand nodes left'
                terminate = maxflow_tools.other(G).simulation_completed(text,graph_edges_removed,print_edges,print_nodes)
                write_result_file_simulation_end(results_file, trigger_edges, graph_edges_removed, graph_nodes_removed)                
            
            if print_test_outputs == True: print '### Check supply still left in network'        
            # if the supply value now at zero, stop simulation
            demand_sum = sum(d['demand'] for v, d in G.nodes(data = True))

            if demand_sum != 0:
                raise error_classes.DemandError(G,'Demand across network does not equal zero as it should.',fail_print_nodes,fail_print_edges)
            
            # check demand in the network has not reached 0 - if not a super supply node then must add up             
            if super_supply_node != False and terminate == False:
                if G.node[super_supply_node]['demand'] == 0: 
                    text = 'Supply in network is now zero'
                    terminate = maxflow_tools.other(G).simulation_completed(text,graph_edges_removed,print_edges,print_nodes)
                    write_result_file_simulation_end(results_file, trigger_edges, graph_edges_removed, graph_nodes_removed)                    
                    
            elif terminate == False:
                supply_left = 0
                for nd in supply_nodes:
                    supply_left += -G.node[nd]['demand']
                if supply_left == 0:
                    text = 'Supply in network is now zero'
                    terminate = maxflow_tools.other(G).simulation_completed(text,graph_edges_removed,print_edges,print_nodes)
                    write_result_file_simulation_end(results_file,text,trigger_edges,graph_edges_removed,graph_nodes_removed)
                    
        except nx.exception.NetworkXUnfeasible:
            text = 'No routes which allow demand(s) to be met'
            terminate = maxflow_tools.other(G).simulation_completed(text,graph_edges_removed,print_edges,print_nodes)
            write_result_file_simulation_end(results_file,text,trigger_edges,graph_edges_removed,graph_nodes_removed)
            
        #check if any changes since last step - if not terminate
        # this should only terminate if trigger untilc ascading is false - some cascading has occured
        if trigger_until_cascading == False and graph_edges_removed[step_count] == [] and graph_nodes_removed[step_count] == []  and terminate == False:
            text = 'Network has reached an equilibrium'
            terminate = maxflow_tools.other(G).simulation_completed(text,graph_edges_removed,print_edges,print_nodes)
            write_result_file_simulation_end(results_file,text,trigger_edges,graph_edges_removed,graph_nodes_removed)
        #iterate the step counter based on what has happend thus far
        step_count += 1
    
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
db_params = {}
db_params['host'] = 'localhost'; 
db_params['dbname'] = '_new_schema_synthetics' #'_new_schema'
db_params['port'] = 5433
db_params['user'] = 'postgres';
db_params['password'] = 'aaSD2011'
result_path = 'F:\\a8243587\\work_package_two\\results'

#networks of equal size
net_names = 'er198','gnm522','ba119','ws989','hr577','ahr72','hc7','tree5'


number_of_runs = 5
adjust_capacities = False
set_edge_capacities_by_type = False
select_supply_demand_at_random = True
trigger_until_cascading = True

run = 0
while run < number_of_runs:
    for net_name in net_names:
        print '----------------------\n----------------------'
        print 'Running for %s' %(net_name)
        if adjust_capacities == True:
            params = {'capacity_factor':1.0,'demand_value':100,'trigger_edge':[],'default_capacity':4}
        else:
            params = {'capacity_factor':1.0,'demand_value':24,'trigger_edge':[],'default_capacity':4}
        G = load_network_from_db(net_name,db_params)
                
        #run failure simulation over the network
        flow_fail_sim(G,params['demand_value'],params['capacity_factor'],params['default_capacity'],params['trigger_edge'],net_name,result_path,run,adjust_capacities,net_name,set_edge_capacities_by_type,select_supply_demand_at_random,trigger_until_cascading)
    run += 1