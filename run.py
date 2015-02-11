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
conn = ogr.Open("PG:dbname='_new_schema_SB' host='localhost'port='5433' user='postgres' password='aaSD2011'")
sql = ("SELECT np_delete_all_tables('%s');" %(name))
conn.ExecuteSQL(sql)

'''-------------create networkx instance from database----------------------'''
#G = nx_pg.read_pg(conn, 'sample_lines','sample_points')
G = nx_pg.read_pg(conn, 'sample_lines_atts','sample_points_atts')
#G = nx_pg.read_pg(conn, 'tyne_wear_m_a_b') #no attributes added at this time
contains_atts = True; contains_functions = False

'''-------------add network to db with specified attributes-----------------'''
#attributes = None
attributes = [{'flow':False, 'capacity':True, 'storage':False, 'resistance':False, 'latency':False},
              {'flow':False, 'capacity':True, 'length':False, 'resistance':False, 'stacking':False}]
result = nx_pgnet_av.write(conn,name).write_to_db(G,attributes, contains_atts, contains_functions)
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
    attribute = 'flow' ; att_value_range = [5,25] ; functionid_range = [0,2]
    nx_pgnet_av.write(conn,name).add_atts_randomly(G,attribute,att_value_range,functionid_range,overwrite=False)
    attribute = 'capacity' ; att_value_range = [2,56] ; functionid_range = [0,2]
    nx_pgnet_av.write(conn,name).add_atts_randomly(G,attribute,att_value_range,functionid_range,overwrite=False)
if contains_functions == False and contains_atts == True:
    attribute = 'capacity' ;
    for i in range(1, G.number_of_nodes()+1):
        functionid = random.randint(0,2)
        nx_pgnet_av.table_sql(conn,name).update_node_functionid(attribute,functionid,i)
    for i in range (1, G.number_of_edges()+1):
        functionid = random.randint(0,2)
        nx_pgnet_av.table_sql(conn,name).update_edge_functionid(attribute,functionid,i)
        
'''-------------pull network from database with attributes and functions----'''
print 'pulling network from db'
#need to re-estacblish connection as it does not pick up the addition of a new column
conn = ogr.Open("PG:dbname='_new_schema_SB' host='localhost'port='5433' user='postgres' password='aaSD2011'")

G = nx_pgnet_av.read(conn,name).read_from_db(attributes)
print "Loaded network. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())
print "---------------------------------------"

#contains_atts = write atts from network into database tables
result = nx_pgnet_av.write(conn,'test_new_write').write_to_db(G,attributes,contains_atts = True, contains_functions = True )
if result == False: exit()
else: print "Written network back to database with attributes saved to tables."

print "---------------------------------------"

G = nx_pgnet_av.read(conn,name).read_from_db(None)
print "Loaded written network with no attributes. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())

G = nx_pgnet_av.read(conn,name).read_from_db(attributes)
print "Loaded written network with attributes. Has %s nodes and %s edges." %(G.number_of_nodes(), G.number_of_edges())
#print G.node[1]
functions = nx_pgnet_av.read(conn,name).return_network_functions()
print "Number of functions for network number %s." %len(functions)
#update function text and type (set type as none if not changing it)
new_function = 'capacity / flow * 2'
functionid = 2
result = nx_pgnet_av.write(conn,name).update_function(functionid,new_function, None)
if result == False: print "Could not find function with an id of %s in function table." %(functionid)
nx_pgnet_av.read(conn,name).return_network_functions()

