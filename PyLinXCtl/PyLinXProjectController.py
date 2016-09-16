'''
Created on 19.08.2015

@author: Waetzold Plaum
'''
import inspect
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal #, #QObject

import PyLinXData.BContainer as BContainer 
import PyLinXData.PyLinXHelper as PyLinXHelper 
import PyLinXGui.PX_Templates as PX_Templ
import PyLinXData.PyLinXCoreDataObjects as PyLinXCoreDataObjects
import PyLinXData.PX_ObjectHandler as PX_ObjectHandler 
import PyLinXData.PX_Signals #as PX_Signals  
from PyLinXCompiler import PyLinXRunEngine
import PyLinXData.PyLinXHelper as helper
import PyLinXController


class PyLinXProjectController(PyLinXController.PyLinXController):

    def __init__(self, rootGraphics = None, mainWindow = None, bListActions = True):
        
        super(PyLinXProjectController, self).__init__(None, mainWindow, bListActions, u"MainController")

        # Initializing some data structures
        ###################################
        self.activeFolder       = PyLinXCoreDataObjects.PX_PlottableGraphicsContainer(self, u"rootGraphics")
        self._latentGraphics    = PyLinXCoreDataObjects.PX_PlottableLatentGraphicsContainer(self, name="latentGraphics")
        self._signalFiles       = PyLinXData.PX_Signals.PX_SignalsFolder(self)
        self._objectHandler     = PX_ObjectHandler.PX_ObjectHandler(self)
        PyLinXData.PX_DataDictionary.PX_DataDictionary(self)


        # Initializing the dictionary of avaiable constructors
        ######################################################
        dictConstructors = {    u"basicOperator"   : PyLinXCoreDataObjects.PX_PlottableBasicOperator,\
                                u"connector"       : PyLinXCoreDataObjects.PX_PlottableConnector,\
                                u"highlightRect"   : PyLinXCoreDataObjects.PX_LatentPlottable_HighlightRect,\
                                u"varElement"      : PyLinXCoreDataObjects.PX_PlottableVarElement,\
                                u"dataViewer"      : PyLinXCoreDataObjects.PX_PlottableVarDispElement,\
                                u"signalFile"      : PyLinXData.PX_Signals.PX_Signals}
        self.paste(BContainer.BDict(dictConstructors, name="dictConstructors"), bForceOverwrite = True)
        
        # Configuration of the dict of aliases
        ###################################### 
        dictAlias = self.getb("dictAlias")
        dictAlias[ u"@latent"]          = self._latentGraphics
        dictAlias[ u"@signals"]         = self._signalFiles
        dictAlias[ u"@objects"]         = self._objectHandler
        dictAlias[ u"@mainController"]  = self

  
        # The Controller could instantiated without a GUI. In this case no actions are avaiable
        #######################################################################################
        if bListActions:
            self.__listActions = [None, mainWindow.ui.actionNewElement, mainWindow.ui.actionNewPlus,\
                               mainWindow.ui.actionNewMinus, \
                               mainWindow.ui.actionNewMultiplication, mainWindow.ui.actionNewDivision] 


        # Seting sonme attributes
        #########################
        self._BContainer__AttributesVirtual.extend([u"ConnectModInfo", \
                                                    u"Selection_listKeys", \
                                                    u"lenDataDictionary", \
                                                    u"listSignalFiles"])


        self._BContainer__Attributes[u"px_mousePressedAt_X"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_Y"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_x"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_y"] = sys.maxint
        self._BContainer__Attributes[u"bSimulationMode"]     = False
        self._BContainer__Attributes[u"bSimulationRuning"]   = False
        # These attributes are used to manage 
        # the selection mechanims
        self._BContainer__Attributes[u"Selection_bDeep"]     = False        
        self._BContainer__Attributes[u"bConnectorPloting"]   = False
        self._BContainer__Attributes[u"ConnectorToModify"]   = None
        self._BContainer__Attributes[u"idxPointModified"]    = None
        
        self.set(u"LogLevel",1)   
        # idx that indicates the selected tool
        self.set(u"idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.set(u"ID_activeConnector", -1)
        # idx of the last selected Data-Viewer
        self.set(u"idxLastSelectedDataViewer", -1)
        self.set(u"idxOutPinConnectorPloting", None)
        self.set(u"listDataDispObj", [])
        
    
    
    
    ##############
    # PROPERTIES
    ##############    
 
    def get_dictQtSignals(self):
        return self._PyLinXController__dictQtSignals
    
    dictQtSignals = property(get_dictQtSignals)
    
    def get_objectHandler(self):
        return self.getb(u"ObjectHandler")
    
    objectHandler = property(get_objectHandler)        


    def get_latentGraphics(self):
        return self._latentGraphics
    
    def set_latentGraphics(self, latentGraphics, options = None):
        self._latentGraphics = latentGraphics
                
    latentGraphics = property(get_latentGraphics, set_latentGraphics)


    def get_signalFiles(self):
        return self._signalFiles
    
    def set_signalFiles(self, signalFiles, options = None):
        self._signalFiles = signalFiles
        
    signalFiles = property(get_signalFiles, set_signalFiles)

   
    # Execute specific commands
    ############################

    def __execCommand_select(self, command):
        
        self._PyLinXController__execCommand_select(command)
        
        # reset ConnectorToModify if necessary
        len_selection = len(self.selection)
        if len_selection  > 0:
            if len_selection  > 1:
                return  self.set(u"ConnectorToModify", None)
            else:
                ConnectorToModify = self.get(u"ConnectorToModify")
                if self.selection[0] != ConnectorToModify:
                    return  self.set(u"ConnectorToModify", None)
                                
        self.activeFolder.set(u"ConnectorToModify", None )
        self.activeFolder.set(u"idxPointModified" , None )                   
   
    
    ################
    # GET Command
    ################

# Speziell und allgemein    
    
    def get(self, attr):
    
        if attr == u"ConnectModInfo":            
            return (super(PyLinXProjectController, self).get(u"ConnectorToModify"),\
                    super(PyLinXProjectController, self).get(u"idxPointModified"))
        elif attr == u"lenDataDictionary":
            return len(self.getb(u"DataDictionary"))
        elif attr == u"listCommands":
            return self._PyLinXController__listCommands
        elif attr == u"listSignalFiles":
            return self.__get_listSignalFiles()
        elif attr == u"Selection_bUnlock":
            return self.__get_Selection_bUnlock()      
        else:
            return super(PyLinXProjectController, self).get(attr)  


# Speziell udn allgemein (nacht Attribut zu sortieren)
  
    def __get_listSignalFiles(self):
        
        listSignalFiles = []
        for key in self._signalFiles.getChildKeys():
            obj = self._signalFiles.getb(key)
            types = inspect.getmro(type(obj))
            if PyLinXData.PX_Signals.PX_Signals in types:
                listSignalFiles.append(obj)
        return listSignalFiles
        
    def __get_Selection_bUnlock(self):
        
        bUnlockResult = False
        for element in self.selection:
            bUnlock = element.get(u"bUnlock")
            bUnlockResult = bUnlock or bUnlockResult
        return bUnlockResult 
        
    def get_dimActiveGraphics(self):
        
        keys = self.activeFolder.getChildKeys()
        maxX = 0
        maxY = 0
        x = 0
        y = 0
        for key in keys:
            obj = self.activeFolder.getb(key)
            x = obj.X  
            if x > maxX:
                maxX = x
            y = obj.Y  
            if y > maxY:
                maxY = y
        return (maxX, maxY)
    

    ################
    # SET-COMMAND
    ################
    
    
    def set(self, attr, value, options = None):
        
        if attr == u"idxToolSelected":           
            return self.__set_idxToolSelected(value, options)
            
        elif attr == u"bSimulationMode":
            return self.__set_bSimulationMode(value, options)
        
        elif attr == u"listCommands":
            return None
            
        elif attr == u"bConnectorPloting":
            return self.__set_bConnectorPloting(value, options)
        
        elif attr == u"ConnectModInfo":
            super(PyLinXProjectController, self).set(u"ConnectorToModify",self.mainController.activeFolder.getb(unicode(value[0])), options)
            super(PyLinXProjectController, self).set(u"idxPointModified",value[1], options)
            
        elif attr == u"lenDataDictionary":
            self.__set_lenDataDictionary(value, options)
            
        elif attr == u"listSignalFiles":
            return None
            
        else:
            return super(PyLinXProjectController, self).set(attr,value, options)
        
        
    def __set_idxToolSelected(self, value, options):
        
        if self.isAttr(u"idxToolSelected"):
            idxToolSelectedOld = self.get(u"idxToolSelected")
        else:
            idxToolSelectedOld = None
            
        if idxToolSelectedOld not in [None, 0]:
            oldAction = self.__listActions[idxToolSelectedOld]
            oldAction.setChecked(False)
        if value > 0 and value <= PyLinXHelper.ToolSelected.max:
            self.__listActions[value].setChecked(True)
            return BContainer.BContainer.set(self,u"idxToolSelected", value, options)
        elif value == 0:
            return BContainer.BContainer.set(self,u"idxToolSelected", 0, options)

    def __set_bSimulationMode(self, value, options):
          
            if value == True:
                
                runEngine = PyLinXRunEngine.PX_CodeAnalyser(self.mainController, self._PyLinXController__mainWindow)
                self.paste(runEngine, bForceOverwrite=True)
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.backgroundSim)
                self._PyLinXController__mainWindow.ui.drawWidget.setPalette(pal)                
                self._PyLinXController__mainWindow.ui.actionRun.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(True)
                self._PyLinXController__mainWindow.ui.actionNewElement.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionNewPlus.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionNewMinus.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionNewMultiplication.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionNewDivision.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionStop.setEnabled(True)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, u"widgetShow", ())
            
            elif value == False:
                
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
                self._PyLinXController__mainWindow.ui.drawWidget.setPalette(pal)
                self._PyLinXController__mainWindow.ui.actionRun.setEnabled(False)
                self._PyLinXController__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(False)
                self._PyLinXController__mainWindow.ui.actionNewElement.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionNewPlus.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionNewMinus.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionNewMultiplication.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionNewDivision.setEnabled(True)
                self._PyLinXController__mainWindow.ui.actionStop.setEnabled(False)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, u"widgetHide", ())

                
            
            retVal = BContainer.BContainer.set(self,u"bSimulationMode", value, options)
            self.__set_bSimulationMode_MainTabs(value)
            return retVal
    
    
    def __set_bSimulationMode_MainTabs(self, value):
        
        self._PyLinXController__mainWindow.emit(QtCore.SIGNAL("updateTabs"))


    def __set_bConnectorPloting(self, value, options):
        
        if self.get(u"bConnectorPloting"):
            if value == False:
                self.latentGraphics.set(u"bConnectorPlotting", False)
                self.set(u"ConnectorPloting", None)
                self.set(u"idxToolSelected", PyLinXHelper.ToolSelected.none)
            return super(PyLinXProjectController, self).set(u"bConnectorPloting",value, options)
        else:
            return super(PyLinXProjectController, self).set(u"bConnectorPloting",value, options)        

    def __set_lenDataDictionary(self, value,options):
        if value == 0:
            DataDictionary = self.getb(u"DataDictionary")
            del DataDictionary
            DataDictionaryNew = BContainer.BDict({})
            DataDictionaryNew.set(u"Name", u"DataDictionary")
            DataDictionaryNew.set(u"DisplayName", u"DataDictionary")
            self._BContainer__Body[u"DataDictionary"] = DataDictionaryNew 
        else:
            raise Exception("Error PyLinXProjectController.__set_lenDataDictionary: set-values other then 0 are not accepted!")
    
    ########
    # MISC
    ########
    
    ## TODO: The mechanism of recur has to be modified by the use of lambda expressions

