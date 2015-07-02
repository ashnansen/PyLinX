'''
Created on 15.09.2014

@author: Waetzold Plaum

'''

## @package BContainer
# This module contains the core data objekt "BContainer" and directly derived standard classes. They are aimed to build  
# transparent tree structures


import inspect
import threading
from PyQt4 import QtCore


import PyLinXData

## Base class of the B object modell

class BContainer(object):


    ## Constructor
    
    def __init__(self, name = u"<no Name>", parent = None):

        # Element for saving the main or global information ot the knot
        self.__Head = None
        # Dict of Elements indexed by "name"
        self.__Body = {}
        # reference to the root knot
        self.__parent = parent

        self.__Attributes                = {} 
        self.__Attributes[u"Type"]        = 0
        self.__Attributes[u"Name"]        = name
        self.__Attributes[u"DisplayName"] = name

       
    ## Method for deleting BContainers    
    
    def delete(self, name):
        
        if name in self.__Body:
            obj = self.__Body.pop(name)
            keys = obj.__Body.keys()
            for childKey in keys:
                obj.delete(childKey)
            del obj


    ## Method that gets the value of an label
    
    def get(self, attr):
        return self.__Attributes.get(attr)   

           
    def getb(self,name):
        return self.__Body.get(name)
        
    ## Method that gets the head of a container
     
    def geth(self):
        return self.__Head
    
    ## Method that returns the parent element
    
    def getParent(self):
        return self.__parent
    
    def getRoot(self):
        if self.__parent == None:
            return self
        else:
            return self.__parent.getRoot()
    
    ## Method that returns True if the attribute exists
    
    def isAttr(self, attr):
        #return self.__Attributes.get(attr) is True
        return attr in self.__Attributes
    
    ## Method that returns true, if an attribute exists and has the value "True", otherwise it returns "False" 

    def isAttrTrue(self, attr):
        return self.__Attributes.get(attr) is True
#         if self.__Attributes.get(attr) is True:
#             if self.__Attributes[attr] == True:
#                 return True
#             else:
#                 return False
#         else:
#             return False
        
    ## Method that determines if there exists an element for a certain key
    
    def isInBody(self, key):
        return key in self.__Body  
    
    ## Method that gets all attributes
    
    def getAttrs(self):
        
        return self.__Attributes.keys()
     
    ## Method that gets all keys of the child elements
    
    def getChildKeys(self):
        
        return self.__Body.keys()
    
    ## This method pastes an object into another one.
                
    def paste(self, obj, name = None, bForceOverwrite = False, pathkey = None, bHashById = False):
        
        types = inspect.getmro(type(obj))
        if BContainer in types:
            if bHashById == True:
                 
                if PyLinXData.PyLinXDataObjects.PX_IdObject in types:                    
                    key = obj.ID
                else:
                    key = obj.get(u"Name")
            else:
                key = obj.get(u"Name")
        else:
            if name == None:
                # TODO: Error-Handling has to be implemented 
                print "Error BContainer.py: No key for paste-function!"
                return
            
        if key in self.__Body.keys():
            if bForceOverwrite:
                self.__Body[key] = obj
                obj.__parent = self                
            else:
                '''
                If an object with corresponding Name exists, then an error message should be returned
                TODO: Has to be impemented
                '''
                pass
        
        else:
            self.__Body[key] = obj
            types = inspect.getmro(type(obj))
            if(BContainer in types):
                obj.__parent = self

    
    ## function to execite a function recursively on special typesy
    
    def recur(self, typeinfo, strFunction, tupleArgs, bSubTypes = False):
        
        
        
        if bSubTypes:
            types = inspect.getmro(type(self))
        else:
            types = [type(self)]
        bCallFunction = (typeinfo in types)

        #print "typeinfo: ", typeinfo 
        if bCallFunction:
            if len(tupleArgs) > 0:
                strExec = u"self." + strFunction + u"(" + u"*tupleArgs" + u")"
            else:
                strExec = u"self." + strFunction + u"()"
            #print "-> RECUR typeInfo: ", typeinfo, "  strFunction: ", strFunction, "  tupleArgs: ", tupleArgs
            #print "strExec: ", strExec
            exec(strExec)
                
        for key in self.__Body:
            element = self.__Body[key]
            element.recur(typeinfo, strFunction, tupleArgs, bSubTypes)
            

    ##  Method to add or set an attribute
    
    def set(self,  attr, setObj):
        
        try:
            self.__Attributes[attr] = setObj
        except:
            print "type(self): ",  type(self)
            raise
   

class BList(BContainer, list):
    
    def __init__(self, *args):
        
        list.__init__(self, *args)
        BContainer.__init__(self, *args)




class BDict(BContainer, dict):
    
    def __init__(self, *args):
        
        dict.__init__(self, *args)
        BContainer.__init__(self, *args)

