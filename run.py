# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 13:56:45 2014

@author: a8243587
"""
import networkx as nx
import sys, ogr
import random
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
import nx_pg
import nx_pgnet_atts as nx_pgnet_av #read and write methods to db

'''-------------pull network from database and create networkx instance-----'''
name = "sample"
#name = "tyne_wear_m_a_b"
conn = ogr.Open("PG:dbname='_new_schema' host='localhost'port='5433' user='postgres' password='aaSD2011'")
conn.ExecuteSQL("SELECT np_delete_all_tables('%s');" %(name))

'''-------------create networkx instance from database----------------------'''
#G = nx_pg.read_pg(conn, 'sample_lines','sample_points')
G = nx_pg.read_pg(conn, 'sample_lines_atts','sample_points_atts')
#G = nx_pg.read_pg(conn, 'tyne_wear_m_a_b') #no attributes added at this time
contains_atts = False; contains_functions = False

#for nd in G.nodes(): print nd, G.node[nd]['role'],G.node[nd]['id']  
#for eg in G.edges(): print eg

'''-------------add network to db with specified attributes-----------------'''
#attributes = None
attributes = [{'flow':True, 'storage':True, 'resistance':False, 'latency':False},
              {'flow':True, 'length':False, 'resistance':False, 'stacking':False}]
result = nx_pgnet_av.write(conn,name).write_to_db(G,attributes, contains_atts, contains_functions,True,27700,True,False)

#exit()
if result == False: exit()
else: print "Network added."

'''-------------add functions to functions table----------------------------'''
if contains_functions == False:
    functions = [('constant','capacity',1), ('constant',' ',0),
             ('expression', 'capacity / flow ',2)]
             
    result = nx_pgnet_av.write(conn,name).add_functions(functions)
    if result == False: print "Error adding functions! Check function table exists and the inputs are correct."

'''-------------add attribute values and function ids to nodes and edges----'''
if contains_atts == False and contains_functions == False:
    attribute = 'storage' ; att_value_range = [5,25] ; functionid_range = [0,2] ; units = 'Per hour'
    nx_pgnet_av.write(conn,name).add_atts_randomly(G,attribute,True,False,att_value_range,functionid_range,units,overwrite=False)
    attribute = 'flow' ; att_value_range = [2,56] ; functionid_range = [0,2] ; units = 'Per hour'
    nx_pgnet_av.write(conn,name).add_atts_randomly(G,attribute,True,True,att_value_range,functionid_range,units,overwrite=False)

if contains_functions == False and contains_atts == True:
    attribute = 'capacity' ;
    for i in range(1, G.number_of_nodes()+1):
        functionid = random.randint(0,2)
        nx_pgnet_av.table_sql(conn,name).update_node_functionid(attribute,functionid,i)
    for i in range (1, G.number_of_edges()+1):
        functionid = random.randint(0,2)
        nx_pgnet_av.table_sql(conn,name).update_edge_functionid(attribute,functionid,i)

'''-------------pull network from database with attributes and functions----'''
#need to re-establish connection as it does not pick up the addition of a new column
conn = ogr.Open("PG:dbname='_new_schema' host='localhost'port='5433' user='postgres' password='aaSD2011'")
print "Reading network from database. Should contain the units attribute."
print attributes
G = nx_pgnet_av.read(conn,name).read_from_db(attributes)
print "Loaded network. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())
print "---------------------------------------"
print "Writing network back to database."
#contains_atts = write atts from network into database tables (G,atts,contains_atts,contains_funcs,overwrite,srid,directed,multigraph)
result = nx_pgnet_av.write(conn,'test_new_write').write_to_db(G,attributes,True,True, True, 27700, True, False )

if result == False: exit()

print "---------------------------------------"

G = nx_pgnet_av.read(conn,name).read_from_db(None)
print "Loaded written network with no attributes. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())
G.node[1]
G = nx_pgnet_av.read(conn,name).read_from_db(attributes)
print "Loaded written network with attributes. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())
print G.node[1]
print "Number of functions for network number %s." %len(functions)
#update function text and type (set type as none if not changing it)
new_function = 'capacity / flow * 2'
functionid = 2
result = nx_pgnet_av.write(conn,name).update_function(functionid,new_function, None)
if result == False: print "Could not find function with an id of %s in function table." %(functionid)
nx_pgnet_av.read(conn,name).return_network_functions()