# Ggf. zu verallgemeinern. Auch andere GUI-Teile koennten bei einem Exberiment zu verallgemeinern sein.

    # Method that synchronizes the DataDictionary with the data hold for graphical representation in the DataViewer
    def sync(self):
        self.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, u"sync", ())
        self.objectHandler.recorder.record()
        
    # Method that is executed when a run is stopped
    def stop_run(self):
        print "stop_run"
        self.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, u"stop_run", ())
        self.objectHandler.recorder.exit()
        self.set(u"bSimulationRuning", False)


# Allgemein
        
    # Method to change the active folder
    def cd(self, path):
        try:
            obj = self.getObjFromPath(path)
        except Exception as exp:
            errorString = u"Error PyLinXProjectController,PyLinXProjectController.cd: Failed to open " + path + \
                     " - " + unicode(Exception) 
            helper.error(errorString)
            return 
        if obj == None:
            errorString = u"Error PyLinXProjectController,PyLinXProjectController.cd - " + unicode(Exception) 
            helper.error(errorString)
            return
        self.activeFolder = obj
        return

# Ggf. zu verallgemeinern. Auch andere GUI-Teile koennten bei einem Exberiment zu verallgemeinern sein.
    
    # Method to initialize a simulation run
    def runInit(self):
        self._objectHandler.runInit()
        self.set(u"bSimulationRuning", True)

# Speziell
        
    def updateDataDictionary(self):
        self._objectHandler.updateDataDictionary()
