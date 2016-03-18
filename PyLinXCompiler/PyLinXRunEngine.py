'''
Created on 18.12.2014

@author: Waetzold Plaum
'''
# general imports
import inspect
from PyQt4 import QtCore
import mdfreader 
import numpy as np
import os
from datetime import datetime

from PyLinXData import BContainer, PyLinXCoreDataObjects

from PyLinXCode import Code
from PyLinXCodeRef import PX_CodeRefObject, PX_CodableBasicOperator, PX_CodableVarElement

# Allgemein

class PX_CodeAnalyser(BContainer.BContainer, QtCore.QObject):
    
    class CodingVariant:
        ReadSingleVars = 0
        ReadVarsFromDataDict = 1
 
    def __init__(self, parent, PyLinXMainObject):
        
        super(PX_CodeAnalyser, self).__init__(u"PX_CodeGeerator")
        QtCore.QObject.__init__(self)    
        self.__runThread = None
        self.__runThreadMessageQueue = PyLinXMainObject.runThreadMessageQueue
        
        # Object Data
        ###############
        
        self.__PyLinXMainObject  = PyLinXMainObject
        self.__mainController    = parent
        self.__rootGraphics      = self.__mainController.getb(u"rootGraphics")
        self.__objectHandler     = self.__mainController.getb(u"ObjectHandler")
        
        # Initialize Lists of DataTypes
        
        self.__listConnectors = []
        self.__listVarElements = []
        self.__listBasicOperators = []
        
        self.__listNotConnectedOutVarElements = []
        self.__listNotConnectedInVarElements = []
        
        # Syntax Tree
        
        self.__syntaxTree = None

# Speziell
        
        # Code
        
        self.__Code = Code()
        self.__CodeStr = u""

# Allgemein
        
        # Setting Coding-Variant           
        self.set(u"CodingVariant", PX_CodeAnalyser.CodingVariant.ReadVarsFromDataDict)
        # self.set(u"CodingVariant", PX_CodeAnalyser.CodingVariant.ReadSingleVars)

        # Processing
        ############
        
        # generate Code 
        
        self.__genCode()
        
        # create global data-Dictionary

        RunConfigDictionary = BContainer.BDict({})
        RunConfigDictionary.set(u"Name", u"RunConfigDictionary")
        RunConfigDictionary.set(u"DisplayName", u"RunConfigDictionary")
        RunConfigDictionary[u"t"] = 0.0
        self.__mainController.paste(RunConfigDictionary, bForceOverwrite = True)
        self.__RunConfigDictionary = RunConfigDictionary 

        self.__DataDictionary = self.__mainController.getb(u"DataDictionary") 
        for element in self.__listVarElements:
            self.__DataDictionary[element.get(u"DisplayName")] = 0.0                 
        self.__mainController.updateDataDictionary()
            
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
            if PyLinXCoreDataObjects.PX_PlottableVarElement in types:            
                knotRefObj = PX_CodableVarElement(parent,knot, CodingVariant)
            elif PyLinXCoreDataObjects.PX_PlottableBasicOperator in types:
                orderConnection = {}
                for connector in self.__listConnectors:
                    if connector.elem1 == knot:
                        idxInPin    = connector.idxInPin
                        ID_inObject = connector.elem0.ID
                        orderConnection[ID_inObject] = idxInPin
                knotRefObj = PX_CodableBasicOperator(parent,knot, CodingVariant, orderConnection)                  
            for connector in self.__listConnectors:
                if connector.elem1 == knot:
                    __createSingleBranch(knotRefObj,connector.elem0)
            return knotRefObj
                    
        
        # Creating lists of different data types
        
        childKeys = self.__rootGraphics.getChildKeys()
        
        for key in childKeys:
            element = self.__rootGraphics.getb(key)
            types = inspect.getmro(type(element))
            if PyLinXCoreDataObjects.PX_PlottableConnector in types:
                self.__listConnectors.append(element)
            if PyLinXCoreDataObjects.PX_PlottableVarElement in types:
                self.__listVarElements.append(element)
            if PyLinXCoreDataObjects.PX_PlottableBasicOperator in types:
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

