'''
Created on 30.10.2014

@author: Waetzold Plaum
'''
# General Libraries - alphabedic order
import copy
import cProfile
import ctypes
import inspect
import jsonpickle
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys
import threading
import Queue
import codecs

# Project specific Libraries - alphabedic order
from PyLinXData import * 
from PyLinXGui import *
from PyLinXCodeGen import *
import PX_Templates as PX_Templ
import PyLinXData.PyLinXHelper as helper

class PyLinXMain(QtGui.QMainWindow):

    def __init__(self):
 
        super(PyLinXMain, self).__init__()
        
        reload(sys) 
        sys.setdefaultencoding('utf8')
        
        uiString = u".//Recources//Ui//PyLinX_v0_3.ui"
        self.ui = uic.loadUi(uiString)
        self.ui.setWindowIcon(QtGui.QIcon('pylinx.png'))
        self.ui.setWindowTitle('PyLinX')
        self.runThreadMessageQueue = Queue.Queue()
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('cleanlooks') )
        
        
        # ExampleData

        self.rootContainer = PyLinX_DataObjectsInternal.RootContainer(self)
        rootGraphics = PyLinXDataObjects.PX_PlottableObject("rootGraphics")
        self.rootContainer.paste(rootGraphics)

        testvar  = PyLinXDataObjects.PX_PlottableVarElement(u"TestVar_0", 150,90, 15 )
        testvar2 = PyLinXDataObjects.PX_PlottableVarElement(u"Variable_id4", 150,140, 15 )
        testvar3 = PyLinXDataObjects.PX_PlottableVarElement(u"Variable_id3", 400,100, 15 )
        plusOperator = PyLinXDataObjects.PX_PlottableBasicOperator(300,100, u"+")
        connector1 = PyLinXDataObjects.PX_PlottableConnector(testvar,plusOperator,  idxInPin=1)
        connector2 = PyLinXDataObjects.PX_PlottableConnector(testvar2,plusOperator,  idxInPin=0)
        connector3 = PyLinXDataObjects.PX_PlottableConnector(plusOperator,testvar3,  idxInPin=0)
        
        rootGraphics.paste(testvar, bHashById=True)
        rootGraphics.paste(testvar2, bHashById=True)
        rootGraphics.paste(testvar3, bHashById=True)        
        rootGraphics.paste(plusOperator, bHashById = True)        
        rootGraphics.paste(connector1, bHashById = True)
        rootGraphics.paste(connector2, bHashById = True)
        rootGraphics.paste(connector3, bHashById = True)
                 
        rootGraphics.set(u"bConnectorPloting", False)     
        self.rootContainer.paste(rootGraphics)
        

        # Configuration
        
        # idx that indicates the selected tool
        self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.rootContainer.set(u"ID_activeConnector", -1)
        # idx of the last selected Data-Viewer
        self.rootContainer.set(u"idxLastSelectedDataViewer", -1)
        rootGraphics.set(u"idxOutPinConnectorPloting", None)

        

        # run Engine
        
        self.runEngine = None
        
        
        # Drawing GUI
        
        # Events
        
        self.stopRunEvent = threading.Event()
        self.repaintEvent = threading.Event()
        
        
        scrollingArea = QtGui.QScrollArea()
        horizongalLayout2 = QtGui.QHBoxLayout()
        drawWidget = DrawWidget(self.rootContainer, self, self.repaintEvent )        
        self.drawWidget = drawWidget
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
        drawWidget.setAutoFillBackground(True)
        drawWidget.setPalette(pal)
        
        
        self.rootContainer.set(u"bSimulationMode", False)
        
        #drawWidget.setBaseSize(1500,480)
        horizongalLayout2.addWidget(drawWidget)
        scrollingArea.setLayout(horizongalLayout2)
        horizongalLayout2.setSizeConstraint(1)
        #scrollingArea.setLineWidth(6)
        scrollingArea.setContentsMargins(-30,-30,-30,-30)
        #scrollingArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #scrollingArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scrollingArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollingArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        
        # Has effect
        #scrollingArea.setFixedWidth(1000)
        scrollingArea.setMinimumWidth(500)
        self.ui.horizontalLayout.addWidget(scrollingArea)
        scrollingArea.setWidgetResizable(True)
        scrollingArea.setAutoFillBackground(False)
        #scrollingArea.setViewportMargins(0,0,0,0)
        self.ui.splitter.setStretchFactor(1,1)

        ## new UI
        if uiString == u"PyLinX_v0_4.ui":
            self.ui.tabWidget.setTabText(0,u"Elements")
            self.ui.tabWidget.setTabText(1,u"Libraries")
        
        #self.scene.addWidget(self.drawWidget)
        #self.ui.graphicsView.setScene(self.scene)

        self.ui.show()
        
        # Connecting Actions
        ####################
        
        # Menu-Bar
            
            # Programm
        
        self.ui.actionClose.triggered.connect(self.closeApplication)
        
            # Project
        
        self.ui.actionNewProject.triggered.connect(self.on_actionNewProject)
        self.ui.actionLoadProject.triggered.connect(self.on_actionLoadProject)
        self.ui.actionSave.triggered.connect(self.on_actionSave)
        self.ui.actionSave_As.triggered.connect(self.on_actionSave_As)
        
        # Tool-Bar
        
        self.ui.actionNewElement.triggered.connect(self.on_actionNewElement)
        self.ui.actionNewElement.setCheckable(True)
        self.ui.actionOsci.setCheckable(True)
        self.ui.actionNewPlus.triggered.connect(self.on_actionNewPlus)
        self.ui.actionNewMinus.triggered.connect(self.on_actionNewMinus)
        self.ui.actionNewMultiplication.triggered.connect(self.on_actionNewMultiplication)
        self.ui.actionNewDivision.triggered.connect(self.on_actionNewDivision)
        
        self.ui.actionOsci.triggered.connect(self.on_actionOsci)
        self.ui.actionNewPlus.setCheckable(True)
        self.ui.actionNewMinus.setCheckable(True)
        self.ui.actionNewMultiplication.setCheckable(True)
        self.ui.actionNewDivision.setCheckable(True)
        self.ui.actionRun.setEnabled(False)
        self.ui.actionOsci.setEnabled(False)
        self.ui.actionActivate_Simulation_Mode.triggered.connect(self.on_Activate_Simulation_Mode)
        self.ui.actionRun.triggered.connect(self.on_run)
        self.ui.actionStop.triggered.connect(self.on_stop)
        

        self.ui.resize(800,600)
        
        
