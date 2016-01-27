'''
Created on 19.08.2015

@author: Waetzold Plaum
'''


import PyLinXData.BContainer as BContainer 
import PyLinXData.PyLinXHelper as PyLinXHelper 
from PyQt4 import QtGui, QtCore, uic, Qt
import inspect
import PyLinXData
import sys

import PyLinXGui.PX_Templates as PX_Templ
import PyLinXData.PyLinXDataObjects as PyLinXDataObjects
from PyLinXCodeGen import PyLinXRunEngine
import PyLinXData.PyLinXHelper as helper
 

class PyLinXMainController(PyLinXData.PyLinXDataObjects.PX_Object):

    
    def __init__(self, rootGraphics =None, mainWindow = None):
        
        super(PyLinXMainController, self).__init__(None, u"MainController")

        # Main Controller should be known to all objects.This mnechanism has to be changed if the 
        # PyLinX should get capable of multisession. Then the "paste" method should set the correponding main 
        # controller.  
        PyLinXData.PyLinXDataObjects.PX_Object.mainController = self
        
        # Initializing the DataDictionary
        
        DataDictionary = BContainer.BDict({})
        DataDictionary.set(u"Name", u"DataDictionary")
        DataDictionary.set(u"DisplayName", u"DataDictionary")
        self.paste(DataDictionary)   
        
        
        # Initializing List for Tracking of the commands
        self.__listCommands = []
        
        self.__mainWindow  = mainWindow
        self._activeFolder = PyLinXDataObjects.PX_PlottableGraphicsContainer(self, u"rootGraphics")
        self._rootGraphics = self._activeFolder 
        self._latentGraphics = PyLinXDataObjects.PX_PlottableLatentGraphicsContainer(self, name="latentGraphics")
        self.set(u"LogLevel", 0)
        self.__listActions = [None, mainWindow.ui.actionNewElement, mainWindow.ui.actionNewPlus,\
                              mainWindow.ui.actionNewMinus, \
                              mainWindow.ui.actionNewMultiplication, mainWindow.ui.actionNewDivision]
        self.set(u"listDataDispObj", [])
        
        dictConstructors = {    u"basicOperator"   : PyLinXDataObjects.PX_PlottableBasicOperator,\
                                u"connector"       : PyLinXDataObjects.PX_PlottableConnector,\
                                u"highlightRect"   : PyLinXDataObjects.PX_LatentPlottable_HighlightRect,\
                                u"varElement"      : PyLinXDataObjects.PX_PlottableVarElement,\
                                u"dataViewer"      : PyLinXDataObjects.PX_PlottableVarDispElement}
        
        self.paste(BContainer.BDict(dictConstructors, name="dictConstructors"))
               
        self._BContainer__Attributes[u"px_mousePressedAt_X"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_Y"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_x"] = sys.maxint
        self._BContainer__Attributes[u"px_mousePressedAt_y"] = sys.maxint
        # These attributes are used to manage the selection mechanims
        self._BContainer__Attributes[u"Selection_bDeep"]     = False        
        self._BContainer__Attributes[u"bConnectorPloting"]   = False
        self._BContainer__Attributes[u"ConnectorToModify"]   = None
        self._BContainer__Attributes[u"idxPointModified"]    = None
        
        self.set(u"LogLevel",1)
        #self.set(u"bConnectorPloting", False)     
        # idx that indicates the selected tool
        self.set(u"idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.set(u"ID_activeConnector", -1)
        # idx of the last selected Data-Viewer
        self.set(u"idxLastSelectedDataViewer", -1)
        self.set(u"idxOutPinConnectorPloting", None)
        self._BContainer__Attributes[u"bSimulationMode"] = False

        
    
        self._BContainer__AttributesVirtual.extend([u"ConnectModInfo", u"Selection_listKeys", u"lenDataDictionary", u"listCommands"])
        self._selection = []
        
     
        
    def get_selection(self):
        return self._selection

    def set_selection(self, selection):
        self._selection = selection

        
    selection = property(get_selection, set_selection)        
    
    def get_activeFolder(self):
        return self._activeFolder
    
    def set_activeFolder(self, activeFolder, options = None):
        self._activeFolder = activeFolder
    
    activeFolder = property(get_activeFolder, set_activeFolder)

    def get_rootGraphics(self):
        return self._rootGraphics 
        
    rootGraphics = property(get_rootGraphics)


    def get_latentGraphics(self):
        return self._latentGraphics
    
    def set_latentGraphics(self, latentGraphics, options = None):
        self._latentGraphics = latentGraphics
        
    latentGraphics = property(get_latentGraphics, set_latentGraphics)
    
    def execScript(self, script, bResetID = True):
        if bResetID:
            PyLinXDataObjects.PX_IdObject._PX_IdObject__ID = 0
        listScript = script.split("\n")
        for line in listScript:
            self.execCommand(line) 
            
    def execCommand(self, command):
        
        if self.get(u"LogLevel") > 0:
            print  self.activeFolder.get(u"path") + "> " +  command
        
        # Tracking of the commands
        self.__listCommands.append(command)

        
        if (type(command) == str) or (type(command) == unicode):
            command = command.strip()
            command = command.split(" ")
        
        strCommand = command[0]
        
        strExec = ""
        for i in range(1, len(command)):
            command_i = command[i]
            command_i_0 = command_i[0]
            
            # lists, sets, dicts
            if      (command_i_0 in (u"[", u"(", u"{")) \
                    or (command_i   in (u"True", u"False")): 
                strExec += (u"command[" + unicode(i) + u"] = " + command[i] + u"\n")
            # other cases
            else:
                if u"\"" in command_i:
                    command[i] = command_i.replace(u"\"", u"\\\"")
                strExec += (u"command[" + unicode(i) + u"] = u\"" + command[i] + u"\"\n")

        exec(strExec)
        
        if strCommand == u"set":
            return self.__execCommand_set(command[1:])
        elif strCommand == u"del":
            return self.activeFolder.delete(command[1:])
        elif strCommand == u"new":
            return self.__execCommand_new(command[1:])
        elif strCommand == u"select":
            return self.__execCommand_select(command[1:])
        
    def __execCommand_new(self, listCommands):
        
        strType = listCommands[0]
        dictConstructors = self.getb("dictConstructors")
        _type = dictConstructors[strType]
        dictKWArgs = {}
        listArgs = None
        if _type == PyLinXDataObjects.PX_PlottableConnector:
            if len(listCommands) > 1:
                if u"=" in listCommands[2]:
                    listArgs = [self.latentGraphics]
        if listArgs == None:
            listArgs = [self.activeFolder]
        for command in listCommands[1:]:
            if type(command) in (unicode, str):
                if u"=" in command:
                    command = command.split(u"=")
                    exec(u"val = " + command[1])
                    dictKWArgs[command[0]] = val
                else:
                    listArgs.append(command)
            else:
                listArgs.append(command)
        return  self.activeFolder.new(_type, * tuple(listArgs), **dictKWArgs)
     
    def __execCommand_set(self, command):
        
        path = command[0]
        if path[0] == u"@": 
            if path[1] == u".":
                command[0] = path[2:]
                return  self.__execCommand_set_Selection(command)
            elif path[1:8] == u"latent/":
                pathList = path.split(u".")
                setPath = u"." + path[7:]
                obj = self.latentGraphics.getObjFromPath(setPath)  
                return  obj.set(pathList[-1], command[-1])
            elif path[1:15] == u"mainController":
                pathList = path.split(u".")
                return  self.mainController.set(pathList[1],command[-1])
            else:
                raise Exception ("Error PyLinXMainController.__execCommand_set: Invalid Syntax!")
            
        else:
            listPath = path.split(u".")
            len_listPath = len(listPath)
            bAbsPath = (listPath[0] == u'/')
            bSubElement =  (listPath[0] == '')\
                        or (bAbsPath and len_listPath > 1)\
                        or (listPath[-1] == '' and len_listPath > 1)    
            if bSubElement:
                if len_listPath >1:
                    attr = listPath[-1]
                    element = self.activeFolder.getObjFromPath(path)
                    return  element.set(attr, command[-1])                  
            else:
                return  self.activeFolder.set(command[0], command[1])
       
    def __execCommand_set_Selection(self, command):
        for element in self.selection:
            if element.isAttr(command[0]):
                element.set(*tuple(command))

    def __execCommand_select(self, command):
        
        self.selection = [self.activeFolder.getb(key) for key in command]
        
        # reset ConnectorToModify if necessary
        len_selection = len(self.selection)
        if len_selection  > 0:
            if len_selection  > 1:
                return  self.set(u"ConnectorToModify", None)
            else:
                ConnectorToModify = self.get(u"ConnectorToModify")
                if self.selection[0] != ConnectorToModify:
                    return  self.set(u"ConnectorToModify", None)
                                
        self._activeFolder.set(u"ConnectorToModify", None )
        self._activeFolder.set(u"idxPointModified" , None )                   

    # Method that synchronizes the DataDictionary with the data hold for graphical representation in the DataViewer
    def sync(self):
        self.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"sync", ())       
        
    # Method that is executed when a run is stopped
    def stop_run(self):
        print "stop_run"
        self.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"stop_run", ())
        
    
    def get(self, attr):
    
        if attr == u"mainWindow":
            return self.__mainWindow
        elif attr == u"drawWidget":
            return self.__mainWindow.drawWidget
        elif attr == u"ConnectModInfo":
            return (super(PyLinXMainController, self).get(u"ConnectorToModify"),\
                    super(PyLinXMainController, self).get(u"idxPointModified"))
        elif attr == u"Selection_listKeys":
            return [ val.get(u"Name") for val in self._selection ]
        elif attr == u"lenDataDictionary":
            return len(self.getb(u"DataDictionary"))
        elif attr == u"listCommands":
            return self.__listCommands
        elif attr[0] == u"@":
            if attr[1] == u".":
                attr = attr[2:]
                if attr == u"types":
                    return self.__get_Selection_types()
                elif attr == u"bUnlock":
                    return self._get_Selection_bUnlock()
            else:
                raise Exception("Error PyLinXMainController.get: Syntax error.")
        else:
            return super(PyLinXMainController, self).get(attr)  
        
    def __get_Selection_types(self):
        
        setTypes = set([])
        for element in self.selection:
            types = inspect.getmro(type(element))
            setTypes = setTypes.union(set(types))
        return setTypes
        
    def _get_Selection_bUnlock(self):
        
        bUnlockResult = False
        for element in self.selection:
            bUnlock = element.get(u"bUnlock")
            bUnlockResult = bUnlock or bUnlockResult
        return bUnlockResult 
        
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
            super(PyLinXMainController, self).set(u"ConnectorToModify",self.mainController.activeFolder.getb(unicode(value[0])), options)
            super(PyLinXMainController, self).set(u"idxPointModified",value[1], options)
            
        elif attr == u"Selection_listKeys":
            self.selection = value
            
        elif attr == u"lenDataDictionary":
            self.__set_lenDataDictionary(value, options)
            
        else:
            return super(PyLinXMainController, self).set(attr,value, options)
        
        
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
                
                runEngine = PyLinXRunEngine.PX_CodeGenerator(self.mainController, self.__mainWindow)
                self.paste(runEngine, bForceOverwrite=True)
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.backgroundSim)
                self.__mainWindow.drawWidget.setPalette(pal)                
                self.__mainWindow.ui.actionRun.setEnabled(True)
                self.__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(True)
                self.__mainWindow.ui.actionNewElement.setEnabled(False)
                self.__mainWindow.ui.actionNewPlus.setEnabled(False)
                self.__mainWindow.ui.actionNewMinus.setEnabled(False)
                self.__mainWindow.ui.actionNewMultiplication.setEnabled(False)
                self.__mainWindow.ui.actionNewDivision.setEnabled(False)
                self.__mainWindow.ui.actionStop.setEnabled(True)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"widgetShow", ())
                return BContainer.BContainer.set(self,u"bSimulationMode", True, options)
            
            elif value == False:
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
                self.__mainWindow.drawWidget.setPalette(pal)
                self.__mainWindow.ui.actionRun.setEnabled(False)
                self.__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(False)
                self.__mainWindow.ui.actionNewElement.setEnabled(True)
                self.__mainWindow.ui.actionNewPlus.setEnabled(True)
                self.__mainWindow.ui.actionNewMinus.setEnabled(True)
                self.__mainWindow.ui.actionNewMultiplication.setEnabled(True)
                self.__mainWindow.ui.actionNewDivision.setEnabled(True)
                self.__mainWindow.ui.actionStop.setEnabled(False)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"widgetHide", ())
                return BContainer.BContainer.set(self,u"bSimulationMode", False, options)

    def __set_bConnectorPloting(self, value, options):
        
        if self.get(u"bConnectorPloting"):
            if value == False:
                self.latentGraphics.set(u"bConnectorPlotting", False)
                self.set(u"ConnectorPloting", None)
                self.set(u"idxToolSelected", PyLinXHelper.ToolSelected.none)
            return super(PyLinXMainController, self).set(u"bConnectorPloting",value, options)
        else:
            return super(PyLinXMainController, self).set(u"bConnectorPloting",value, options)        

    def __set_lenDataDictionary(self, value,options):
        if value == 0:
            DataDictionary = self.getb(u"DataDictionary")
            del DataDictionary
            DataDictionaryNew = BContainer.BDict({})
            DataDictionaryNew.set(u"Name", u"DataDictionary")
            DataDictionaryNew.set(u"DisplayName", u"DataDictionary")
            self._BContainer__Body[u"DataDictionary"] = DataDictionaryNew 
        else:
            raise Exception("Error PyLinXMainController.__set_lenDataDictionary: set-values other then 0 are not accepted!")
    