# Speziell

    def __writeCode(self):
        
        self.__Code.append(u"def main(DataDictionary):\n")
        CodingVariant = self.get(u"CodingVariant")
        
        if CodingVariant == PX_CodeAnalyser.CodingVariant.ReadSingleVars:
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
            
        if CodingVariant == PX_CodeAnalyser.CodingVariant.ReadSingleVars:          
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

# Allgemein

    class SimulationThread(BContainer.BContainer, QtCore.QThread ):
        
        def __init__(self, CodeGenerator,  mainDrawWidget, runConfigDictionary, dataDictionary):
            QtCore.QThread.__init__(self)
            self.__CodeGenerator            = CodeGenerator
            self.__runThreadMessageQueue    = CodeGenerator._PX_CodeAnalyser__runThreadMessageQueue
            self.__drawWidget               = mainDrawWidget
            self.__signalUpdated            = QtCore.pyqtSignal(str)
            self.__RunConfigDictionary      = runConfigDictionary
            self.__DataDictionary           = dataDictionary
            self.__bRecord = False
            
        def __del__(self):
            self.exit(0)
            
        def run(self):

            self.__runInit_prepareRecorderInRunThread()
            #i = 0
            while 1:
                #i += 1
                #print i
                self.__CodeGenerator.run_()
                # Synchronize the data in DataDictionary with the data stored in the DataViewer-GUI
                self.emit(QtCore.SIGNAL(u"signal_sync"))
                # Trigger Repaint
                self.emit(QtCore.SIGNAL(u"signal_repaint"))
                if self.__bRecord:
                    self.__record()
                
                if not self.__runThreadMessageQueue.empty():
                    try:
                        message = self.__runThreadMessageQueue.get()
                    except:
                        message = None
                else:
                    message = None
                # Maybe some day we have to implement a more sophisticated protocoll
                if message != None:
                    if self.__bRecord:
                        self.__runExitInTread()
                    self.__runThreadMessageQueue.task_done()
                    self.emit(QtCore.SIGNAL(u"signal_stop_run"))
                    return

        ###############################################
        # Methods used for the recording functionality
        ###############################################
        
        def __runInit_prepareRecorderInRunThread(self):
            self.__bRecord = self.__RunConfigDictionary["bRecord"]
            if self.__bRecord:
                self.__mdfObject = mdfreader.mdf()
            else: 
                self.__mdfObject = None
                return
            self.__dataDict = {}
            
            self.__dataDict[u"time_1"] = {}
            self.__dataDict["time_1"]["data"] = np.array([], np.float64)
            self.__dataDict["time_1"]["description"] = "Time"
            self.__dataDict["time_1"]["master"] = u"time_1"
            self.__dataDict["time_1"]["masterType"] = 1 
            self.__dataDict["time_1"]["unit"] = u"s"
            
            
            recorder_VariablesToRecordProcessed = self.__RunConfigDictionary[u"recorder_VariablesToRecordProcessed"]
            for var in recorder_VariablesToRecordProcessed:
                self.__dataDict[var] = {}
                self.__dataDict[var]["data"] = np.array([], np.float64)
                self.__dataDict[var]["description"] = u""
                self.__dataDict[var]["master"] = u"time_1"
                self.__dataDict[var]["masterType"] = 1 
                self.__dataDict[var]["unit"] = u""
       
        def __record(self):
            
            time = self.__RunConfigDictionary[u"t"]
            self.__dataDict[u"time_1"][u"data"] = np.append(self.__dataDict[u"time_1"][u"data"], time)
            for var in self.__RunConfigDictionary[u"recorder_VariablesToRecordProcessed"]:
                val = self.__DataDictionary[var]
                self.__dataDict[var][u"data"] = np.append(self.__dataDict[var]["data"], val)

        def __runExitInTread(self):
            
            recorder_VariablesToRecordProcessed = self.__RunConfigDictionary[u"recorder_VariablesToRecordProcessed"]
            listVarsToSave = [u"time_1"]
            listVarsToSave.extend(recorder_VariablesToRecordProcessed)
            for var in listVarsToSave :          
                self.__mdfObject.add_channel(0, str(var),\
                           self.__dataDict[var][u"data"],\
                           master_channel   = str("time_1"), \
                           master_type      = self.__dataDict[var][u"masterType"],\
                           unit             = str(self.__dataDict[var][u"unit"]),\
                           description      = str(self.__dataDict[var][u"description"]),\
                           conversion       = None)
        
            recorder_BaseFileName = self.__RunConfigDictionary[u"recorder_BaseFileName"]
            recorder_SaveFolder = self.__RunConfigDictionary[u"recorder_SaveFolder"]
            dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = str(os.path.join(recorder_SaveFolder,recorder_BaseFileName + u"_" + dt + u".dat"))
            self.__mdfObject.write(filename)                           
                
        
    def startRun(self, drawWQidget, stopEvent, repaintEvent):
        
        
        # connecting the signal "signal_runInit" to the main controller
        ###############################################################
        
        self.__PyLinXMainObject.ui.drawWidget.connect(self, QtCore.SIGNAL(u"signal_runInit"),self.__mainController.runInit)
        
        
        # initializing the Run
        ######################
        
        self.__runInit()
        self.emit(QtCore.SIGNAL(u"signal_runInit"))
        self.__runInit_prepareRecorder()        
        
        
        # creatubg tge run thread
        #########################
        
        self.__runThread = PX_CodeAnalyser.SimulationThread(self, self.__PyLinXMainObject.ui.drawWidget, self.__RunConfigDictionary,\
                                                                            self.__DataDictionary)

