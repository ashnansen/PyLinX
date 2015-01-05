'''
Created on 18.12.2014

@author: Waetzold Plaum
'''
# general imports
import inspect

# PyLinX specific imports
from PyLinXData import *
import CodeObj


class PX_CodeGeerator(BContainer.BContainer):
 
    def __init__(self, parent):
        super(PX_CodeGeerator, self).__init__("PX_CodeGeerator")
        
        # Object Data
        ###############
        
        self.__rootContainer = parent 
        self.__rootGraphics  = self.__rootContainer.getb("rootGraphics")
        
        # Initialize Lists of DataTypes
        
        self.__listConnectors = []
        self.__listVarElements = []
        self.__listBasicOperators = []
        
        self.__listNotConnectedOutVarElements = []
        self.__listNotConnectedInVarElements = []
        
        # Syntax Tree
        
        self.__syntaxTree = None
        
        # Code
        
        self.__Code = ""
        
        # Processing
        ###################
        
        # generate Code 
        
        self.__genCode()
        
        
    ################################################
    # internal classes used for code-generation
    # they should "know" all the global information
    # of the run-engine
    ################################################
    
    class PX_CodeRefObject(PyLinXDataObjects.PX_IdObject):
        '''
        classdocs
        '''
    
    
        def __init__(self, refObj):
            '''
            Constructor
            '''
            name = refObj.get("Name") + "_REF"
            super(PX_CodeGeerator.PX_CodeRefObject, self).__init__(name)
            self._BContainer__Head = refObj
            
            
        def get_ref(self):
            return self._BContainer__Head
        
        ref = property(get_ref)
    
    
    
    class PX_CodableObject(PX_CodeRefObject):
        
        def __init__(self,*param):
            super(PX_CodeGeerator.PX_CodableObject, self).__init__(*param)
            
    
    class PX_CodableBasicOperator(PX_CodableObject):
        
        def __init__(self,*param):
            super(PX_CodeGeerator.PX_CodableBasicOperator, self).__init__(*param)
            
        def getCode(self,):
            lenBody = len(self._BContainer__Body)
            if lenBody != 2:
                print "TODO: Error-Handling (2)"
            else:
                keys = self.getChildKeys()
                keys.sort()
                operator = self.ref._BContainer__Head
                var0 = self.getb(keys[0]).getCode()
                var1 = self.getb(keys[1]).getCode() 
                return "( " + var0 + " " + operator + " " + var1 + " ) "


    class PX_CodableVarElement(PX_CodableObject):
            
        def __init__(self,*param):
            super(PX_CodeGeerator.PX_CodableVarElement, self).__init__(*param)
            
        def getCode(self):
            global Code
            lenBody = len(self._BContainer__Body)
            name = self.ref.get("Name") 
            if lenBody == 1:
                input = self.getb(self.getChildKeys()[0])
                code_to_add =  name + " = " + input.getCode() 
                Code.append(code_to_add)
            return name
    
        
            
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
        
        self.__writeCode()
    
        ## Optimize code
        ################
        
        pass
    
    def __getSyntaxTree(self):
        
        def __createSingleBranch(knot):

            types = inspect.getmro(type(knot))
            if PyLinXDataObjects.PX_PlotableVarElement in types:
                knotRefObj = PX_CodeGeerator.PX_CodableVarElement(knot)
            if PyLinXDataObjects.PX_PlotableBasicOperator in types:
                knotRefObj = PX_CodeGeerator.PX_CodableBasicOperator(knot)
                      
            for connector in self.__listConnectors:
                if connector.elem1 == knot:
                    childRef = __createSingleBranch(connector.elem0)
                    knotRefObj.paste(childRef,connector.idxInPin)
            return knotRefObj
                    
        
        # Creating lists of different data types
        
        childKeys = self.__rootGraphics.getChildKeys()
        
        for key in childKeys:
            element = self.__rootGraphics.getb(key)
            types = inspect.getmro(type(element))
            if PyLinXDataObjects.PX_PlottableConnector in types:
                self.__listConnectors.append(element)
            if PyLinXDataObjects.PX_PlotableVarElement in types:
                self.__listVarElements.append(element)
            if PyLinXDataObjects.PX_PlotableBasicOperator in types:
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

        # Creating the Syntax Tree
        
        rootRef = PX_CodeGeerator.PX_CodeRefObject(self.__rootGraphics)
        for notConnectedOutElement in self.__listNotConnectedOutVarElements:
            rootRef.paste(__createSingleBranch(notConnectedOutElement), bHashById = True )
        self.__syntaxTree = rootRef


    def __writeCode(self):
        
        global Code
        Code = []
        
        keys = self.__syntaxTree.getChildKeys()
        for key in keys:
            child = self.__syntaxTree.getb(key)
            child.getCode()
        
        self.__Code = Code
        
        print "BEGIN---------------"
        for line in Code:
            print line
        print "END--------------"
        
        
        