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
from PyLinXCode import Code
from PyLinXCodeRef import PX_CodeRefObject, PX_CodableBasicOperator, PX_CodableVarElement

class PX_CodeGenerator(BContainer.BContainer):
    
    class CodingVariant:
        ReadSingleVars = 0
        ReadVarsFromDataDict = 1
 
    def __init__(self, parent, PyLinXMainObject):
        
        super(PX_CodeGenerator, self).__init__(u"PX_CodeGeerator")       
        self.__runThread = None
        self.__runThreadMessageQueue = PyLinXMainObject.runThreadMessageQueue
        
        # Object Data
        ###############
        
        self.__PyLinXMainObject  = PyLinXMainObject
        self.__rootGraphics  = PyLinXDataObjects.PX_Object.mainController.getb(u"rootGraphics")
        
        # Initialize Lists of DataTypes
        
        self.__listConnectors = []
        self.__listVarElements = []
        self.__listBasicOperators = []
        
        self.__listNotConnectedOutVarElements = []
        self.__listNotConnectedInVarElements = []
        
        # Syntax Tree
        
        self.__syntaxTree = None
        
        # Code
        
        self.__Code = Code()
        self.__CodeStr = u""
        
        # Setting Coding-Variant           
        self.set(u"CodingVariant", PX_CodeGenerator.CodingVariant.ReadVarsFromDataDict)
        # self.set(u"CodingVariant", PX_CodeGenerator.CodingVariant.ReadSingleVars)

        # Processing
        ############
        
        # generate Code 
        
        self.__genCode()
        
        # create global data-Dictionary

        RunConfigDictionary = BContainer.BDict({})
        RunConfigDictionary.set(u"Name", u"RunConfigDictionary")
        RunConfigDictionary.set(u"DisplayName", u"RunConfigDictionary")
        RunConfigDictionary[u"t"] = 0.0
        PyLinXDataObjects.PX_Object.mainController.paste(RunConfigDictionary, bForceOverwrite = True)
        self.__RunConfigDictionary = RunConfigDictionary 

        self.__DataDictionary = PyLinXDataObjects.PX_Object.mainController.getb("DataDictionary") 
        for element in self.__listVarElements:
            self.__DataDictionary[element.get(u"Name")] = 0.0                 
        self.__rootGraphics.updateDataDictionary()
            
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
        
        def __createSingleBranch(parent, knot):
            
            CodingVariant = self.get(u"CodingVariant")
            types = inspect.getmro(type(knot))
            if PyLinXDataObjects.PX_PlottableVarElement in types:
                knotRefObj = PX_CodableVarElement(parent,knot, CodingVariant)
            elif PyLinXDataObjects.PX_PlottableBasicOperator in types:
                knotRefObj = PX_CodableBasicOperator(parent,knot, CodingVariant)                  
            for connector in self.__listConnectors:
                if connector.elem1 == knot:
                    __createSingleBranch(knotRefObj,connector.elem0)
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
        
        rootRef = PX_CodeRefObject(self, self.__rootGraphics)
        for notConnectedOutElement in self.__listNotConnectedOutVarElements:
            __createSingleBranch(rootRef, notConnectedOutElement) 
        self.__syntaxTree = rootRef 

    def __writeCode(self):
        
        # TODO: The code generator should get two modes: Simulation Mode and Productive Mode. In the simulation Mode all 
        # values should be directly read from the DataDictionary, so that no  exec at the beginning and the end of one calculation
        # circle is neccessary. In the Prodictive Mode the code is generated using single variable names without the Data-Dictionary.
        
        self.__Code.append(u"def main(DataDictionary):\n")
        CodingVariant = self.get(u"CodingVariant")
        
        if CodingVariant == PX_CodeGenerator.CodingVariant.ReadSingleVars:
            self.__Code.append(u"    Variables = DataDictionary.keys()")
            self.__Code.append(u"    execStr = u\"\"")
            self.__Code.append(u"    for variable in Variables:")
            self.__Code.append(u"        if variable[0] != u\"*\":")
            self.__Code.append(u"            execStr += (variable + u\" = DataDictionary[\\\"\" + variable +\"\\\"]\\n\")")   
            self.__Code.append(u"    exec(execStr)\n")
        
        self.__Code.changeIndent(1)
        
        keys = self.__syntaxTree.getChildKeys()
        for key in keys:
            child = self.__syntaxTree.getb(key)
            child.getCode(self.__Code)
            
        if CodingVariant == PX_CodeGenerator.CodingVariant.ReadSingleVars:          
            self.__Code.append(u"\n    execStr = u\"\"")
            self.__Code.append(u"    for variable in Variables:")
            self.__Code.append(u"        if variable[0] != \"*\":")
            self.__Code.append(u"            execStr += (u\"DataDictionary[\\\"\" + variable + \"\\\"] = \" + variable + u\"\\n\" )")
            self.__Code.append(u"    exec(execStr)\n")
            
        self.__Code.append(u"\nmain(DataDictionary)")

        self.__CodeStr = self.__Code.getCodeStr()
        print "BEGIN---------------"
        print self.__CodeStr
        print "END-----------------"

    class SimulationThread(BContainer.BContainer, QtCore.QThread ):
        
        def __init__(self, CodeGenerator,  mainDrawWidget):
            QtCore.QThread.__init__(self)
            self.__CodeGenerator            = CodeGenerator
            self.__runThreadMessageQueue    = CodeGenerator._PX_CodeGenerator__runThreadMessageQueue
            self.__drawWidget               = mainDrawWidget
            self.__signalUpdated            = QtCore.pyqtSignal(str)
            
        def __del__(self):
            self.exit(0)
            
        def run(self):
            
            self.__CodeGenerator.runInit()
            while 1:
                self.__CodeGenerator.run()
                # Synchronize the data in DataDictionary with the data stored in the DataViewer-GUI
                self.emit(QtCore.SIGNAL(u"signal_sync"))
                # Trigger Repaint
                self.emit(QtCore.SIGNAL(u"signal_repaint"))
                
                if not self.__runThreadMessageQueue.empty():
                    try:
                        message = self.__runThreadMessageQueue.get()
                    except:
                        message = None
                else:
                    message = None
                                
                # Maybe some day we have to implement a more sophisticated protocoll
                if message != None:
                    self.__runThreadMessageQueue.task_done()
                    self.emit(QtCore.SIGNAL(u"signal_stop_run"))
                    return
                
        
    def startRun(self, drawWQidget, stopEvent, repaintEvent):
        
        self.__runThread = PX_CodeGenerator.SimulationThread(self, self.__PyLinXMainObject.drawWidget)
        self.__PyLinXMainObject.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_repaint"), self.__PyLinXMainObject.drawWidget.repaint,\
                                                                          QtCore.Qt.BlockingQueuedConnection)
        self.__PyLinXMainObject.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_sync"),\
                                                   PyLinXDataObjects.PX_Object.mainController.mainController.sync,\
                                                   QtCore.Qt.BlockingQueuedConnection)
        self.__PyLinXMainObject.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_stop_run"),
                                                   PyLinXDataObjects.PX_Object.mainController.mainController.stop_run)
        
        self.__runThread.start()
        

    def runInit(self):
        
        self.delta_t = 0.02
        self.t = - self.delta_t
        self.__RunConfigDictionary[u"t"] = self.t
        self.__RunConfigDictionary[u"delta_t"] = self.delta_t
        bSimulationRuning = True
        self.__RunConfigDictionary[u"bSimulationRuning"] = bSimulationRuning
            
    def run(self): 
        import cProfile 
        cProfile.runctx("self.run_()", globals(), locals(), "profile.stat")
           
    def run_(self):
        self.t+= self.delta_t    
        self.__RunConfigDictionary[u"t"] = self.t
        self.__rootGraphics.updateDataDictionary()
        DataDictionary = self.__DataDictionary 
        try:
            exec(self.__CodeStr, globals(), locals())
        except Exception as exc:
            strExp = str(exc)
            print "Error executing code! -- " + strExp 
