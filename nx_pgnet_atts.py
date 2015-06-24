# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 17:12:05 2015

@author: Craig
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 08:37:39 2014

@author: a8243587
"""

import networkx as nx
import sys
sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
import nx_pgnet,nx_pg
import random
import error_classes


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
    
    def create_units_table(self,):
        '''
        '''
        sql = ("SELECT * FROM np_create_units_table ('%s');" % (self.prefix))
        result = None
        for row in self.conn.ExecuteSQL(sql):
            
            result = row.np_create_units_table
        
        return result
        
    def create_role_table(self,):
        '''
        '''
        sql = ("SELECT * FROM np_create_role_table ('%s');" % (self.prefix))
        result = None
        for row in self.conn.ExecuteSQL(sql):
            
            result = row.np_create_role_table
            
        return result
        
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

    def update_node_attributes(self,attribute,att_value,functionid,unit_id,nodeid,overwrite):
        '''
        Update the attribute of a node in the specified attribute table.
        '''        
    
        sql = ("SELECT * FROM np_add_node_attribute('%s','%s',%s,%s,%s,%s,%s)" %(self.prefix,attribute,att_value,functionid,unit_id,nodeid,overwrite))
        
        result = True
        for row in self.conn.ExecuteSQL(sql):
              result = row.np_add_node_attribute
     
        try:
            sql = '''
                  UPDATE "%s" 
                  SET "UnitID" = %s
                  '''%(self.prefix+'_Nodes_'+attribute,unit_id)
            self.conn.ExecuteSQL(sql)
        except:
            pass
        return result
    
    def update_node_attributes2(self,attribute,att_value,functionid,unitid,nodeid,overwrite):
        '''
        This is used as there is an as yet unidentified issue with the above 
        method (update_node_attributes).
        '''
        if type(att_value) != tuple:
            if attribute == 'buffer':
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, %s = %s, "UnitID" = %s 
                      WHERE "NodeID" = %s
                      ''' %(self.prefix+"_Nodes_"+attribute,functionid,'storage',att_value,unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
            elif attribute == 'flow':
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "NodeID" = %s
                      ''' %(self.prefix+"_Nodes_"+attribute,functionid,'flow_capacity',att_value,unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
            else:
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "NodeID" = %s
                      ''' %(self.prefix+"_Nodes_"+attribute,functionid,attribute,att_value,unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
        elif len(att_value) == 2:
            if attribute == 'buffer':
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "NodeID" = %s
                      ''' %(self.prefix+"_Nodes_"+attribute,functionid,'storage',att_value[0],'buffer_capacity',att_value[1],unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
            elif attribute == 'flow':
                if att_value[0] == None:att_value = (0,att_value[1])
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "NodeID" = %s
                      ''' %(self.prefix+"_Nodes_"+attribute,functionid,attribute,att_value[0],'flow_capacity',att_value[1],unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
        return result

    def update_edge_attributes(self,attribute,att_value,functionid,unitid,edgeid,overwrite):
        '''
        Update the attribute of an edge in the specified attribute table.
        '''
            
        sql = ("SELECT * FROM np_add_edge_attribute('%s','%s',%s,%s,%s,%s,%s)" %(self.prefix,attribute,att_value,functionid,unitid,edgeid,overwrite))
        
        result = True
    
        for row in self.conn.ExecuteSQL(sql):
              result = row.np_add_edge_attribute
    
        try:
            sql = '''
                  UPDATE "%s" 
                  SET "UnitID" = %s
                  '''%(self.prefix+'_Edges_'+attribute,unitid)
            self.conn.ExecuteSQL(sql)
        except:
            pass
        
        return result
    
    def update_edge_attributes2(self,attribute,att_value,functionid,unitid,nodeid,overwrite):
        '''
        This is used as there is an as yet unidentified issue with the above 
        method (update_node_attributes).
        '''
        if type(att_value) != tuple:
            if attribute == 'flow':
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "EdgeID" = %s
                      ''' %(self.prefix+"_Edges_"+attribute,functionid,'flow_capacity',att_value,unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
            else:
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "EdgeID" = %s
                      ''' %(self.prefix+"_Edges_"+attribute,functionid,attribute,att_value,unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
        elif len(att_value) == 2:
            if attribute == 'flow':
                if att_value[0] == None:att_value = (0,att_value[1])
                sql = '''
                      UPDATE "%s" 
                      SET "FunctionID" = %s, "%s" = %s, "%s" = %s, "UnitID" = %s 
                      WHERE "EdgeID" = %s
                      ''' %(self.prefix+"_Edges_"+attribute,functionid,attribute,att_value[0],'flow_capacity',att_value[1],unitid,nodeid)
                result = self.conn.ExecuteSQL(sql)
        return result
        
    def update_function(self,functionid,function_text,function_type):
        '''
        '''
        if function_type == None:
            sql = 'UPDATE "%s" SET "function" = %s WHERE "FunctionID" = %s' %(self.prefix+"_Functions",function_text,functionid)
        else:
            function_type = "'" + function_type + "'"
            sql = 'UPDATE "%s" SET "function" = %s, "type" = %s WHERE "FunctionID" = %s' %(self.prefix+"_Functions",function_text,function_type,functionid)
        
        self.conn.ExecuteSQL(sql)

        return
    
    def update_node_functionid(self,attribute,functionid,nodeid):
        '''
        Updaets the functionid for a node in the network.
        '''        
        sql = 'UPDATE "%s" SET "FunctionID" = %s WHERE "NodeID" = %s' %(self.prefix+"_Nodes_"+attribute,functionid,nodeid)
        self.conn.ExecuteSQL(sql)
        
        return
        
    def update_edge_functionid(self,attribute,functionid,edgeid):
        '''
        Updates the function id of an edge in the network.
        '''
        sql = 'UPDATE "%s" SET "FunctionID" = %s WHERE "EdgeID" = %s' %(self.prefix+"_Edges_"+attribute,functionid,edgeid)
        self.conn.ExecuteSQL(sql)
        
        return
    
    def get_function_ids(self,function_table):
        '''
        Returns a list of the function ids which already exist in the function 
        table.
        '''
        functionids = []
        
        sql = "SELECT * FROM %s" %(function_table)
        try:
            result = self.conn.ExecuteSQL(sql)
            for row in result:
                #adds the function id to a list
                functionids.append(row['FunctionID'])
        except: 
            functionids = False
        
        return functionids
    
    def get_functionid(self,function_table,function):
        '''
        Returns the id of a function if in the function tabale. If not returns 
        a blank id('').
        '''
        #check if function exists in function table
        sql = "SELECT * FROM %s WHERE function = '%s'" %(function_table,function)
                           
        result = self.conn.ExecuteSQL(sql)
        functionid = '' #default value, over written if function found in table
                                
        for row in result:
            #if function exists get id
            functionid = row["FunctionID"]
            
        return functionid
        
    def get_node_data(self,key,node_table,function_table,att_table):
        '''
        Returns a list of data with each entry being the attributes for a node.
        '''
        if key == 'buffer':
            sql = '''SELECT node_table.*, snc.storage, snc.buffer_capacity,snc.function, snc."UnitID" 
                     FROM "%s" AS node_table 
                     JOIN (SELECT * 
                           FROM "%s" AS function_table 
                           JOIN "%s" snc 
                           ON function_table."FunctionID" = snc."FunctionID") AS snc 
                     ON node_table."NodeID" = snc."NodeID"''' %(node_table,function_table,att_table)
            result = self.conn.ExecuteSQL(sql)
        elif key == 'flow':
            sql = '''SELECT node_table.*, snc.flow, snc.flow_capacity,snc.function, snc."UnitID" 
                     FROM "%s" AS node_table 
                     JOIN (SELECT * 
                           FROM "%s" AS function_table 
                           JOIN "%s" snc 
                           ON function_table."FunctionID" = snc."FunctionID") AS snc 
                     ON node_table."NodeID" = snc."NodeID"''' %(node_table,function_table,att_table)
            result = self.conn.ExecuteSQL(sql)
        else:
            sql = '''SELECT node_table.*, snc.%s, snc.function, snc."UnitID" 
                     FROM "%s" AS node_table 
                     JOIN (SELECT * 
                           FROM "%s" AS function_table 
                           JOIN "%s" snc 
                           ON function_table."FunctionID" = snc."FunctionID") AS snc 
                     ON node_table."NodeID" = snc."NodeID"''' %(key,node_table,function_table,att_table)
            result = self.conn.ExecuteSQL(sql)
        return result
        
    def get_edge_data(self,key,edge_table,function_table,att_table):
        '''
        Returns a list of data with each entry being the attributes for a edge.
        '''        

        sql = 'SELECT edge_table.*, snf.%s, snf.function, snf."UnitID" FROM "%s" AS edge_table JOIN (SELECT * FROM "%s" AS function_table JOIN "%s" snf ON function_table."FunctionID" = snf."FunctionID") AS snf ON edge_table."EdgeID" = snf."EdgeID"'%(key,edge_table,function_table,att_table)
        result = self.conn.ExecuteSQL(sql)
        
        return result

    def get_units_dict(self,):
        '''
        Returns a dict of entries in the units table.
        '''
        sql = '''
              SELECT * FROM "%s"
              ''' %(self.prefix+'_Units')
        result = self.conn.ExecuteSQL(sql)
        
        unit_dt = {}
        for row in result:
            unit_dt[str(row['UnitID'])] = row['unit']
        
        return unit_dt
    
    def get_role_dict(self,):
        '''
        '''
        #return a dict of node roles
        sql = '''
            SELECT * FROM "%s"
            ''' %(self.prefix+'_Roles')
        result = self.conn.ExecuteSQL(sql)

        role_dt = {}
        for row in result:
            role_dt[str(row['RoleID'])] = row['type']
        
        return role_dt
        
    def get_roleid(self,role):
        '''
        '''
        sql = '''
              SELECT * FROM "%s"
              WHERE type = '%s'
              ''' %(self.prefix+'_Roles',role)
        result = self.conn.ExecuteSQL(sql)
        add_to_table = True
        for row in result: add_to_table = False
        if add_to_table == True:
            #adds role into role table
            sql = '''
                  INSERT INTO "%s" (type)
                  VALUES ('%s');
                  ''' %(self.prefix+'_Roles',role)
            self.conn.ExecuteSQL(sql)
        #gets id of role
        sql = '''
              SELECT "RoleID"
              FROM "%s"
              WHERE type = '%s';
              ''' %(self.prefix+'_Roles',role)
        result = self.conn.ExecuteSQL(sql)
        for row in result: role_id = row['RoleID']

        return role_id
        
    def get_unitid(self,unit):
        '''
        '''
        unit_id = None
        
        #for unit, check if in units table
        sql=''' SELECT * FROM "%s" WHERE unit = '%s';''' %(self.prefix+'_Units',unit)
        result=self.conn.ExecuteSQL(sql)
        #get unit_id if in row returned
        for row in result:
            try: unit_id = row['UnitID']
            except: pass
            
        #if unit not in table, add and get id
        if unit_id == None:
            #insert units; get id
            sql='''
                INSERT INTO "%s" (unit)
                VALUES('%s');
                
                SELECT "UnitID"
                FROM "%s"
                WHERE unit = '%s';
                ''' %(self.prefix+'_Units',unit,self.prefix+'_Units',unit)
            result = self.conn.ExecuteSQL(sql)
            for row in result: unit_id = row['UnitID']
        
        return unit_id
    
    def check_role_column(self,):
        '''
        '''
        sql = '''
              SELECT * FROM "%s"  
              ''' %(self.prefix+'_Nodes')
        result = self.conn.ExecuteSQL(sql)
        dont_add = False
        for row in result: 
            for key in row.keys():
                if key == 'role_id':
                    dont_add = True
        if dont_add == False:
            #add new role id column to node table
            sql = '''
                  ALTER TABLE "%s"  
                  ADD "role_id" integer
                  ''' %(self.prefix+'_Nodes')
            self.conn.ExecuteSQL(sql)
        
        return
        
class write:

    def __init__(self, db_conn, prefix):
        '''Setup connection to be inherited by methods.
		
        db_conn - ogr connection
		
        '''
        self.conn = db_conn
        if self.conn == None:
            raise error_classes.GeneralError('No connection to database!')
            
        self.prefix = prefix
            
    def write_to_db(self,G,attributes,contains_atts,contains_functions,overwrite,srid,directed,multigraph):
        '''
        Writes a networkx instance of a network to a postgres/postgis network 
        database schema. Uses the nx_pgnet library for the mian functionality, 
        then facilitates the building of the extra tables for the node and egde 
        attributes and relevant functions.
        '''
        try:
            print 'before contains atts code:',G.node[1].keys()
        except:
            pass
        #check here for attribute headings being in network
        if contains_atts == False:
            #if att columns exist in the network rename columns (appends'_1')
            for key in attributes[0].keys():
                if attributes[0][key] == True: 
                    print "Renaming column.",key
                    table_sql(self.conn,self.prefix).rename_node_column(key)                    
            for key in attributes[1].keys():
                if attributes[1][key] == True: 
                    print "Renaming column.",key
                    table_sql(self.conn,self.prefix).rename_edge_column(key) 
        
        Gwrite = G.copy()
        #write network to database -this is where it goes wrong. It writes out 
        #to the database all atts into the nodes table, but as the connection
        #is not refreshed, returns on read those values which were in the node 
        #table beforehand. Same applies to edges.
        nx_pgnet.write(self.conn).pgnet(Gwrite, self.prefix, srid, overwrite, directed, multigraph)
        print G.nodes()
        print G.edges()
        exit()
        print 'issue is that nodes are being reassigned an id which is different and the edges are not being given this id, thus creating a different network.'
        for nd in G.nodes():
            print G.node[nd]['id']
            for eg in G.edges():
                print G.edge[eg[0]][eg[1]]
        exit()
        Gwrite = None
        #pull back so we have edge id's which are easier to work with
        #G = nx_pgnet.read(self.conn).pgnet(self.prefix) #this is causing issues with attributes - not 100% why
        
        #create anscilary tables
        table_sql(self.conn,self.prefix).create_units_table()
        table_sql(self.conn,self.prefix).create_role_table()
        #checks built network for role attribute and populates role table and nodes table appropriately
        result = self.populate_roles(G) #table_sql(self.conn,self.prefix).populate_role_table()
        
        if attributes != None:
    
            #create table to store functions
            table_sql(self.conn,self.prefix).create_function_table()
            
            #create attribute tables for nodes
            for key in attributes[0].keys():
                
                #if attribute is set as True
                if attributes[0][key] == True:
                    #create attribute table with all nodes within
                    result = table_sql(self.conn,self.prefix).create_node_attribute_table(key)
                    if result <> 1: raise error_classes.GeneralError("Could not create %s attribute table." %(key))
                    
            #create attribute tables for edges
            for key in attributes[1].keys():

                #if attribute set as True
                if attributes[1][key] == True:

                    #create attribute table with all edges within
                    result = table_sql(self.conn,self.prefix).create_edge_attribute_table(key)
                    if result <> 1: raise error_classes.GeneralError("Could not create %s attribute table." %(key))
                    
            if contains_atts == False:
                #if att columns exist in the network rename columns
                for key in attributes[0].keys():
                    if attributes[0][key] == True: table_sql(self.conn,self.prefix).rename_node_column(key)                    
                for key in attributes[1].keys():
                    if attributes[1][key] == True: table_sql(self.conn,self.prefix).rename_edge_column(key)
            else:
                # add the attributes in the network to the databse tables

                #define function table                            
                function_table = '"'+self.prefix + '_Functions"'
                
                #return a list of function id's
                table_functionids = table_sql(self.conn, self.prefix).get_function_ids(function_table)
               
                #if table empty, use an id of zero
                if table_functionids == []:
                    next_functionid = 0
                else:
                    #if values in table, use value higher than list max
                    next_functionid = max(table_functionids) + 1

                #check if all attributes exist which have been set as True
                for key in attributes[0].keys():
                    if attributes[0][key] == True:
                        for nd in G.nodes():
                            #check attribute available for node
                            try:
                                if key == 'buffer':
                                    att_value = G.node[nd]['storage']
                                else:
                                    att_value = G.node[nd][key]
                            except:
                                raise error_classes.GeneralError("Warning! At least one of the nodes does not have a specified attribute, %s, attached to it. Is the contains_atts variable set correctly?" %(key))
                            #check attribute function available for node
                            if contains_functions == True:
                                try:
                                    function = G.node[nd][key+"_function"]
                                except:
                                    raise error_classes.GeneralError("Warning! At least one of the nodes does not have a specified attribute, %s, attached to it. Is the contains_functions variable set correctly?" %(key+"_function"))
                
                for key in attributes[1].keys():
                    if attributes[1][key] == True:
                        for edg in G.edges():
                            edge = G.edge[edg[0]][edg[1]]
                            #check attribute available in edge
                            try:
                                att_value = edge[key]
                            except:
                                raise error_classes.GeneralError("Warning! At least one of the edges does not have a specified attribute, %s, attached to it." %(key))
                            #check attribute function in edge
                            if contains_functions == True:
                                try:
                                    function = edge[key+"_function"]
                                except:
                                    raise error_classes.GeneralError("Warning! At least one of the edges does not have a specified attribute, %s, attached to it." %(key+"_function"))
                                
                #check if node attribute exists and copy to table if so
                for key in attributes[0].keys():
                    #needs to also write functions to table, first checking if 
                    #it is already there. If get functionid, if not add.
                    if attributes[0][key] == True:
                        
                        for nd in G.nodes():
                            
                            #get the attribute value
                            if key == 'buffer': att_value = G.node[nd]['storage'],G.node[nd]['buffer_capacity']
                            elif key == 'flow': att_value = G.node[nd]['flow'],G.node[nd]['flow_capacity']
                            else: att_value = G.node[nd][key]

                            #get unit
                            unit = G.node[nd][key+'_unit']
                            unit_id = None
                            
                            #get unit id if in table
                            sql='''
                                SELECT * FROM "%s" WHERE unit = '%s'
                                '''%(self.prefix+'_Units',unit)
                            result = self.conn.ExecuteSQL(sql)
                            for row in result:
                                for k in row.keys():
                                    if k == 'UnitID':
                                        unit_id = row[k]
                            
                            if unit_id == None:
                                #add unit to table
                                sql='''
                                    INSERT INTO "%s" (unit) VALUES ('%s') '''%(self.prefix+'_Units',unit)
                                self.conn.ExecuteSQL(sql)
                                #get unit id
                                sql='''
                                    SELECT * FROM "%s" WHERE unit = '%s' '''%(self.prefix+'_Units',unit)
                                result = self.conn.ExecuteSQL(sql)
                                for row in result:
                                    unit_id = row['UnitID']
                            
                            if unit_id==None: print "Error adding unit to table/getting id.";exit()
                            
                            #get the function if set as existing
                            if contains_functions == True:
                                function = G.node[nd][key+"_function"]
                            else:
                                #if function not an attribute
                                function = False
                            
                            #if a function exists add and get id
                            if function != False:
                                
                                #get id of function if exists else = ''
                                functionid = table_sql(self.conn,self.prefix).get_functionid(function_table,function)
                                
                                #if the function id has not been found, add function to function table
                                if functionid == '':
                                    #decalare the type as unknown/unspecified                                    
                                    function_type = "unspecified"
                                    
                                    #add function to function table
                                    result = self.add_functions([[function_type,function,next_functionid]])
                                    if result == False:
                                        raise error_classes.DatabaseError("Failed to add function with id %s!" %(next_functionid))
                                    else:
                                        functionid = next_functionid
                                        next_functionid += 1
                                                               
                                #update attribute table with att value and function id
                                if att_value != False and function != False and functionid != '':
                                    #result = table_sql(self.conn,self.prefix).update_node_attributes(key,att_value,functionid,nd,overwrite=False)
                                    result = table_sql(self.conn,self.prefix).update_node_attributes2(key,att_value,functionid,unit_id,nd,overwrite=False)
                                    if result == False:
                                        raise error_classes.DatabaseError("Could not update node attributes for node %s." %(nd))
                                    else:
                                        pass
                                else:
                                    raise error_classes.DatabaseError("Error! Attribute value variable or function variable is false or function id variable is blank.")
                            else:
                                #don't add a function id
                                pass
                                                                
                #check if edge attribute exists and copy to table if so
                for key in attributes[1].keys():
                    if attributes[1][key] == True:
                        #loop through edges
                        for edg in G.edges():
                            edge = G.edge[edg[0]][edg[1]]
       
                            #get attribute value
                            if key == 'flow':
                                att_value = edge[key],edge['flow_capacity']
                            else:
                                att_value = edge[key]
                            
                            #get unit
                            unit = G.node[nd][key+'_unit']
                            unit_id = None
                            
                            #get unit id if in table
                            sql='''
                                SELECT * FROM "%s" WHERE unit = '%s'
                                '''%(self.prefix+'_Units',unit)
                            result = self.conn.ExecuteSQL(sql)
                            for row in result:
                                for k in row.keys():
                                    if k == 'UnitID':
                                        unit_id = row[k]
                            
                            if unit_id == None:
                                #add unit to table
                                sql='''
                                    INSERT INTO "%s" (unit) VALUES ('%s') '''%(self.prefix+'_Units',unit)
                                self.conn.ExecuteSQL(sql)
                                #get unit id
                                sql='''
                                    SELECT * FROM "%s" WHERE unit = '%s' '''%(self.prefix+'_Units',unit)
                                result = self.conn.ExecuteSQL(sql)
                                for row in result:
                                    unit_id = row['UnitID']
                            
                            if unit_id==None: print "Error adding unit to table/getting id.";exit()
                            
                            #get function
                            if contains_functions == True:
                                function = edge[key+"_function"]
                            else:
                                function = False
                            
                            #if a function exists get function id and update table
                            if function != False:

                                function_table = '"'+self.prefix + '_Functions"'
                                functionid = table_sql(self.conn,self.prefix).get_functionid(function_table,function)
                                
                                if functionid == '':
                                    #add function to function table, find a function id
                                    
                                    #as not stored in the network we don't know the type
                                    function_type = "unspesified"
                                    
                                    #add function to table
                                    result = self.add_functions((function_type,function,next_functionid))
                                    if result == False:
                                        raise error_classes.DatabaseError("Failed to add function with id %s!" %(next_functionid))
                                    else:
                                        functionid = next_functionid
                                        next_functionid += 1
                                if att_value != False and functionid != '':                            
                                    #updates the edge attribute table - uses edge id and function id
                                    result = table_sql(self.conn,self.prefix).update_edge_attributes2(key,att_value,functionid,unit_id,edge["EdgeID"],overwrite=False)
                            
                            #if no function exists
                            else:  
                                #leave function id blank as nothing specified
                                pass
                    else: pass
                
                
    def populate_roles(self, G):
        '''
        '''
        role_att=False; roles=[]
        #check node table if role column exists
        sql = '''SELECT * FROM "%s"''' %(self.prefix+'_Nodes')
        result = self.conn.ExecuteSQL(sql)
        for row in result:
            if role_att==False:
                #check if a role attribute exists
                for key in row.keys():
                    if key=='role': 
                        role_att=True
                        #check if role id column already exists -add if needed
                        table_sql(self.conn,self.prefix).check_role_column()
                        
            if role_att==True:
                #check if role already in role table
                role = row['role']
                add_role=True
                for text in roles:
                    if role == text:
                        role=False
                        break
                if add_role==True:
                    #check if role already exists in role table
                    role_id = table_sql(self.conn,self.prefix).get_roleid(role)
                
                    #add id to all nodes which have the same type
                    sql = '''
                          UPDATE "%s"
                          SET role_id = '%s'
                          WHERE role = '%s';
                          ''' %(self.prefix+'_Nodes',role_id,role)
                    self.conn.ExecuteSQL(sql)
                    
        #at end remove original role column
        sql = '''
              ALTER TABLE "%s"
              DROP COLUMN "%s"
              ''' %(self.prefix+'_Nodes','role')
        #self.conn.ExecuteSQL(sql)
        return True
        
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
        function_text = "'" + function_text + "'"
        
        #to check the function exists in the table
        sql = 'SELECT * FROM "%s"' %(self.prefix+"_Functions")
        result = self.conn.ExecuteSQL(sql)
        
        for row in result:
            if row["FunctionID"] == functionid:
                result = table_sql(self.conn,self.prefix).update_function(functionid,function_text,function_type)
            else: pass

        return True
        
    def add_atts_randomly(self,G,attribute,nodes,edges,att_value_range,functionid_range,units,overwrite):
        '''
        Adds attributes to nodes and edges given an attribute name, a range for
        random values, function ids and a unit string.
        '''
        if nodes == True:
            #loop through all the nodes
            for i in range(1, G.number_of_nodes()+1):
                #get random function id
                functionid = random.randint(functionid_range[0],functionid_range[1])
                #get random attribute value
                att_value = random.randint(att_value_range[0],att_value_range[1])
                #get unit id. if not in unit table, add
                unit_id = table_sql(self.conn,self.prefix).get_unitid(units)
                
                #assign random values to node in appropriate attribute table
                result = table_sql(self.conn,self.prefix).update_node_attributes2(attribute,att_value,functionid,unit_id,i,overwrite=False)
                
                #error reporting
                if result == False:
                    functionids = table_sql(self.conn,self.prefix).get_function_ids(self.prefix+"_Functions")
                    if functionids == False:
                        raise error_classes.GeneralError('Error!. Could not get function ids. Check %s_Functions table exists and the specified function with ids are in the table. Also, check "contains_functions" variable is set correctly - False if network does not contain all attribute functions.'%(self.prefix))
                    for _id in functionids:
                        if functionid == _id:
                            functionid_exists = True
                            break
                    if functionid_exists == False:
                        raise error_classes.GeneralError('FunctionID (%s) not recognised. Check function is in %s_Functions table.' %(functionid,self.prefix))
                    else:
                        raise error_classes.GeneralError('Unknown error! Function with an id of %s exists in %s_Functions table but could not be written in the node table.' %(functionid,self.prefix))
                    raise error_classes.GeneralError("SHOULD NOT BE DOING THIS")
                    #sql here to add the function id manually
                    #sql = 'UPDATE "%s" SET "FunctionID" = %s, "%s" = %s WHERE "NodeID" = %s' %(self.prefix+"_Nodes_"+attribute,functionid,attribute,att_value,i)
                    #self.conn.ExecuteSQL(sql)
        
        if edges == True:
            #loop through all edges
            for i in range (1, G.number_of_edges()+1):
                #get random function id
                functionid = random.randint(functionid_range[0],functionid_range[1])
                #get random attribute value
                att_value = random.randint(att_value_range[0],att_value_range[1])
                #get unit id. if not in unit table, add
                unit_id = table_sql(self.conn,self.prefix).get_unitid(units)
                
                #assign random values to edge in appropriate attribute table
                result = table_sql(self.conn,self.prefix).update_edge_attributes(attribute,att_value,functionid,unit_id,i,overwrite=False)
                
                #error reporting
                if result == False: 
                    functionids = table_sql(self.conn,self.prefix).get_function_ids(self.prefix+"_Functions")
                    for _id in functionids:
                        if functionid == _id:
                            functionid_exists = True
                            break
                    if functionid_exists == False:
                        raise error_classes.GeneralError('FunctionID (%s) not recognised. Check function is in %s_Functions table.' %(functionid,self.prefix))
                    else:
                        raise error_classes.GeneralError('Unknown error! Function with an id of %s exists in %s_Functions table but could not be written in the edge table.' %(functionid,self.prefix))
    
        
class read:
    def __init__(self, db_conn, name):
        '''Setup connection to be inherited by methods.
		
        db_conn - ogr connection
		
        '''
        self.conn = db_conn
        if self.conn == None:
            raise error_classes.GeneralError('Error. No connection to database!')
            
        self.prefix = name

    def read_from_db(self, attributes):
        '''
        Retrieves the network from the database and builds a networkx instance.
        Initally uses nx_pgnet to build the entwork, then uses a range of 
        functions to pull specific attributes from the database and adds them 
        as attributes of teh nodes and edges.
        '''
        
        try:
            #is the error caused by me renaming the column after the building of the tables????
            G = nx_pgnet.read(self.conn).pgnet(self.prefix)
        except:
            raise error_classes.GeneralError("Error. Could not read %s network. Check contain_atts variable is set correctly." %(self.prefix))
        
        #add role type to G using role id attribute
        #need to check for role attribute and if exists, pull types from role table
        roleid = False
        for node in G.nodes(data=True):
            for key in node[1].keys():
                if key == 'role_id':
                    role_dt = table_sql(self.conn,self.prefix).get_role_dict()
                    roleid = True
                    break
            break
        
        #loop through nodes adding role_type att use role_dt dict and roleid att        
        if roleid == True:
            for node in G.nodes():
                G.node[node]['role_type'] = role_dt[str(G.node[node]['role_id'])]
        
        if attributes != None:
            #check units table and return a dict of units in it
            unit_dt = table_sql(self.conn,self.prefix).get_units_dict()
            
            #check attribute tables exist before trying to retrieve data
            for key in attributes[0].keys():
                if attributes[0][key] == True:
                    result = table_sql(self.conn,self.prefix).check_attribute_table_exists(key,True)
                    if result == False: 
                        raise error_classes.DatabaseError("Error. Table for the '%s' node attribute does not exist. Cancelling network build request." %(key))
            for key in attributes[1].keys():
                if attributes[1][key] == True:
                    result = table_sql(self.conn,self.prefix).check_attribute_table_exists(key,False)
                    if result == False: 
                        raise error_classes.DatabaseError("Table for the '%s' edge attribute does not exist. Cancelling network build request." %(key))
    
            #need to use attributes to get the required data from the database and
            #adds attributes ang thier functions to G
            function_table = self.prefix + "_Functions"
            #nodes
            for key in attributes[0].keys():
                if attributes[0][key] == True:
                    node_table = self.prefix + "_Nodes"
                    att_table = self.prefix + "_Nodes_" + key
                    #get node data for attribute
                    result = table_sql(self.conn,self.prefix).get_node_data(key,node_table,function_table,att_table)
                    for row in result:
                        #using the node pk add to the attributes of the nodes
                        #add to the networkx instance
                        if key == 'buffer':
                            G.node[row["NodeID"]]['storage'] = row['storage']
                            G.node[row["NodeID"]]['buffer_capacity'] = row['buffer_capacity']
                        else:
                            G.node[row["NodeID"]][key] = row[key]
                        G.node[row["NodeID"]][key + "_function"] = row["function"]
                        G.node[row["NodeID"]][key + "_unit"] = unit_dt[str(row["UnitID"])]
                        
            #edges
            for key in attributes[1].keys():
                if attributes[1][key] == True:
                    #get data for attribute
                    edge_table = self.prefix + "_Edges"
                    att_table = self.prefix + "_Edges_" + key
                    result = table_sql(self.conn,self.prefix).get_edge_data(key,edge_table,function_table,att_table)
                    
                    for row in result:
                        #using the node pk add to the attributes of the nodes
                        #add to the networkx instance
                        G.edge[row["Node_F_ID"]][row["Node_T_ID"]][key]=row[key]
                        G.edge[row["Node_F_ID"]][row["Node_T_ID"]][key+"_function"]=row["function"]
                        G.edge[row["Node_F_ID"]][row["Node_T_ID"]][key+"_unit"] = unit_dt[str(row["UnitID"])]
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
            functions.append(row)
        
        return functions   
    