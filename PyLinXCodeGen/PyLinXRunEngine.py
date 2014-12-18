'''
Created on 18.12.2014

@author: Waetzold Plaum
'''
# general imports
import inspect

# PyLinX specific imports
from PyLinXData import *


class RunEngine(BContainer.BContainer):
    
    def __init__(self, parent):
        super(RunEngine, self).__init__("PX_RunEngine")
        self.__rootContainer = parent 
        self.__rootGraphics  = self.__rootContainer.getb("rootGraphics")
        
        # Initialize Lists of DataTypes
        
        self.__listConnectors = []
        self.__listVarElements = []
        self.__listBasicOperators = []
        
        self.__listNotConnectedOutVarElements = []
        self.__listNotConnectedInVarElements = []
        
        # generate Code 
        
        self.__genCode()
            
    def __genCode(self):
        
        #############
        ## Frontend
        #############
        
        ## Lexicalic Analysis
        #####################
        
        pass
    
        ## Syntactic Analysis
        #####################
        # Here the syntax tree is generated
        
        self.__getSyntaxTree()
        
        
        ## Semantic Analysis
        ####################
        
        pass
    
        ###############
        ## Backend
        ###############
        
        ## Generate Code
        ################
        
        pass
    
        ## Optimize code
        ################
        
        pass
    
    def __getSyntaxTree(self):
        
        def __createSingleBranch(knot):
            print "__createSingleBranch"
            pass
        
        
        # Creating lists of different data types
        
        childKeys = self.__rootGraphics.getChildKeys()
        
        for key in childKeys:
            element = self.__rootGraphics.getb(key)
            types = inspect.getmro(type(element))
            if PyLinXDataObjects.PX_PlottableConnector in types:
                self.__listConnectors.append(element)
            if PyLinXDataObjects.PX_PlotableVarElement in types:
                self.__listVarElements.append(element)
            if PyLinXDataObjects.PX_BasicOperator in types:
                self.__listBasicOperators.append(element)
        
        
        # Creating lists of not connected elements
        
        setConnectedOutVarEleemnts = set([])
        for connector in self.__listConnectors:
            setConnectedOutVarEleemnts.add(connector.elem0)            
        setNotConnectedOutVarElements = set(self.__listVarElements).difference(setConnectedOutVarEleemnts)
        self.__listNotConnectedOutVarElements = list(setNotConnectedOutVarElements)

        setConnectedInVarEleemnts = set([])
        for connector in self.__listConnectors:
            setConnectedInVarEleemnts.add(connector.elem1)            
        setNotConnectedInVarElements = set(self.__listVarElements).difference(setConnectedInVarEleemnts)
        self.__listNotConnectedInVarElements = list(setNotConnectedInVarElements)        
        
        print "self.__listNotConnectedOutVarElements: ", self.__listNotConnectedOutVarElements
        print "self.__listNotConnectedInVarElements: ", self.__listNotConnectedInVarElements
        
        # Creating the Syntax Tree
        
        for notConnectedOutElement in  self.__listNotConnectedOutVarElements:
            __createSingleBranch(notConnectedOutElement)
         
        
            