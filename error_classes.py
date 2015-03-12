# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:14:54 2015

@author: a8243587
"""

class GeneralError(Exception):
    '''Non-descript error'''
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class DatabaseError(Exception):
    '''Error in database'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 
  
class NetworkError(Exception):
    '''Problem with network'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
        
        
        
        