'''
Created on 18.08.2015

@author: Waetzold Plaum
'''

# General Libraries - alphabedic order
import copy
import ctypes 
import inspect
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys

# Project specific Libraries - alphabedic order
from PyLinXData import * 
import PX_Dialogue_SelectDataViewer
import PX_Dialogue_SimpleStimulate
import PX_Templates as PX_Templ
import PyLinXData.PyLinXHelper as helper

class DrawWidget (QtGui.QWidget):

    def __init__(self, mainController, mainWindow, repaintEvent):
        super(DrawWidget, self).__init__()
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, PX_Templ.color.background)
        self.setPalette(p)
        self.repaintEvent = repaintEvent
        self.mainController = mainController
        self.rootGraphics = mainController.getb(u"rootGraphics")
        self.latentGraphics = mainController.latentGraphics 
        self.activeGraphics = self.rootGraphics
        self.mainController.set(u"ConnectorToModify", None)
        self.mainController.set(u"idxPointModified" , None)
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
        iconMeasure   = QtGui.QIcon(u".//Recources//Icons//measure24.png")
        iconStimulate = QtGui.QIcon(u".//Recources//Icons//stimulate24.png")
        self.actionMeasure   = QtGui.QAction(iconMeasure,    u"Measure", self)
        self.actionStimulate = QtGui.QAction(iconStimulate , u"Stimulate", self)
        self.actionMeasure.setCheckable(True)
        self.actionStimulate.setCheckable(True)
        self.popMenu_SimulationMode.addAction(self.actionStimulate)
        self.popMenu_SimulationMode.addAction(self.actionMeasure)

        self.setEnabled(True)
        
        # Connecting signals       
        self.connect(self, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menu)
        self.connect(self, QtCore.SIGNAL("signal_repaint"), self.repaint)

    def on_context_menu(self, coord):
        # show context menu
        bSimulationMode = self.mainController.get(u"bSimulationMode")
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
                        result = PX_Dialogue_SimpleStimulate.PX_Dialogue_SimpleStimulate.getParams(self, var,self.mainController, self)
                        if result == False:
                            self.actionStimulate.setChecked(False)
                            actionStimulateIsChecked = False
                    
                    if actionMeasureIsChecked and not bMeasure:
                        result = PX_Dialogue_SelectDataViewer.PX_Dialogue_SelectDataViewer.getParams( self,var,self.mainController,self)
                        if result == False:
                            self.actionMeasure.setChecked(False)
                            actionMeasureIsChecked = False
                     
                    # TODO COMMAND
                    var.set(u"bStimulate",actionStimulateIsChecked)    
                    
                    self.repaint() 

    def newProject(self, rootGraphics):
        self.rootGraphics   = rootGraphics
        self.activeGraphics = rootGraphics
    
    def paintEvent(self, event = None):
        self.activeGraphics.write(self,PX_Templ.Plot_Target.Gui)
        self.latentGraphics.write(self,PX_Templ.Plot_Target.Gui)
        
    def keyPressEvent(self, qKeyEvent):

        def __keyPressEvent_delete():
        
            objectsInFocus = list(self.mainController.selection)
            setDel = set([])
            # deleting elements and preparing a list of connectors, which has to be deleted 
            for key in self.activeGraphics._BContainer__Body:    
                element = self.activeGraphics.getb(key)
                bUnlock = element.get(u"bUnlock")
                if bUnlock: 
                    types = inspect.getmro(type(element))
                    if (PyLinXDataObjects.PX_PlottableConnector in types):
                        # deleting all connectors which are connected to an object, that is deleted
                        elem0 = element.elem0
                        if elem0 in objectsInFocus:
                            setDel.add(unicode(element.ID))
                        elem1 = element.elem1
                        if elem1 in objectsInFocus:
                            setDel.add(unicode(element.ID))
                    # deleting all objects in focus
                    if (element in objectsInFocus):
                        setDel.add(element.get(u"Name"))
            # writing the command
            command = u"del"
            for delItem in setDel:
                command += " " + unicode(delItem)
                           
            self.mainController.execCommand(command) 
            self.repaint()

       
        #################
        # Main Method
        #################
        
        # Deleting Objects      
        if qKeyEvent.key() == QtCore.Qt.Key_Delete:
            __keyPressEvent_delete()
        else:
            super(DrawWidget, self).keyPressEvent(qKeyEvent)
    
    def mousePressEvent(self, coord):

        def mousePressEvent_tool_none():

            objInFocusOld = list(self.mainController.selection)
            objInFocus = self.activeGraphics.getObjectInFocus(coord)
            
            # Create HighlightObject if necessary.
            #  This is not done by command since
            #  the highlight rect is not considered
            #  to be part of the data
            # selecting clicked element by command
            #######################################
            
            len_objectsInFocus  = len(objInFocus)
            if len(set(objInFocus).intersection(set(objInFocusOld))) == 0:
                if len_objectsInFocus == 0:
                    if len(self.mainController.selection) > 0:
                        self.mainController.execCommand(u"select")
                    PyLinXDataObjects.PX_LatentPlottable_HighlightRect(self.latentGraphics,coord.x(), coord.y())
                else:
                    if set(objInFocus) != set(self.mainController.selection):                
                        usttObj = [obj.get("Name") for obj in objInFocus]
                        self.mainController.execCommand(u"select " + u" ".join(usttObj)) 
                

                    
            # move lines of connectors
            ##########################
            
            # Detect index of line to modify and save it in active graphics
            if len_objectsInFocus == 1:
                activeObject = objInFocus[0]
                if activeObject.isAttr(u"listPoints"):
                    listPoints = list(activeObject.get(u"listPoints"))
                    objectInFocus = objInFocus[0]
                    shape = objectInFocus.get(u"Shape")
                    elem0 = objectInFocus.elem0
                    idxPolygons = helper.point_inside_polygon(x, y, shape)
                    if len(idxPolygons) == 1:
                        idxPolygon = idxPolygons[0]
                        if idxPolygon > 0:
                            # not sent via ustr-Command, since this information is only cached at the mainController
                            # for the final command. No data is changed here.
                            self.mainController.set(u"ConnectModInfo", (activeObject.get("ID") ,idxPolygon - 1 ))
                            return 
                            
            # Connecting Elements
            #####################
            
            bConnectorPloting = self.mainController.get(u"bConnectorPloting")
            # connecting has been started yet
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
                
                # case connecting of elements is not finished yet. No second Element has been clicked
                if objInFocus == None:                    
                    strVal = repr((x,y)).replace(u" ", u"")
                    #strCommand_xy = u"set ./PX_PlottableProxyElement.xy " + strVal
                    strCommand_xy = u"set @latent/PX_PlottableProxyElement.xy " + strVal
                    self.mainController.execCommand(strCommand_xy)
                
                # Case connecting of elements is finished. Second Element is clicked
                else:
                    # idxPin determined as the index of Pins in focus
                    setIdxConnectedInPins = objInFocus.get(u"setIdxConnectedInPins")
                    #print "setIdxConnectedInPins: ", setIdxConnectedInPins 
                    if not (idxPin in setIdxConnectedInPins):
                        ConnectorPloting = self.mainController.get(u"ConnectorPloting")
                        connectorName = ConnectorPloting.get(u"Name")
                        #ustrCommand = u"set ./" + connectorName + ".connectInfo (\"" + objInFocus.get(u"Name") + u"\"," + unicode(idxPin) + u")"
                        ustrCommand = u"set @latent/" + connectorName + ".connectInfo (\"" + objInFocus.get(u"Name") + u"\"," + unicode(idxPin) + u")"
                        self.mainController.execCommand(ustrCommand)
                                               
            # connecting has not been started yet
            else:
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
                            strCommand = u"new connector " + unicode( element.ID ) + u" idxOutPinConnectorPloting=" + unicode(idxPin)
                            self.mainController.execCommand(strCommand)
                                      
        def mousePressEvent_tool_newVarElement():     
            n = PyLinXDataObjects.PX_IdObject._PX_IdObject__ID + 1
            ustrCommand = u"new varElement Variable_id" + unicode(n) + u" " + unicode(X) + u" " + unicode(Y) + u" " + unicode(15)
            self.mainController.execCommand(ustrCommand)
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
        def mousePressEvent_tool_newBasicOperator(ustrOperator):
            ustrCommand = u"new basicOperator " +  ustrOperator + " " + unicode(X) + " " + unicode(Y) 
            self.mainController.execCommand(ustrCommand)
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
        def mousePressEvent_tool_newVarDispObj():
            ustrCommand = u"new varDispElement "+ unicode(X) + " " + unicode(Y)
            self.mainController.execCommand(ustrCommand)
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionOsci.setChecked(False)
            
                   
        #################
        # Main Method
        #################
        
        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.mainController.get(u"idxToolSelected")
        bSimulationMode = self.mainController.get(u"bSimulationMode")
        
        # not passed as command since just clicking should not change the data
        self.mainController.set(u"px_mousePressedAt_X",X)
        self.mainController.set(u"px_mousePressedAt_Y",Y)
        self.mainController.set(u"px_mousePressedAt_x",x)
        self.mainController.set(u"px_mousePressedAt_y",y)

        if toolSelected == helper.ToolSelected.none:
            mousePressEvent_tool_none()

        
        if not bSimulationMode:
    
            if toolSelected == helper.ToolSelected.newVarElement:
                mousePressEvent_tool_newVarElement()
    
            elif toolSelected == helper.ToolSelected.newPlus:
                mousePressEvent_tool_newBasicOperator("+")
                
            elif toolSelected == helper.ToolSelected.newMinus:
                mousePressEvent_tool_newBasicOperator("-")

            elif toolSelected == helper.ToolSelected.newMultiplication:
                mousePressEvent_tool_newBasicOperator("*")

            elif toolSelected == helper.ToolSelected.newDivision:
                mousePressEvent_tool_newBasicOperator("/")

        else:
            
            if toolSelected == helper.ToolSelected.newVarDispObj:
                mousePressEvent_tool_newVarDispObj()
            
        self.repaint()
                   
    def mouseMoveEvent(self,coord):

        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.mainController.get(u"idxToolSelected")

        if toolSelected == helper.ToolSelected.none:

            # Moving objects
            objectsInFocus = list(self.mainController.selection)             
            if objectsInFocus != []:

                px_mousePressedAt_X = self.mainController.get(u"px_mousePressedAt_X")
                px_mousePressedAt_Y = self.mainController.get(u"px_mousePressedAt_Y")
                if px_mousePressedAt_X != sys.maxint:
                    xOffset = X - px_mousePressedAt_X 
                    yOffset = Y - px_mousePressedAt_Y 
                    
                    if ((xOffset != 0) or (yOffset != 0)) and \
                            (PyLinXDataObjects.PX_PlottableElement in self.mainController.get(u"@.types")) and\
                            self.mainController.get(u"@.bUnlock"):
                        ustrCommand = u"set @.xy (" + unicode(xOffset) + "," + unicode(yOffset) + u") -p"
                        self.mainController.execCommand(ustrCommand)
                    
                    # move line of connector.                 
                    ConnectorToModify = self.mainController.get(u"ConnectorToModify") 
                    if ConnectorToModify  != None:
                        idxPointModified = self.mainController.get(u"idxPointModified")
                        listPoints = list(ConnectorToModify.get(u"listPoints"))
                        listPointsOld = copy.copy(listPoints)
                        value = listPoints[idxPointModified]
                        if idxPointModified % 2 == 0:
                            value = value + xOffset 
                        else:
                            value = value + yOffset
                        listPoints[idxPointModified] = 10 * round( 0.1 * float(value))
                        if sum([abs(x-y) for x,y in zip(listPoints, listPointsOld)]) != 0:
                            ustrCommand = "set ./" + ConnectorToModify.get(u"Name") + ".listPoints " + repr(listPoints).replace(" ", "")
                            self.mainController.execCommand(ustrCommand)   
                    
                    self.mainController.set(u"px_mousePressedAt_X", X)
                    self.mainController.set(u"px_mousePressedAt_Y", Y)
                
            # Ploting the selection frame
            if self.latentGraphics.isInBody(u"HighlightObject"):
                highlightObject = self.latentGraphics.getb(u"HighlightObject")
                highlightObject.set(u"X1", coord.x())
                highlightObject.set(u"Y1", coord.y())
                    
            # change coordinates of the proxyElement, that is a placeholder for the finally connected element
            bConnectorPloting = self.mainController.get(u"bConnectorPloting")
            if bConnectorPloting:
                proxyElem = self.mainController.latentGraphics.getb(u"PX_PlottableProxyElement")
                proxyElem.X = X
                proxyElem.Y = Y

            self.repaint()
     
    def mouseReleaseEvent(self,coord):
        
        keys = self.latentGraphics.getChildKeys()       
        toolSelected = self.mainController.get(u"idxToolSelected")        

        # selecting Elements
        if toolSelected == helper.ToolSelected.none:
            for key in keys:
                if self.latentGraphics.getb(key).isAttrTrue(u"bLatent"):
                    self.latentGraphics.delete(key)
             
        self.mainController.set(u"px_mousePressedAt_X", sys.maxint)
        self.mainController.set(u"px_mousePressedAt_Y", sys.maxint)  

        self.repaint()
           
    def mouseDoubleClickEvent(self, coord):
        
        def bDialogue(X,Y,strShape, element):
            bDialog = False
            shape = element.get(strShape)
           
            if shape != None:
                idxPolygon = helper.point_inside_polygon(X , Y,shape)
                bDialog = not (len(idxPolygon) == 0)
            return bDialog
        
        if not self.mainController.get(u"bSimulationMode"):
            if self.mainController.get(u"bConnectorPloting"):
                self.mainController.execCommand("set /.bConnectorPloting False")
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
                PX_Dialogue_SimpleStimulate.PX_Dialogue_SimpleStimulate.getParams(self, element, self)
                return 
            if bFocusMeasure:
                PX_Dialogue_SelectDataViewer.PX_Dialogue_SelectDataViewer.getParams(self,element,self.mainController,self)
                return 
            
            if bFocus:
                if PyLinXDataObjects.PX_PlottableVarDispElement in types:
                    # TODO COMMAND
                    element.set(u"bVarDispVisible", True)                 