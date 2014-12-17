'''
Created on 15.09.2014

@author: Waetzold Plaum

'''

## @package BContainer
# This module contains the core data objekt "BContainer" and directly derived standard classes. They are aimed to build  
# transparent tree structures


import inspect
import PyLinXData


#import PyLinXDataObjects

## Base class of the B object modell

class BContainer(object):


    ## Constructor
    
    def __init__(self, name = "<no Name>", parent = None):

        # Element for saving the main or global information ot the knot
        self.__Head = None
        # Dict of Elements indexed by "name"
        self.__Body = {}
        # reference to the root knot
        self.__parent = parent

        self.__Attributes                               = {} 
        self.__Attributes['Type']                       = 0
        self.__Attributes['Name']                       = name
        self.__Attributes['DisplayName']                = name
  
       
    ## Method for deleting BContainers    
    
    def delete(self, name):
        
        if name in self.__Body.keys():
            obj = self.__Body.pop(name)
            del obj


    ## Method that gets the value of an label
    
    def get(self, attr):    
        if attr in self.__Attributes.keys():
            #print "> ", attr
            return self.__Attributes[attr]
        else:
            return None

    
    ## Method that gets elements of the body of a container
           
    def getb(self,name):
        if name in self.__Body.keys():
            return self.__Body[name]
        else:
            return None
        
    ## Method that gets the head of a container
     
    def geth(self):
        return self.__Head
    
    ## Method that returns the parent element
    
    def getParent(self):
        return self.__parent
    
    ## Method that returns True if the attribute exists
    
    def isAttr(self, attr):
        if attr in self.__Attributes.keys():
            return True
        else:
            return False
    
    ## Method that returns true, if an attribute exists and has the value "True", otherwise it returns "False" 

    def isAttrTrue(self, attr):
        if attr in self.__Attributes.keys():
            if self.__Attributes[attr] == True:
                return True
            else:
                return False
        else:
            return False
        
    ## Method that determines if there exists an element for a certain key
    
    def isInBody(self, key):
        if key in self.__Body.keys():
            return True
        else:
            return False
    
    ## Method that gets all attributes
    
    def getAttrs(self):
        
        return self.__Attributes.keys()
    
    
    ## Method that gets all keys of the child elements
    
    def getChildKeys(self):
        
        return self.__Body.keys()
    
    ## This method pastes an object into another one.
                
    def paste(self, obj, name = None, bForceOverwrite = False, pathkey = None, bHashById = False):
        
        types = inspect.getmro(type(obj))
        #print "---> ", types
        if BContainer in types:
            if bHashById == True:
                 
                if PyLinXData.PyLinXDataObjects.PX_PlotableObject in types:                    
                    key = obj.ID
                else:
                    key = obj.get("Name")
            else:
                key = obj.get("Name")
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


    ##  Method to add or set an attribute
    
    def set(self,  attr, setObj):
        
        self.__Attributes[attr] = setObj    
