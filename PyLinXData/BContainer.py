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
        self.__AttributesVirtual = [u"path"]

        self.__Attributes                 = {} 
        self.__Attributes[u"Type"]        = 0
        self.__Attributes[u"Name"]        = name
        self.__Attributes[u"DisplayName"] = name
        
       
    ## Method to get the attribute of an element uniquely identificied by the value of another attribute
    
    def call(self, attributeKey, value, attrubuteReturn = None):
        listElements = self.getbCond(attributeKey, value, attrubuteReturn)
        if len(listElements) != 1:
            raise Exception("Fatal Error BContainer.call: inconsistent IDs!")
        return listElements[0]
    
    ## Method for deleting BContainers
    
    def delete(self, name):
        
        if name in self.__Body:
            obj = self.__Body.pop(name)
            keys = obj.__Body.keys()
            for childKey in keys:
                obj.delete(childKey)
            del obj

    ## Method that gets the value of an label
    
    def get(self, attr, bComplex = False):
        if attr == u"path":
            return self.__get_path()
        else:
            if bComplex:
                return self.__get_complex(attr)
            else:
                return self.__Attributes[attr]
            
    def __get_complex(self, attr):
        types = inspect.getmro(type(attr))
        if dict in types:
            dictReturn = {}
            for key in attr:
                len_key = len(key)
                if len_key > 0:
                    if key[0] == u"@":
                        childObj = self.getb(key[1:])
                        getDict = attr[key]
                        childObjReturn = childObj.__get_complex(getDict)
                        dictReturn[key] = childObjReturn
                    else:
                        objReturn = self.get(key)
                        dictReturn [key] = objReturn
                else:
                    raise Exception(u"Error BContainer.__get_complex: key of length 0.")
            return dictReturn
        else:
            raise Exception("Error BContainer.get: No valid type for collective set. Use dict!")        
    
    def __get_path(self, path = u""):
        if self.__parent == None:
            return u"/" + path
        else:
            return self.__parent.__get_path( self.__parent.key(self) + u"/" +  path)
        
    def getb(self,name):
        if name in self.__Body:
            return self.__Body.get(name)
        else:
            print "name: ", name
            print "type(name): ", type(name)
            print "body: ", self.__Body
            self.ls()
            raise Exception(u"Error BContainer.getb: Element \"" + name +"\" in " + unicode(type(self)) + u" does not exist.")
    
    def getbCond(self, attrib, value, returnAttribute = None):
        listChilds = []
        for key in self.__Body:
            element = self.__Body[key]
            if (attrib in element.__Attributes) or (attrib in element.__AttributesVirtual):
                if element.get(attrib) == value:
                    if returnAttribute == None:
                        listChilds.append(element)
                    else:
                        listChilds.append(element.get(returnAttribute))
        return listChilds
        
        
    ## Method that gets the head of a container
     
    def geth(self):
        return self.__Head
    
    ## Method that returns the parent element
    
    def getParent(self):
        return self.__parent
    
    def getRoot(self, _type = None):
        if _type == None:
            if self.__parent == None:
                return self
            else:
                return self.__parent.getRoot()
        else:
            types = inspect.getmro(type(self))
            if _type in types:
                return self
            else:
                if self.__parent == None:
                    return self
                else:
                    return self.__parent.getRoot(_type) 
    
    ## Method that returns True if the attribute exists
    
    def isAttr(self, attr):
        return (attr in self.__Attributes) or (attr in self.__AttributesVirtual)
    
    ## Method that returns true, if an attribute exists and has the value "True", otherwise it returns "False" 

    def isAttrTrue(self, attr):      
        if self.isAttr(attr):
            return self.get(attr) == True
        else:
            return False
        
    ## Method that determines if there exists an element for a certain key
    
    def isInBody(self, key):
        return key in self.__Body  
    
    ## Method that gets all attributes
    
    def getAttrs(self):
        return self.__Attributes.keys()
     
    ## Method that gets all keys of the child elements
    
    def getChildKeys(self):
        return self.__Body.keys()
    
    ## gets key of an objekt in Body
    def key(self, obj):
        for key in self.__Body:
            objComp = self.__Body[key]
            if objComp == obj:
                return key  
        return None
            
    def ls(self):
        listLs = []
        for key in self.__Body:
            elem = self.getb(key)
            listLs.append((unicode(elem.get("Name")), unicode(type(elem))))
        if len(listLs) > 0:
            self.__printLsList(sorted(listLs))
          
    def lsAttr(self):
        listLsAttr = []
        for attr in self.__Attributes:
            listLsAttr.append( (unicode(attr), u"-",  unicode(self.__Attributes[attr]) ) )
        for attr in self.__AttributesVirtual:
            print "attr: ", attr
            listLsAttr.append( (unicode(attr),u"v", unicode(self.get(attr))))
        if len(listLsAttr) > 0:
            self.__printLsList(sorted(listLsAttr))
          
    def __printLsList(self, lsList):
        len_lsList = len(lsList)
        if len_lsList == 0:
            return
        else:
            len_lsList_0 = len(lsList[0])
            if len_lsList_0 == 0:
                return
        len_cell = []
        max_len_cell = []
        unicode_key = []
        unicode_whitespace = []
        for i in range(len_lsList_0):
            if i < len_lsList_0 - 1:
                len_cell.append([])
                unicode_key.append([])
                unicode_whitespace.append([])
                len_cell[i] = [ len(row[i]) for row in lsList ]
                max_len_cell.append(max(len_cell[i]))
            else:
                len_cell.append([])
                len_cell[i] = [ 0 for cell in lsList ]
                max_len_cell.append(0)
        for i in range(len_lsList):
            ustrPrint = u""
            for j in range(len(lsList[i])):
                ustrPrint += lsList[i][j]
                ustrPrint += u" " * (max_len_cell[j] - len_cell[j][i] + 1)
            print ustrPrint 

    # moves an element
    
    def mv(self, path0, path1):
               
        if type(path0) in (str, unicode):
            objSource       = self.getObjFromPath(path0)
        else:
            objSource       = path0
        parentSource    = objSource.getParent()
        parentSource.__Body.pop(parentSource.key(objSource))
        if type(path1) in (str, unicode):
            parentTarget    = self.getObjFromPath(path1)
        else:
            parentTarget = path1
        parentTarget.paste(objSource)

    def getObjFromPath(self,path):
        
        if not (type(path) == list):
            path = path.split(u"/")
            if path[-1] == u"":
                path.pop(-1)
        
        len_path = len(path)   
         
        if len_path == 0:
            return self
        
        path_0 = path[0]
        
        if path_0 == u"..":
            if self.__parent != None:
                return self.__parent.getObjFromPath(path[1:])
            else:
                raise Exception("Error BContainer.getObjFromPath: Syntax Error 1")
        elif path_0 == u"":
            root = self.getRoot()
            if root != None:
                return root.getObjFromPath(path[1:])
            else:
                raise Exception("Error BContainer.getObjFromPath: Syntax Error 2")
        elif path_0 == u".":
            return self.getObjFromPath(path[1:])
        else:
            if len_path == 1:
                path = path[0].split(u".")
                if len(path) > 1:
                    path = ".".join(path[0:-1])
                else:
                    path = path[0]
                #TODO Chance hasByID mechanism. Hash by unicoe(ID)
                # so far a quick and dirty workaround
                #if path.isdigit():
                #    path = int(path)
                obj = self.getb(path)
                return obj
            else:
                #TODO Chance hasByID mechanism. Hash by unicoe(ID)
                # so far a quick and dirty workaround
                #if path[0].isdigit():
                #    path[0] = int(path[0])
                obj = self.getb(path[0])
                return obj.getObjFromPath(path[1:]) 
    
    # function creating a new object and pasting it to the parent knot
    
    def new(self, _type, *args, **kwargs):
        newObject = _type(*args , **kwargs)
        return newObject

    ## This method pastes an object into another one.
                
    def paste(self, obj, name = None, bForceOverwrite = False, pathkey = None):
        
        
        types = inspect.getmro(type(obj))
        if BContainer in types: 
            key = obj.get(u"Name")
        else:
            if name == None: 
                raise Exception(u"Error BContainer.py: No key for paste-function!")
            else:
                key = name
        
        if key in self.__Body.keys():
            if bForceOverwrite:
                self.__Body[key] = obj
                obj.__parent = self                
            else:
                print "key (2)", key
                raise Exception(u"Key already in use. Set bForceOverwrite=True to enforce overwriting!")        
        else:
            self.__Body[key] = obj
            types = inspect.getmro(type(obj))
            if(BContainer in types):
                obj.__parent = self
    
    def recur(self, typeinfo, strFunction, tupleArgs, bSubTypes = False):
            
        if bSubTypes:
            types = inspect.getmro(type(self))
        else:
            types = [type(self)]
        bCallFunction = (typeinfo in types)

        if bCallFunction:
            if len(tupleArgs) > 0:
                strExec = u"self." + strFunction + u"(" + u"*tupleArgs" + u")"
            else:
                strExec = u"self." + strFunction + u"()"
            exec(strExec)
                
        for key in self.__Body:
            element = self.__Body[key]
            element.recur(typeinfo, strFunction, tupleArgs, bSubTypes)

    ##  Method to add or set an attribute
    
    def set(self,  attr, setObj, options = None):
                
        # None or empty string as attribute indicates complex set command with a whole dict to be set.
        if attr == None or attr == u"": 
            types = inspect.getmro(type(setObj))
            if dict in types:
                return self.__set_dict(setObj, options)
            else:
                raise Exception("Error BContainer.set: No valid type for collective set. Use dict!")
        if options == None: 
            self.__Attributes[attr] = setObj
        elif options == u"-p":
            val = self.__Attributes[attr]
            types = inspect.getmro(type(val))
            if (float in types) or (int in types):
                self.set(attr,  val + setObj)
            elif tuple in types:
                self.set(attr, tuple([a + b for a, b in zip(val, setObj ) ] ) )
            elif list in types:
                self.set(attr, [a + b for a, b in zip(val, setObj ) ] )
                
    def __set_dict(self, setObj, options):
        for key in setObj:
            len_key = len(key)
            if len_key > 0:
                if key[0] == u"@":
                    childObj = self.getb(key[1:])
                    setObjChild = setObj[key]
                    childObj.__set_dict(setObjChild, options)
                else:
                    self.set(key, setObj[key], options)
            else:
                raise Exception(u"Error BContainer.__set_dict: key of length 0.")
                    
        
class BList(BContainer, list):
    
    def __init__(self, *args, **kwargs):
        
        list.__init__(self, *args)
        BContainer.__init__(self, *args, **kwargs)


class BDict(BContainer, dict):
    
    def __init__(self, *args, **kwargs):
        
        dict.__init__(self, *args)
        BContainer.__init__(self, **kwargs)