######################
# Methods
#####################


# Callbacks
####################

    def closeApplication(self):
        
        print "CLOSE!"
        if QtGui.QMessageBox.question(None, u"", u"Soll PyLinX wirklich beendet werden?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)\
                 == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
            
    def on_actionNewElement(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newVarElement) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewPlus(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newPlus) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)

    def on_actionNewMinus(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newMinus) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewMultiplication(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newMultiplication) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewDivision(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newDivision) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)

            
    def on_actionSave(self):
        rootGraphics = self.rootContainer.getb(u"rootGraphics")
        if rootGraphics .isAttr(u"strSavePath"):
            strSavePath = rootGraphics.get(u"strSavePath")
            self.__saveProject(strSavePath)
        else:
            self.on_actionSave_As()

    
    def on_actionSave_As(self):
        if self.rootContainer.isAttr(u"strSavePath"):
            strSavePath_old = self.rootContainer.get(u"strSavePath")
            (strPath, strSavePath_old_file) = os.path.split(strSavePath_old)
        else:
            strPath = os.getcwd()
        strSavePath= self.__showFileSaveSelectionDialog(strPath, bDir = False, strExt = u"pson", strHeader =u"Select File to save Project...")
        (strSavePath_base,strSavePath_ext) = os.path.splitext(strSavePath)
        if not  strSavePath_ext == u".pson":
            strSavePath = strSavePath_base + u".pson"
        self.__saveProject(strSavePath)

     
    def __saveProject(self, strSavePath):    
        
        #_file = open(strSavePath, "w")
        _file = codecs.open(strSavePath, encoding='utf-8', mode='w')
        project = self.rootContainer.getb(u"rootGraphics")
        project._BContainer__parent = None
        #pickledObject = jsonpickle.encode(project, keys=True) 
        pickledObject = jsonpickle.encode(project, keys=True, unpicklable=False)
        _file.write(pickledObject)
        _file.close()
        rootGraphics = self.rootContainer.getb(u"rootGraphics")
        rootGraphics.set(u"strSavePath", strSavePath)  

   
    def on_actionLoadProject(self):
        strPath = os.getcwd()
        strSavePath= self.__showFileSelectionLoadDialog(strPath, bDir = False,strHeader ="Select File to load Project...")  
        _file = open(strSavePath)
        
        newProject = jsonpickle.decode(_file.read(), keys=True)
        oldProject = self.rootContainer.getb(u"rootGraphics")
        self.rootContainer.paste(newProject,u"rootGraphics",  bForceOverwrite = True)
        self.drawWidget.newProject(newProject)
        del oldProject
        self.rootContainer.set(u"bSimulationMode", False)
        maxID = newProject.getMaxID()
        PyLinXDataObjects.PX_IdObject._PX_IdObject__ID = maxID + 1
        self.drawWidget.repaint()
    
    def on_actionNewProject(self):
        rootGraphicsNew = PyLinXDataObjects.PX_PlottableObject(u"rootGraphics")
        self.rootContainer.delete(u"rootGraphics")
        self.rootContainer.set(u"bSimulationMode", False)
        self.rootContainer.paste(rootGraphicsNew)
        self.drawWidget.activeGraphics = rootGraphicsNew
        self.drawWidget.repaint()

    def __showFileSaveSelectionDialog(self,strPath = None, bDir = False, strExt= None, strHeader = None):
        
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = u"Select Directory..."
            else:
                strHeader = u"Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getSaveFileName(self.ui,strHeader,strPath,strExt))
    

    def __showFileSelectionLoadDialog(self, strPath = None, bDir = False, strExt = u"", strHeader = None):
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = u"Select Directory..."
            else:
                strHeader = u"Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getOpenFileName(self.ui,strHeader,strPath,strExt))
        
        
    def on_Activate_Simulation_Mode(self):
        
        bSimulationMode = self.rootContainer.get(u"bSimulationMode")
        if bSimulationMode:
            self.rootContainer.set(u"bSimulationMode", False)
        else:
            runEngine = PyLinXRunEngine.PX_CodeGenerator(self.rootContainer, self)
            self.rootContainer.paste(runEngine, bForceOverwrite=True)
            self.rootContainer.set(u"bSimulationMode", True)
            
        self.drawWidget.repaint()
        
    def on_run(self):
        
        self.runEngine = self.rootContainer.getb(u"PX_CodeGeerator")
        #self.stopRunEvent.clear()
        self.runEngine.startRun(self.drawWidget, self.stopRunEvent, self.repaintEvent)
        self.rootContainer.set(u"bSimulationRunning", True)
        
    def on_actionOsci(self):
        
        if self.rootContainer.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.newVarDispObj) 
        else:
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_stop(self):
        self.runThreadMessageQueue.put(u"stopRun")
        
        
