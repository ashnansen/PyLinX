'''
Created on 18.12.2014

@author: Waetzold Plaum
'''
# general imports
import inspect
from PyQt4 import QtCore
import threading

# PyLinX specific imports
from PyLinXData import *

global DataDictionary

class PX_CodeGenerator(BContainer.BContainer):
 
    def __init__(self, parent, PyLinXMainObject):
        super(PX_CodeGenerator, self).__init__("PX_CodeGeerator")
        
        # TEST
        ######
        
        self.__runThread = None
        self.__runThreadMessageQueue = PyLinXMainObject.runThreadMessageQueue
        # Object Data
        ###############
        
        self.__rootContainer = parent
        self.__PyLinXMainObject  = PyLinXMainObject
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
        
        self.__Code = []
        self.__CodeStr = ""

        # Processing
        ############
        
        # generate Code 
        
        self.__genCode()
        
        # create global data-Dictionary

        RunConfigDictionary = BContainer.BDict({})
        RunConfigDictionary.set("Name", "RunConfigDictionary")
        RunConfigDictionary.set("DisplayName", "RunConfigDictionary")
        RunConfigDictionary["t"] = 0.0
        self.__rootContainer.paste(RunConfigDictionary, bForceOverwrite = True)  
        global DataDictionary      
        DataDictionary = BContainer.BDict({})
        DataDictionary["*bGuiToUpdate"] = True      # Bit indicating that the values are updated, but the GUI, excpecially the 
                                                    # data viewers are not updated yet. The star indicates that this is and 
                                                    # should no valid Python Variable used in the simulation model 
        DataDictionary.set("Name", "DataDictionary")
        DataDictionary.set("DisplayName", "DataDictionary")    
        # initializing values
        for element in self.__listVarElements:
            DataDictionary[element.get("Name")] = 0.0
        self.__rootContainer.paste(DataDictionary, bForceOverwrite = True)                
        # setting values to predefined defaults (e.g. constant stimulations should be displayed)         
        self.__rootGraphics.updateDataDictionary()
  



        
      
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
            super(PX_CodeGenerator.PX_CodeRefObject, self).__init__(name)
            self._BContainer__Head = refObj
            
            
        def get_ref(self):
            return self._BContainer__Head
        
        ref = property(get_ref)
            
                
    class PX_CodableObject(PX_CodeRefObject):
        
        def __init__(self,*param):
            super(PX_CodeGenerator.PX_CodableObject, self).__init__(*param)
            
    
    class PX_CodableBasicOperator(PX_CodableObject):
        
        def __init__(self,*param):
            super(PX_CodeGenerator.PX_CodableBasicOperator, self).__init__(*param)
            
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
            super(PX_CodeGenerator.PX_CodableVarElement, self).__init__(*param)
            
        def getCode(self):
            global Code
            global nIndent
            lenBody = len(self._BContainer__Body)
            name = self.ref.get("Name") 
            if lenBody == 1:
                input = self.getb(self.getChildKeys()[0])
                code_to_add = nIndent * "    " + name + " = " + input.getCode() 
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
            if PyLinXDataObjects.PX_PlottableVarElement in types:
                knotRefObj = PX_CodeGenerator.PX_CodableVarElement(knot)
            if PyLinXDataObjects.PX_PlottableBasicOperator in types:
                knotRefObj = PX_CodeGenerator.PX_CodableBasicOperator(knot)
                      
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
            if PyLinXDataObjects.PX_PlottableVarElement in types:
                self.__listVarElements.append(element)
            if PyLinXDataObjects.PX_PlottableBasicOperator in types:
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
        
        rootRef = PX_CodeGenerator.PX_CodeRefObject(self.__rootGraphics)
        for notConnectedOutElement in self.__listNotConnectedOutVarElements:
            rootRef.paste(__createSingleBranch(notConnectedOutElement), bHashById = True )
        self.__syntaxTree = rootRef


    def __writeCode(self):
        
        global Code
        Code = []
        global nIndent
        Code.append("def main():\n")
        Code.append("    global DataDictionary")
        Code.append("    Variables = DataDictionary.keys()")
        Code.append("    for variable in Variables:")
        Code.append("        if variable[0] != \"*\":")
        Code.append("            execStr = variable + \" = DataDictionary[variable]\" ")
        Code.append("            exec(execStr)\n")
        
        nIndent = 1
        
        keys = self.__syntaxTree.getChildKeys()
        for key in keys:
            child = self.__syntaxTree.getb(key)
            child.getCode()
          
        Code.append("\n    for variable in Variables:")
        Code.append("        if variable[0] != \"*\":")
        Code.append("            execStr = \"DataDictionary[variable] = \" + variable ")
        Code.append("            exec(execStr)\n")
        Code.append("\nmain()")


        self.__Code = Code
        self.__CodeStr = ""
        
        
        for line in Code:
            self.__CodeStr += line
            self.__CodeStr += "\n"
        print "BEGIN---------------"
        print self.__CodeStr
        print "END-----------------"

    class SimulationThread(BContainer.BContainer, QtCore.QThread ):
        
        def __init__(self, CodeGenerator,  mainDrawWidget, rootContainer):
            QtCore.QThread.__init__(self)
            self.__CodeGenerator            = CodeGenerator
            self.__runThreadMessageQueue    = CodeGenerator._PX_CodeGenerator__runThreadMessageQueue
            self.__drawWidget               = mainDrawWidget
            self.__rootContainer            = rootContainer
            self.__signalUpdated            = QtCore.pyqtSignal(str)
            
        def __del__(self):
            self.exit(0)
            
        def run(self):
            
            
            RunConfigDictionary = self.__rootContainer.getb("RunConfigDictionary")
            self.__CodeGenerator.runInit()
            while 1:
                self.__CodeGenerator.run()
                print "test 0"
                self.emit(QtCore.SIGNAL("signal_repaint"))
                #self.emit(QtCore.SIGNAL("signal_repaint"))
                print "test 1"
                
                if not self.__runThreadMessageQueue.empty():
                    try:
                        message = self.__runThreadMessageQueue.get()
                    except:
                        message = None
                else:
                    message = None
                                
                # Maybe some day we have to implement a more sophisticated protocoll
                if message != None:
                    print "runThreadMessageQueue.task_done()"
                    self.__runThreadMessageQueue.task_done()
                    return
                
        
    def startRun(self, drawWQidget, stopEvent, repaintEvent):
        
        self.__runThread = PX_CodeGenerator.SimulationThread(self, self.__PyLinXMainObject.drawWidget, self.__rootContainer)
 
        self.__PyLinXMainObject.drawWidget.connect(self.__runThread, QtCore.SIGNAL("signal_repaint"), self.__PyLinXMainObject.drawWidget.repaint,\
                                                                          QtCore.Qt.BlockingQueuedConnection)
        self.__runThread.start()
        
    def stopRun(self):
        
        self.__runThread.exit(0)

    def runInit(self):
        self.t = 0
        self.delta_t = 0.02
        global DataDictionary
        DataDictionary = self.__rootContainer.getb("DataDictionary")
        global RunConfigDictionary
        RunConfigDictionary = self.__rootContainer.getb("RunConfigDictionary")
        RunConfigDictionary["t"] = self.t
        RunConfigDictionary["delta_t"] = self.delta_t
        bSimulationRuning = True
        RunConfigDictionary["bSimulationRuning"] = bSimulationRuning
        self.i = 0
            
    def run(self):
        #print "i:", self.i
        global DataDictionary
        self.__rootGraphics.updateDataDictionary()
        try:
            exec(self.__CodeStr)
        except Exception as exc:
            strExp = str(exc)
            print "Error executing code! -- " + strExp 
        
        self.t+= self.delta_t
        DataDictionary["*bGuiToUpdate"] = True
        RunConfigDictionary["t"] = self.t

        self.i +=1

