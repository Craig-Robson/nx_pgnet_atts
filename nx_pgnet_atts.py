# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 08:37:39 2014

@author: a8243587
"""

import networkx as nx
import sys, ogr
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
import nx_pgnet,nx_pg
import random



class table_sql:
    def __init__(self, db_conn, name):
        '''Setup connection to be inherited by methods.
		
        db_conn - ogr connection
		
        '''
        self.conn = db_conn
        if self.conn == None:
            #raise Error('No connection to database.')
            print "No connection to databse!"
            exit()
        self.prefix = name
               
    def create_function_table(self,):
        '''
        '''
        sql = ("SELECT * FROM np_create_function_table ('%s');" % (self.prefix))
        result = None
        for row in self.conn.ExecuteSQL(sql):   
    		
             result = row.np_create_function_table
    		
        return result
    
    def create_node_attribute_table(self, attribute):
        '''
    
        '''
        sql = ("SELECT * FROM np_create_node_attribute_table ('%s', '%s');" % (self.prefix, attribute))
    		
        result = None
        for row in self.conn.ExecuteSQL(sql):   
    		
              result = row.np_create_node_attribute_table
    		
        return result
    
    def create_edge_attribute_table(self, attribute):
        '''
                    
        '''
        sql = ("SELECT * FROM np_create_edge_attribute_table ('%s', '%s');" % (self.prefix, attribute))
    		
        result = None
        for row in self.conn.ExecuteSQL(sql):   
    		
              result = row.np_create_edge_attribute_table
    		
        return result
      
      
    def rename_node_column(self, attribute):
        '''
        '''
        sql = ("SELECT * FROM np_rename_node_column('%s','%s')" %(self.prefix, attribute))
        result = None
    
        for row in self.conn.ExecuteSQL(sql):
    
                result = row.np_rename_node_column
                
        return result
        
    def rename_edge_column(self, attribute):
        '''
        '''
        sql = ("SELECT * FROM np_rename_node_column('%s','%s')" %(self.prefix, attribute))
        result = None
    
        for row in self.conn.ExecuteSQL(sql):
    
                result = row.np_rename_node_column
                
        return result

    def check_attribute_table_exists(self, attribute, node_table):
        '''
        '''
        sql = "SELECT np_check_attribute_table_exists('%s','%s',%s)" %(self.prefix,attribute,node_table)
        outcome = True
                
        for row in self.conn.ExecuteSQL(sql):
                        
            outcome = row.np_check_attribute_table_exists

        return outcome

    def update_node_attributes(self,attribute,att_value,functionid,nodeid,overwrite):
        '''
        Update the attribute of a node in the specified attribute table.
        '''        
    
        sql = ("SELECT * FROM np_add_node_attribute('%s','%s',%s,%s,%s,%s)" %(self.prefix,attribute,att_value,functionid,nodeid,overwrite))
        result = True
    
        for row in self.conn.ExecuteSQL(sql):
              result = row.np_add_node_attribute
              
        return result
    
    def update_edge_attributes(self,attribute,att_value,functionid,edgeid,overwrite):
        '''
        Update the attribute of an edge in the specified attribute table.
        '''
            
        sql = ("SELECT * FROM np_add_edge_attribute('%s','%s',%s,%s,%s,%s)" %(self.prefix,attribute,att_value,functionid,edgeid,overwrite))
        result = True
    
        for row in self.conn.ExecuteSQL(sql):
              result = row.np_add_edge_attribute
              
        return result
        
class write:

    def __init__(self, db_conn, prefix):
        '''Setup connection to be inherited by methods.
		
        db_conn - ogr connection
		
        '''
        self.conn = db_conn
        if self.conn == None:
            #raise Error('No connection to database.')
            print "No connection to databse!"
            exit()
        self.prefix = prefix
            
    def write_to_db(self,G,attributes,contains_atts):
        '''
        Writes a networkx instance of a network to a postgres/postgis network 
        database schema. Uses the nx_pgnet library for the mian functionality, 
        then facilitates the building of the extra tables for the node and egde 
        attributes and relevant functions.
        '''

        #write network to database
        nx_pgnet.write(self.conn).pgnet(G, self.prefix, 27700, overwrite=True, directed = False, multigraph = False)
        #pull back so we have edge id's which might be needed later
        G = nx_pgnet.read(self.conn).pgnet(self.prefix) #this is causing issues with attributes - not 100% why
        
        if attributes != None:
    
            #create table to store functions
            table_sql(self.conn,self.prefix).create_function_table()
            
            #create attribute tables for nodes
            for key in attributes[0].keys():
                
                #if attribute is set as True
                if attributes[0][key] == True:
                    
                    #create attribute table with all nodes within
                    result = table_sql(self.conn,self.prefix).create_node_attribute_table(key)
                    if result <> 1: print 'Could not create %s attribute table' %(key); exit()
                    
            #create attribute tables for edges
            for key in attributes[1].keys():

                #if attribute set as True
                if attributes[1][key] == True:

                    #create attribute table with all edges within
                    result = table_sql(self.conn,self.prefix).create_edge_attribute_table(key)
                    if result <> 1: print 'Could not create %s attribute table' %(key); exit()

            if contains_atts == False:
                #if att columns exist in the network rename columns
                for key in attributes[0].keys():
                    if attributes[0][key] == True: table_sql(self.conn,self.prefix).rename_node_column(key)                    
                for key in attributes[1].keys():
                    if attributes[1][key] == True: table_sql(self.conn,self.prefix).rename_edge_column(key)
            else:
                #this is where I need to have functions which add the attributes in the network to the databse tables

                #define function table                            
                function_table = '"'+self.prefix + '_Functions"'
                
                #find a function id
                sql = "SELECT * FROM %s" %(function_table)
                result = self.conn.ExecuteSQL(sql)

                table_functionids = []
                for row in result:
                    #adds the function id to a list
                    table_functionids.append(row['FunctionID'])
               
               #if table empty, use an id of zero
                if table_functionids == []:
                    next_functionid = 0
                else:
                    #if values in table, use value higher than list max
                    next_functionid = max(table_functionids) + 1

                #check if node attribute exists and copy to table if so
                for key in attributes[0].keys():
                    #needs to also write functions to table, first checking if 
                    #it is already there. If get functionid, if not add.
                    if attributes[0][key] == True:
                        print "Found an attriubte to add to tables, %s." %key
                        
                        for nd in G.nodes():
                            
                            att_value = False
                            function = False
                            
                            #check attribute available for node
                            try:
                                att_value = G.node[nd][key]
                            except:
                                print G.node[nd].keys()
                                raise error_class("Warning! The attribute '%s' is not part of node %s. Process canceled." %(key,nd))
                                
                            #check attribute function available for node
                            try:
                                function = G.node[nd][key+"_function"]
                            except:
                                #raise error_class("Warning! The function for the atrribute '%s' is not an attribute in the network. Process canceled."%key)
                                print "Warning! The function for the atrribute '%s' is not an attribute of node %s."%(key,nd)
                            
                            #if a function exists add and get id
                            if function != False:
                                
                                #check if function exists in function table
                                sql = "SELECT * FROM %s WHERE function = '%s'" %(function_table,function)
                           
                                result = self.conn.ExecuteSQL(sql)
                                functionid = ''
                                
                                for row in result:
                                    #if function exists get id
                                    functionid = row["FunctionID"]
                                
                                #if the function id has not been found
                                if functionid == '':
                                    #add function to function table
                                    
                                    function_type = "unspesified"
                                    print function_type
                                    print function
                                    print next_functionid
                                    #add function to function table
                                    result = self.add_functions([[function_type,function,next_functionid]])
                                    if result == False:
                                        print "Failed to add function with id %s!" %(next_functionid)
                                    else:
                                        functionid = next_functionid
                                        next_functionid += 1
                                        
                                #update attribute table with att value and function id
                                if att_value != False and function != False and functionid != '':
                                    result = table_sql(self.conn,self.prefix).update_node_attributes(key,att_value,functionid,nd,overwrite=False)
                                    if result == False:
                                        #raise error_class("Could not update node attributes for node %s." %(nd))
                                        #print "Could not update node attributes for node %s." %(nd)
                                        sql = 'UPDATE "%s" SET "FunctionID" = %s, "%s" = %s WHERE "NodeID" = %s' %(self.prefix+"_Nodes_"+key,functionid,key,att_value,nd)
                                        self.conn.ExecuteSQL(sql)
                                        #exit()

                                    else:
                                        pass
                                else:
                                    raise error_class("Error! Att value or function is false or function id is blank.")
                            else:
                                #update attribute table with attribute value, but with no function id
                                print "No function found so adding an id of 9999 for node %s." %nd
                                functionid = 9999
                                result = table_sql(self.conn,self.prefix).update_node_attributes(key,att_value,functionid,nd,overwrite=False)
                                
                                
                #check if edge attribute exists and copy to table if so
                for key in attributes[1].keys():
                    if attributes[1][key] == True:
                        #loop through edges
                        for edg in G.edges(data=True):
                            edge = G.edge[edg[0]][edg[1]]

                            att_value = False
                            function = False
                            
                            try:
                                att_value = edge[key]
                            except:
                                raise error_class("Warning! Attribute (%s) is not part of the network. Process canceled." %key)
                                #return False
                                                        
                            try:
                                function = edge[key+"_function"]
                            except:
                                #raise error_class("Warning! Atrribute (%s) function is not an attribute in the network. Process canceled." %key)
                                print "Warning! Atrribute (%s) function is not an attribute in the network." %key
                                #return False
                            
                            if function != False:

                                table_p = '"'+self.prefix + '_Functions"'
                                sql = "SELECT * FROM %s WHERE function = '%s'" %(table_p,function)
                           
                                result = self.conn.ExecuteSQL(sql)
                                functionid = ''
                                for row in result:
                                    functionid = row["FunctionID"]
                                
                                if functionid == '':
                                    #add function to function table, find a function id
                                    
                                    #as not stored in the network we don't know the type
                                    function_type = "unspesified"
                                    
                                    #add function to table
                                    result = self.add_functions((function_type,function,next_functionid))
                                    if result == False:
                                        print "Failed to add function with id %s!" %(next_functionid)
                                    else:
                                        functionid = next_functionid
                                        next_functionid += 1
                                if att_value != False and functionid != '':                            
                                    #updates the edge attribute table - uses edge id and function id
                                    result = table_sql(self.conn,self.prefix).update_edge_attributes(key,att_value,functionid,edge["EdgeID"],overwrite=False)
                            else:
                                functionid = 9999
                                #update attribute table with att value only
                                result = table_sql(self.conn,self.prefix).update_edge_attributes(key,att_value,functionid,edge["EdgeID"],overwrite=False)
                               
                    else: pass
                            
    def add_functions(self,functions):
        '''
        Adds a new function to the function table for the specified network.
        '''
        #check function table exists        
        sql = "SELECT * FROM %s" %(self.prefix+"_Functions")        
        try:
            self.conn.ExecuteSQL(sql)
            #if table exists no error
        except:
            #table does not exist - build table
            table_sql(self.conn,self.prefix).create_function_table()
            
        bad_results = 0
        for vals in functions:
            #need to check when loading that all id's are unique
            sql = ("SELECT np_add_function('%s','%s','%s',%s);" %(self.prefix,vals[0],vals[1],vals[2])) #table prefix, type, function, id[pk]
            result = True
            for row in self.conn.ExecuteSQL(sql):
    
                result = row.np_add_function
                
            if result == False:
                bad_results += 1
        if bad_results == 0:
            return True
        else: return False
    
    def update_function(self,functionid,function_text,function_type = None):
        '''
        Updates the function text and the function type for a speified 
        function id with the users inputs.
        '''
        function_text = "'"+function_text+"'"
        
        #to check the function exists in the table
        sql = 'SELECT * FROM "%s"' %(self.prefix+"_Functions")
        result = self.conn.ExecuteSQL(sql)
        
        for row in result:
            if row["FunctionID"] == functionid:
                if function_type == None:
                    sql = 'UPDATE "%s" SET "function" = %s WHERE "FunctionID" = %s' %(self.prefix+"_Functions",function_text,functionid)
                else:
                    function_type = "'"+function_type+"'"
                    sql = 'UPDATE "%s" SET "function" = %s, "type" = %s WHERE "FunctionID" = %s' %(self.prefix+"_Functions",function_text,function_type,functionid)
                
                self.conn.ExecuteSQL(sql)
                return True
            else: pass

        return False
        
    def add_atts_randomly(self,G,attribute,att_value_range,functionid_range,overwrite):
        '''
        '''
        
        for i in range(1, G.number_of_nodes()+1):
            functionid = random.randint(functionid_range[0],functionid_range[1])
            att_value = random.randint(att_value_range[0],att_value_range[1])
            result = table_sql(self.conn,self.prefix).update_node_attributes(attribute,att_value,functionid,i,overwrite=False)
            if result == False:
                print 'FunctionID (%s) not recognised. Check function is in %s_Functions table.' %(functionid,self.prefix)
                #result = self.conn.ExecuteSQL('SELECT * FROM "tyne_wear_m_a_b_Functions"')
                #for row in result:
                #    print row["FunctionID"]
                print '--------------------------------'
                #sql here to addthe function id manually
                sql = 'UPDATE "%s" SET "FunctionID" = %s, "%s" = %s WHERE "NodeID" = %s' %(self.prefix+"_Nodes_"+attribute,functionid,attribute,att_value,i)
                self.conn.ExecuteSQL(sql)
                #exit()
                #it works for edges but not nodes. maybe an error in the database side of the function, or in the node id or something
            
        for i in range (1, G.number_of_edges()+1):
            functionid = random.randint(functionid_range[0],functionid_range[1])
            att_value = random.randint(att_value_range[0],att_value_range[1])
            result = table_sql(self.conn,self.prefix).update_edge_attributes(attribute,att_value,functionid,i,overwrite=False)
            if result == False: print 'FunctionID not recognised. Check function is in %s_Functions table.' %(self.prefix)
    
        
class read:
    def __init__(self, db_conn, name):
        '''Setup connection to be inherited by methods.
		
        db_conn - ogr connection
		
        '''
        self.conn = db_conn
        if self.conn == None:
            #raise Error('No connection to database.')
            print "No connection to databse!"
            exit()
        self.prefix = name

    def read_from_db(self, attributes):
        '''
        Retrieves the network from the database and builds a networkx instance.
        Initally uses nx_pgnet to build the entwork, then uses a range of 
        functions to pull specific attributes from the database and adds them 
        as attributes of teh nodes and edges.
        '''
        G = nx_pgnet.read(self.conn).pgnet(self.prefix)
        
        #check attribute tables exist before trying to retrieve data
        if attributes != None:
            for key in attributes[0].keys():
                if attributes[0][key] == True:
                    result = table_sql(self.conn,self.prefix).check_attribute_table_exists(key,True)
                    if result == False: print "Table for the '%s' node attribute does not exist. Cancelling network build request." %(key); exit()
            for key in attributes[1].keys():
                if attributes[1][key] == True:
                    result = table_sql(self.conn,self.prefix).check_attribute_table_exists(key,False)
                    if result == False: print "Table for the '%s' edge attribute does not exist. Cancelling network build request." %(key); exit()
    
            #need to use attributes to get the required data from the database and
            function_table = self.prefix + "_Functions"
            for key in attributes[0].keys():
                if attributes[0][key] == True:
                    node_table = self.prefix + "_Nodes"
                    att_table = self.prefix + "_Nodes_" + key
                    #get data for attribute
                    sql = 'SELECT node_table.*, snc.%s, snc.function FROM "%s" AS node_table JOIN (SELECT * FROM "%s" AS function_table JOIN "%s" snc ON function_table."FunctionID" = snc."FunctionID") AS snc ON node_table."NodeID" = snc."NodeID"' %(key,node_table,function_table,att_table)
                    result = self.conn.ExecuteSQL(sql)
                    for row in result:
                        #using the node pk add to the attributes of the nodes
                        #add to the networkx instance
                        G.node[row["NodeID"]][key] = row[key]
                        G.node[row["NodeID"]][key + "_function"] = row["function"]
            
            for key in attributes[1].keys():
                if attributes[1][key] == True:
                    #get data for attribute
                    edge_table = self.prefix + "_Edges"
                    att_table = self.prefix + "_Edges_" + key
                    sql = 'SELECT edge_table.*, snf.%s, snf.function FROM "%s" AS edge_table JOIN (SELECT * FROM "%s" AS function_table JOIN "%s" snf ON function_table."FunctionID" = snf."FunctionID") AS snf ON edge_table."EdgeID" = snf."EdgeID"'%(key,edge_table,function_table,att_table)
                    result = self.conn.ExecuteSQL(sql)
                    for row in result:
                        #using the node pk add to the attributes of the nodes
                        #add to the networkx instance
                        G.edge[row["Node_F_ID"]][row["Node_T_ID"]][key]=row[key]
                        G.edge[row["Node_F_ID"]][row["Node_T_ID"]][key+"_function"]=row["function"]
        return G

    def return_network_functions(self,):
        """
        Returns the functins found in the function table for the network.
        """
        functions = []

        sql = 'SELECT * FROM "%s"' %(self.prefix+"_Functions")
        result = self.conn.ExecuteSQL(sql)
        
        #loop though the returned rows
        for row in result:
            #print "Function ID: %s, Function: %s, Function type: %s" %(row["FunctionID"],row["function"],row["type"])
            functions.append(row)
        
        return functions

class error_class(Exception):
    '''
    
    '''
    
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    