class DrawWidget (QtGui.QWidget):

    def __init__(self, rootContainer, mainWindow, repaintEvent):
        super(DrawWidget, self).__init__()
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, PX_Templ.color.background)
        self.setPalette(p)
        self.repaintEvent = repaintEvent
        self.rootContainer = rootContainer
        self.rootGraphics = rootContainer.getb(u"rootGraphics")
        self.activeGraphics = self.rootGraphics
        self.activeGraphics.set(u"ConnectorToModify", None)
        self.activeGraphics.set(u"idxPointModified" , None)
        self.mainWindow = mainWindow
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setMouseTracking(True)
        # Why does this not work?
        self.setMinimumSize(1000,600)
        
        self.setFocus(QtCore.Qt.PopupFocusReason) 
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # set button context menu policy
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        

        # create context menu
        self.popMenu_SimulationMode = QtGui.QMenu(self)
        iconMeasure   = QtGui.QIcon(".//Recources//Icons//measure24.png")
        iconStimulate = QtGui.QIcon(".//Recources//Icons//stimulate24.png")
        self.actionMeasure   = QtGui.QAction(iconMeasure,    u"Measure", self)
        self.actionStimulate = QtGui.QAction(iconStimulate , u"Stimulate", self)
        self.actionMeasure.setCheckable(True)
        self.actionStimulate.setCheckable(True)
        self.popMenu_SimulationMode.addAction(self.actionStimulate)
        self.popMenu_SimulationMode.addAction(self.actionMeasure)

        self.setEnabled(True)
        
        # Connecting signals
        self.connect(self, QtCore.SIGNAL("stopSimulation"), self.on_stop_simulation)        
        self.connect(self, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menu)
        self.connect(self, QtCore.SIGNAL("signal_repaint"), self.repaint)

    def on_stop_simulation(self):
        RunConfigDictionary = self.rootContainer.getb(u"RunConfigDictionary")
        RunConfigDictionary[u"bSimulationRunning"] = False        
            
    def on_context_menu(self, coord):
        # show context menu
        bSimulationMode = self.rootContainer.get(u"bSimulationMode")
        if bSimulationMode:
            objInFocus = self.activeGraphics.getObjectInFocus(coord)
            if len(objInFocus) > 0:
                var = objInFocus[0] 
                types = inspect.getmro(type(var))
                if PyLinXDataObjects.PX_PlottableVarElement in types:
                    bStimulate  = var.get(u"bStimulate")
                    bMeasure    = var.get(u"bMeasure")
                    self.actionMeasure.setChecked(bMeasure)
                    self.actionStimulate.setChecked(bStimulate)
                    self.popMenu_SimulationMode.exec_(self.mapToGlobal(coord))
                    actionMeasureIsChecked = self.actionMeasure.isChecked()
                    actionStimulateIsChecked = self.actionStimulate.isChecked()
                    
                    if actionStimulateIsChecked and not bStimulate:
                        result = PX_Dialogue_SimpleStimulate.PX_Dialogue_SimpleStimulate.getParams(self, var, self)
                        if result == False:
                            self.actionStimulate.setChecked(False)
                            actionStimulateIsChecked = False
                    
                    if actionMeasureIsChecked and not bMeasure:
                        result = PX_Dialogue_SelectDataViewer.PX_Dialogue_SelectDataViewer.getParams( self,\
                                                                                                      var,\
                                                                                                      self.rootContainer,\
                                                                                                      self)
                        if result == False:
                            self.actionMeasure.setChecked(False)
                            actionMeasureIsChecked = False
                    
                    
                    var.set(u"bStimulate",actionStimulateIsChecked)    
                    
                    self.repaint() 

    def newProject(self, rootGraphics):
        self.rootGraphics   = rootGraphics
        self.activeGraphics = rootGraphics
    
    def paintEvent(self, event = None):
        self.activeGraphics.write(self,PX_Templ.Plot_Target.Gui)
        
    def keyPressEvent(self, qKeyEvent):

        def __keyPressEvent_delete():
        
            objectsInFocus = list(self.activeGraphics.objectsInFocus)
            setDelete = set([])
            # deleting elements and preparing a list of connectors, which has to be deleted 
            for key in self.activeGraphics._BContainer__Body:    
                element = self.activeGraphics.getb(key)
                bUnlock = element.get(u"bUnlock")
                types = inspect.getmro(type(element))
                if (PyLinXDataObjects.PX_PlottableConnector in types) and bUnlock:
                    # deleting all connectors which are connected to an object, that is deleted
                    elem0 = element.elem0
                    if elem0 in objectsInFocus:
                        setDelete.add(element.ID)
                    elem1 = element.elem1
                    if elem1 in objectsInFocus:
                        setDelete.add(element.ID)
                # deleting all objects in focus
                if element in objectsInFocus and bUnlock:
                    setDelete.add(element.ID)
                    
            # removing the deleted connectors from the list of connected pins of the connected elements
            for _id in setDelete:
                element = self.activeGraphics.getb(_id)
                types = inspect.getmro(type(element))
                if PyLinXDataObjects.PX_PlottableConnector in types:
                    idxInPin = element.idxInPin
                    idxOutPin = element.idxOutPin
                    elem0 = element.elem0
                    elem1 = element.elem1
                    setIdxConnectedOutPins = elem0.get(u"setIdxConnectedOutPins")
                    setIdxConnectedInPins  = elem1.get(u"setIdxConnectedInPins")
                    if idxOutPin in setIdxConnectedOutPins: 
                        setIdxConnectedOutPins.remove(idxOutPin)
                    if idxInPin in setIdxConnectedInPins: 
                        setIdxConnectedInPins.remove(idxInPin)
                    elem0.set(u"setIdxConnectedOutPins", setIdxConnectedOutPins)
                    elem1.set(u"setIdxConnectedInPins", setIdxConnectedInPins)
                    
            DataDictionary = self.rootContainer.getb(u"DataDictionary")
            bDictionary = (DataDictionary != None)
            for element in setDelete:
                elementObject = self.activeGraphics.getb(element)
                name = elementObject.get(u"Name")
                if bDictionary:
                    
                    if name in DataDictionary:
                        DataDictionary.pop(name)
                # This is not nice. But usint "__del__" method or using of contexts did it not for me
                if elementObject.isAttrTrue(u"bExitMethod"):
                    elementObject._exit_()
                self.activeGraphics.delete(element)
            self.repaint()

       
        #################
        # Main Method
        #################
        
        # Deleting Objects

        #bSimulationMode = self.rootContainer.get("bSimulationMode")
        #if not bSimulationMode:
               
        if qKeyEvent.key() == QtCore.Qt.Key_Delete:
            __keyPressEvent_delete()
        else:
            super(DrawWidget, self).keyPressEvent(qKeyEvent)
        