# speziell
        
        # Connecting signals to the run thread
        ######################################
        
        self.__PyLinXMainObject.ui.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_repaint"), self.__PyLinXMainObject.ui.drawWidget.repaint,\
                                                                            QtCore.Qt.BlockingQueuedConnection)
        self.__PyLinXMainObject.ui.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_sync"),\
                                                   self.__mainController.sync,QtCore.Qt.BlockingQueuedConnection)
        self.__PyLinXMainObject.ui.drawWidget.connect(self.__runThread, QtCore.SIGNAL(u"signal_stop_run"),self.__mainController.stop_run)
        

# allgemein

        # Starting the run thread
        #########################
        
        self.__runThread.start()

        

    def __runInit(self):
        
        self.delta_t = 0.02
        self.t = - self.delta_t
        self.__RunConfigDictionary[u"t"] = self.t
        self.__RunConfigDictionary[u"delta_t"] = self.delta_t
        
    def __runInit_prepareRecorder(self):

        recorder_BaseFileName = self.__objectHandler.get(u"recorder_BaseFileName")
        recorder_FileExtension = self.__objectHandler.get(u"recorder_FileExtension")
        recorder_SaveFolder = self.__objectHandler.get(u"recorder_SaveFolder")
        recorder_RecordState = self.__objectHandler.get(u"recorder_RecordState")
        bRecord = self.__objectHandler.get(u"bRecord")
        recorder_VariablesToRecordProcessed = self.__objectHandler.get(u"recorder_VariablesToRecordProcessed")
        
        self.__RunConfigDictionary[u"recorder_BaseFileName"] =  recorder_BaseFileName
        self.__RunConfigDictionary[u"recorder_FileExtension"] = recorder_FileExtension
        self.__RunConfigDictionary[u"recorder_SaveFolder"] = recorder_SaveFolder
        self.__RunConfigDictionary[u"recorder_RecordState"] = recorder_RecordState
        self.__RunConfigDictionary[u"bRecord"] = bRecord
        self.__RunConfigDictionary[u"recorder_VariablesToRecordProcessed"] = recorder_VariablesToRecordProcessed


    def run(self): 
        import cProfile 
        cProfile.runctx("self.run_()", globals(), locals(), "profile.stat")



    def run_(self):
        self.t+= self.delta_t
        self.__RunConfigDictionary[u"t"] = self.t
        self.__mainController.updateDataDictionary()
        
# speziell

        DataDictionary = self.__DataDictionary 
        try:
            exec(self.__CodeStr, globals(), locals())
        except Exception as exc:
            strExp = str(exc)
            print "Error executing code! -- " + strExp