#         else: 
#             pass 
    
    def mousePressEvent(self, coord):

        def mousePressEvent_tool_none():

            objInFocusOld = list(self.activeGraphics.objectsInFocus)
            objInFocus = self.activeGraphics.getObjectInFocus(coord)
            #print "coord.x(): ", coord.x() 
            #print "coord.y(): ", coord.y()
            #print "objInFocus: ", objInFocus
            #print "objInFocusOld: ", objInFocusOld
            
            if len(set(objInFocus).intersection(set(objInFocusOld))) > 0:
                pass
            else:      
                self.activeGraphics.objectsInFocus = objInFocus
                if len(objInFocus) == 0:
                    highlightObject = PyLinXDataObjects.PX_LatentPlottable_HighlightRect(coord.x(), coord.y())
                    self.activeGraphics.paste(highlightObject)
                    
            # move lines of connectors
            len_objectsInFocus  = len(objInFocus)
            if len_objectsInFocus == 0:
                pass
            elif len_objectsInFocus == 1:
                activeObject = objInFocus[0]
                
                if activeObject.isAttr(u"listPoints"):
                    listPoints = list(activeObject.get(u"listPoints"))
                    objectInFocus = objInFocus[0]
                    shape = objectInFocus.get(u"Shape")
                    elem0 = objectInFocus.elem0
                    #X_obj = elem0.X
                    #Y_obj = elem0.Y
                    #idxPolygons = helper.point_inside_polygon(x - X_obj , y - Y_obj, shape)
                    #print "x: ", x
                    #print "y: ", y
                    idxPolygons = helper.point_inside_polygon(x, y, shape)
                    if len(idxPolygons) == 1:
                        idxPolygon = idxPolygons[0]
                        if idxPolygon > 0:
                            self.activeGraphics.set(u"ConnectorToModify", activeObject )
                            self.activeGraphics.set(u"idxPointModified" , idxPolygon -1)
                            
            # Connecting Elements
            bConnectorPloting = self.rootGraphics.get(u"bConnectorPloting")
            if bConnectorPloting:
                # Determining if there is a endpoint in focus
                keys = self.activeGraphics.getChildKeys()
                objInFocus = None
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if PyLinXDataObjects.PX_PlottableElement in types and element.get(u"bUnlock"): 
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if objInFocus != None:
                            if len(idxPin) == 1:
                                idxPin = idxPin[0]
                            break  
                if objInFocus == None:
                
                    # case there is no second element
                    proxyElem = self.activeGraphics.getb(u"PX_PlottableProxyElement")
                    ConnectorPloting = self.rootGraphics.get(u"ConnectorPloting")
                    X0 = ConnectorPloting.X
                    Y0 = ConnectorPloting.Y
                    listPoints = list(ConnectorPloting.get(u"listPoints"))
                    len_listPoints = len(listPoints)
                    if len_listPoints > 1:
                        lastPoint_minus_1 = listPoints[-2]
                    else:
                        lastPoint_minus_1 = sys.maxint
                    x_diff = X - X0
                    y_diff = Y - Y0 
                    if len_listPoints % 2 == 0:
                        if abs(x_diff - lastPoint_minus_1) < 12 and len_listPoints > 1:
                            listPoints[-1] = y_diff
                        else:
                            listPoints.append(x_diff)
                    else:
                        if abs(y_diff - lastPoint_minus_1) < 12 and len_listPoints > 1:
                            listPoints[-1] = x_diff
                        else:
                            listPoints.append(y_diff)
                    ConnectorPloting.set(u"listPoints", listPoints)
                    proxyElem.X = x
                    proxyElem.Y = y
                    
                else:
                    # idxPin determined as the index of Pins in focus
                    setIdxConnectedInPins = objInFocus.get(u"setIdxConnectedInPins")
                    if idxPin in setIdxConnectedInPins:
                        bConnect = False
                    else:
                        bConnect = True
                
                    #print u"bConnect: ", bConnect
                    if bConnect:
                        # connecting the connector to the second element                
                        for key in keys:        
                            element = self.activeGraphics.getb(key)
                            types = inspect.getmro(type(element))
                            if PyLinXDataObjects.PX_PlottableProxyElement in types:
                                self.activeGraphics.delete(key)
                                #print "Proxy Deleted!"
                                break
                        ConnectorPloting = self.rootGraphics.get(u"ConnectorPloting")
                        ConnectorPloting.elem1 = objInFocus
                        #ConnectorPloting.idxInPin = idxPin 
                        # TODO: the convention for the idx of input Puns is not consistent ?
                        #print "-->idxPin: ", idxPin
                        #print "id(0): ", id(ConnectorPloting) 
                        ConnectorPloting.idxInPin = idxPin
                        #print "id(1): ", id(ConnectorPloting)
                        setIdxConnectedInPins.add(idxPin)
                        objInFocus.set(u"setIdxConnectedInPins", setIdxConnectedInPins)
                        self.rootGraphics.set(u"bConnectorPloting", False)
                        objInFocus.idxActiveInPins = []
                        
                        elem0 = ConnectorPloting.elem0
                        setIdxConnectedOutPins = elem0.get(u"setIdxConnectedOutPins")
                        idxOutPinConnectorPloting = self.rootGraphics.get(u"idxOutPinConnectorPloting")
                        setIdxConnectedOutPins.add(idxOutPinConnectorPloting)
                        elem0.set(u"setIdxConnectedOutPins", setIdxConnectedOutPins)
                        self.rootGraphics.set(u"idxOutPinConnectorPloting", None)
            
            if not bConnectorPloting: # and objInFocus.get("bUnlock"):
                #element = objInFocus[0]
                #print "element.get(\"bUnlock\"): ", element.get("bUnlock")
                #if element.get("bUnlock"):
                # Starting connecting Elements
                keys = self.activeGraphics.getChildKeys()
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if (PyLinXDataObjects.PX_PlottableElement in types) \
								and element.get(u"bUnlock"):
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if len(idxPin) > 0:
                            idxPin = idxPin[0]                         
                        if objInFocus != None and (idxPin > -1):
                            proxyElem = PyLinXDataObjects.PX_PlottableProxyElement(x,y)
                            self.activeGraphics.paste(proxyElem)
                            newConnector = PyLinXDataObjects.PX_PlottableConnector(element, proxyElem)
                            self.activeGraphics.paste(newConnector,  bHashById=True)
                            self.rootGraphics.set(u"bConnectorPloting", True)
                            self.rootGraphics.set(u"idxOutPinConnectorPloting", idxPin)
                            self.rootGraphics.set(u"ConnectorPloting", newConnector)
                            
        def mousePressEvent_tool_newVarElement():     
            n = PyLinXDataObjects.PX_IdObject._PX_IdObject__ID + 1
            var = PyLinXDataObjects.PX_PlottableVarElement(u"Variable_id" + unicode(n),X,Y, 15 )
            self.activeGraphics.paste(var, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
        def mousePressEvent_tool_newPlus():  
            plus = PyLinXDataObjects.PX_PlottableBasicOperator(X,Y,u"+")
            self.activeGraphics.paste(plus, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
        def mousePressEvent_tool_newMinus():  
            minus = PyLinXDataObjects.PX_PlottableBasicOperator(X,Y,u"-")
            self.activeGraphics.paste(minus, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)

        def mousePressEvent_tool_newMultiplication():  
            multiplication = PyLinXDataObjects.PX_PlottableBasicOperator(X,Y,u"*")
            self.activeGraphics.paste(multiplication, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
        def mousePressEvent_tool_newDivide():  
            division = PyLinXDataObjects.PX_PlottableBasicOperator(X,Y,u"/")
            self.activeGraphics.paste(division, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)            
            
        def mousePressEvent_tool_newVarDispObj():
            newVarDispObj = PyLinXDataObjects.PX_PlottableVarDispElement(X,Y, self.rootContainer)
            self.activeGraphics.paste(newVarDispObj, bHashById=True)
            self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionOsci.setChecked(False)
            
                   
        #################
        # Main Method
        #################
        
        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.rootContainer.get(u"idxToolSelected")
        bSimulationMode = self.rootContainer.get(u"bSimulationMode")
        
        self.rootContainer.set(u"px_mousePressedAt_X", X)
        self.rootContainer.set(u"px_mousePressedAt_Y", Y)

        if toolSelected == helper.ToolSelected.none:
            mousePressEvent_tool_none()

        
        if not bSimulationMode:
    
#            if toolSelected == helper.ToolSelected.none:
#                mousePressEvent_tool_none()
                
            if toolSelected == helper.ToolSelected.newVarElement:
                mousePressEvent_tool_newVarElement()
    
            elif toolSelected == helper.ToolSelected.newPlus:
                mousePressEvent_tool_newPlus()
                
            elif toolSelected == helper.ToolSelected.newMinus:
                mousePressEvent_tool_newMinus()

            elif toolSelected == helper.ToolSelected.newMultiplication:
                mousePressEvent_tool_newMultiplication()

            elif toolSelected == helper.ToolSelected.newDivision:
                mousePressEvent_tool_newDivide()

            

        else:
            
            if toolSelected == helper.ToolSelected.newVarDispObj:
                mousePressEvent_tool_newVarDispObj()
            
        self.repaint()
                   
    def mouseMoveEvent(self,coord):

        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.rootContainer.get(u"idxToolSelected")

        #bSimulationMode = self.rootContainer.get("bSimulationMode")
        
        #if not bSimulationMode:
        
        if toolSelected == helper.ToolSelected.none:

            # Moving objects
            objectsInFocus = list(self.activeGraphics.objectsInFocus)
            #print "objectsInFocus : ", objectsInFocus 
            if objectsInFocus != []:
                px_mousePressedAt_X = self.rootContainer.get(u"px_mousePressedAt_X")
                px_mousePressedAt_Y = self.rootContainer.get(u"px_mousePressedAt_Y")
                if px_mousePressedAt_X != sys.maxint:
                    xOffset = X - px_mousePressedAt_X 
                    yOffset = Y - px_mousePressedAt_Y 
                    for activeObject in objectsInFocus:
                        #print "bUnlock: ", activeObject.get("bUnlock")
                        if not activeObject.get(u"bUnlock"):
                            continue
                           
                        ConnectorToModify = self.activeGraphics.get(u"ConnectorToModify")
                        # move objects that have coordinates
                        types = inspect.getmro(type(activeObject))
                        if (PyLinXDataObjects.PX_PlottableElement in types):
                            X_obj = activeObject.X
                            Y_obj = activeObject.Y
                            newX = X_obj + xOffset 
                            newY = Y_obj + yOffset 
                            activeObject.X = newX
                            activeObject.Y = newY
                        
                        # move lines of connectors 
                        elif ConnectorToModify  != None:
                            idxPointModified = self.activeGraphics.get(u"idxPointModified")
                            listPoints = list(ConnectorToModify.get(u"listPoints"))
                            value = listPoints[idxPointModified]
                            if idxPointModified % 2 == 0:
                                value = value + xOffset 
                            else:
                                value = value + yOffset
                            listPoints[idxPointModified] = 10 * round( 0.1 * float(value))
                            activeObject.set(u"listPoints", listPoints)                 
                    
                    self.rootContainer.set(u"px_mousePressedAt_X", X)
                    self.rootContainer.set(u"px_mousePressedAt_Y", Y)            
                    
            # Ploting the selection frame
            if self.activeGraphics.isInBody(u"HighlightObject"):
                highlightObject = self.activeGraphics.getb(u"HighlightObject")
                highlightObject.set(u"X1", coord.x())
                highlightObject.set(u"Y1", coord.y())

            keys = self.activeGraphics.getChildKeys()
            for key in keys:
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if PyLinXDataObjects.PX_PlottableElement  in types:
                    element.isPinInFocus(x,y)
                    
            # change coordinates of the proxyElement, that is a placeholder for the finally connected element
            bConnectorPloting = self.rootGraphics.get(u"bConnectorPloting")
            #print "bConnectorPloting: ", bConnectorPloting 
            if bConnectorPloting:
                proxyElem = self.activeGraphics.getb(u"PX_PlottableProxyElement")
                proxyElem.X = X
                proxyElem.Y = Y   
            self.repaint()
            #else:
        #    pass     
    
    def mouseReleaseEvent(self,coord):
        
        def __mouseReleaseEvent_ToolSelNone():
            
            X = coord.x()
            Y = coord.y()
            px_mousePressedAt_X = self.rootContainer.get(u"px_mousePressedAt_X")
            px_mousePressedAt_Y = self.rootContainer.get(u"px_mousePressedAt_Y")
            bSimulationMode = self.rootContainer.get(u"bSimulationMode")
            if px_mousePressedAt_X != sys.maxint and px_mousePressedAt_Y != sys.maxint: 
                polygons = [[(X,Y), (X,px_mousePressedAt_Y ), (px_mousePressedAt_X,px_mousePressedAt_Y),(px_mousePressedAt_X,Y)]]
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    if element.isAttr(u"Shape"):
                        bFocus = True
                        shape = element.get(u"Shape")
                        #X_obj = element.X
                        #Y_obj = element.Y
                        
                        for polygon in shape:
                            if polygon != None:
                                for point in polygon:
                                    #idxCorner = helper.point_inside_polygon(X_obj + point[0], Y_obj + point[1],polygons)
                                    idxCorner = helper.point_inside_polygon(point[0], point[1],polygons)
                                    if len(idxCorner) == 0:
                                        bFocus = False
                        if bFocus:
                            objectsInFocus = list(self.activeGraphics.objectsInFocus )
#                             bOnlyVisibleInSimMode = element.get("bOnlyVisibleInSimMode")
#                             #print "bOnlyVisibleInSimMode: ", bOnlyVisibleInSimMode
#                             if (bOnlyVisibleInSimMode and bSimulationMode) or \
#                                 not bOnlyVisibleInSimMode and not bSimulationMode:
                            if element.get(u"bUnlock"):
                                objectsInFocus.append(element)
                            self.activeGraphics.objectsInFocus = objectsInFocus
                            #print "objectsInFocus: ", objectsInFocus
            self.activeGraphics.set(u"ConnectorToModify", None )
            self.activeGraphics.set(u"idxPointModified" , None )              
        
        ####################
        # Main method
        ####################
        
        keys = self.activeGraphics.getChildKeys()       
        toolSelected = self.rootContainer.get(u"idxToolSelected")        

        #bSimulationMode = self.rootContainer.get("bSimulationMode")
        #if not bSimulationMode:
       
        # selecting Elements
        
        if toolSelected == helper.ToolSelected.none:
            __mouseReleaseEvent_ToolSelNone()
                        
        for key in keys:
            if self.activeGraphics.getb(key).get(u"bLatent") == True:
                self.activeGraphics.delete(key)
             
        self.rootContainer.set(u"px_mousePressedAt_X", sys.maxint)
        self.rootContainer.set(u"px_mousePressedAt_Y", sys.maxint)  
            
        #else:
        #    pass     
        self.repaint()
           
    def mouseDoubleClickEvent(self, coord):
        
        def bDialogue(X,Y,strShape, element):
            
            bDialog = False
            shape = element.get(strShape)
           
            if shape != None:
                idxPolygon = helper.point_inside_polygon(X , Y,shape)
                bDialog = not (len(idxPolygon) == 0)
            return bDialog
        
        bSimulationMode = self.rootContainer.get(u"bSimulationMode")
        if not bSimulationMode:
            bConnectorPloting = self.rootGraphics.get(u"bConnectorPloting")
            if bConnectorPloting: 
                keys = self.activeGraphics.getChildKeys()
                for key in keys:        
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if PyLinXDataObjects.PX_PlottableProxyElement in types:
                        self.activeGraphics.delete(key)
                        break
                ConnectorPloting = self.rootGraphics.get(u"ConnectorPloting")
                self.activeGraphics.delete( ConnectorPloting.ID )
                self.rootGraphics.set(u"bConnectorPloting", False)
                self.rootContainer.set(u"idxToolSelected", helper.ToolSelected.none)
                self.repaint()
                
        else:
            X = coord.x()
            Y = coord.y()
            keys = self.activeGraphics.getChildKeys()
            bFocusStimulate = False
            bFocusMeasure = False
            bFocus = False
            for key in keys:
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if PyLinXDataObjects.PX_PlottableVarElement in types:
                    bFocusStimulate = bDialogue(X,Y,u"Shape_stim", element)
                    bFocusMeasure = bDialogue(X,Y,u"Shape_meas", element)
                    if bFocusStimulate or bFocusMeasure:
                        break                    
                if PyLinXDataObjects.PX_PlottableVarDispElement in types:
                    bFocus  =  bDialogue(X,Y, u"Shape", element)
                    if bFocus:
                        break
            
            if bFocusStimulate:
                values = PX_Dialogue_SimpleStimulate.PX_Dialogue_SimpleStimulate.getParams(self, element, self)          
                return 
            if bFocusMeasure:
                values = PX_Dialogue_SelectDataViewer.PX_Dialogue_SelectDataViewer.getParams(self,\
                                                                                                element, \
                                                                                                self.rootContainer, \
                                                                                                self)
                return 
            
            if bFocus:
                if PyLinXDataObjects.PX_PlottableVarDispElement in types:
                    element.set(u"bVarDispVisible", True)
                    print u"idxDataDispObj:",  element.get(u"idxDataDispObj")
def run():
    app = QtGui.QApplication(sys.argv)
    obj = PyLinXMain()   
    app.exec_()
    
    
if __name__ == '__main__':
    
    PROFILE = False
    
    if PROFILE:
        cProfile.run('run()')
    else:
        run()
