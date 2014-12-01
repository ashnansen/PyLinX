'''
Created on 30.10.2014

@author: Waetzold Plaum
'''
# General Libraries - alphabedic order
import copy
import cProfile
import ctypes
import inspect
import json
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys

# Project specific Libraries - alphabedic order
#import BContainer
from PyLinXData import * 
import PX_Templates as PX_Templ
import PyLinXData.PyLinXHelper as helper


#import PyLinXDataObjects

class PyLinXMain(QtGui.QMainWindow):

    def __init__(self):
 
        super(PyLinXMain, self).__init__()    

        self.ui = uic.loadUi("PyLinX_v0_3.ui")
        self.ui.setWindowIcon(QtGui.QIcon('pylinx.png'))
        self.ui.setWindowTitle('PyLinX')
        # self.ui.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)
        # self.ui.statusbar.hide()
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('cleanlooks') )
        
        # ExampleData
        self.rootContainer = PyLinX_DataObjectsInternal.RootContainer(self.ui)
        rootGraphics = PyLinXDataObjects.PX_PlotableObject("rootGraphics")
        testvar  = PyLinXDataObjects.PX_PlotableVarElement(1, 200,100, 15 )
        rootGraphics.paste(testvar, bHashById=True)
        testvar2 = PyLinXDataObjects.PX_PlotableVarElement(2, 400,200, 15 )
        rootGraphics.paste(testvar2, bHashById=True)
        connector1 = PyLinXDataObjects.PX_PlottableConnector(testvar, testvar2, [300]) 
        rootGraphics.paste(connector1, bHashById = True)   
        rootGraphics.set("bConnectorPloting", False)     
        self.rootContainer.paste(rootGraphics)
        


        # Configuration
        
        # idx that indicates the selected tool
        self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.rootContainer.set("ID_activeConnector", -1)
        
        
        # Drawing GUI
        
        scrollingArea = QtGui.QScrollArea()
        horizongalLayout2 = QtGui.QHBoxLayout()
        drawWidget = DrawWidget(self.rootContainer, self)
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
        drawWidget.setAutoFillBackground(True)
        drawWidget.setPalette(pal)
        
        
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
        self.ui.splitter.setStretchFactor(0,0)
        
        #self.scene.addWidget(self.drawWidget)
        #self.ui.graphicsView.setScene(self.scene)

        self.ui.show()
        self.ui.actionClose.triggered.connect(self.closeApplication)
        self.ui.actionNewElement.triggered.connect(self.on_actionNewElement)
        #self.ui.actionNewConnector.triggered.connect(self.on_actionNewConnector)
        self.ui.actionNewElement.setCheckable(True)
        self.ui.resize(800,600)
        
        
######################
# Methods
#####################


# Callbacks
####################

    def closeApplication(self):
        
        if QtGui.QMessageBox.question(None, '', "Soll PyLinX wirklich beendet werden?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)\
                 == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
            
    def on_actionNewElement(self):
        
        if self.rootContainer.get("idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.newVarElement) 
        else:
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
        
#     def on_actionNewConnector(self):
#         
#         if self.rootContainer.get("idxToolSelected") == helper.ToolSelected.none:
#             self.rootContainer.set("idxToolSelected", helper.ToolSelected.newConnector) 
#         else:
#             self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)

class DrawWidget (QtGui.QWidget):

    def __init__(self, rootContainer, mainWindow):
        super(DrawWidget, self).__init__()
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, PX_Templ.color.background)
        self.setPalette(p)
        self.rootContainer = rootContainer
        self.rootGraphics = rootContainer.getb("rootGraphics")
        self.activeGraphics = self.rootGraphics
        self.activeGraphics.set("ConnectorToModify", None)
        self.activeGraphics.set("idxPointModified" , None)
        self.mainWindow = mainWindow
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setMouseTracking(True)
        # Why does this not work?
        self.setMinimumSize(1000,600)
        
        self.setFocus( QtCore.Qt.PopupFocusReason)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.setEnabled(True)
    
    def paintEvent(self, event = None):
        self.activeGraphics.write(self,PX_Templ.Plot_Target.Gui)
        

    def keyPressEvent(self, qKeyEvent):
        
        # Deleting Objects
        if qKeyEvent.key() == QtCore.Qt.Key_Delete:
            keys = self.activeGraphics.getChildKeys()
            objectsInFocus = copy.copy(self.activeGraphics.get("objectsInFocus"))
            setDelete = set([])
            for key in keys:
                element = self.activeGraphics.getb(key)
                if element.isAttr("elem0"):
                    # deleting all connectors which are connected to an object, that is deleted
                    elem0 = element.get("elem0")
                    if elem0 in objectsInFocus:
                        setDelete.add(element.get("ID"))
                    elem1 = element.get("elem1")
                    if elem1 in objectsInFocus:
                        setDelete.add(element.get("ID"))
                # deleting all objects in focus
                if element in objectsInFocus:
                    setDelete.add(element.get("ID"))
            for element in setDelete:
                self.activeGraphics.delete(element)
            self.repaint()
        else:
            super(DrawWidget, self).keyPressEvent(qKeyEvent)
    
    
    def mousePressEvent(self, coord):
        
        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.rootContainer.get("idxToolSelected")
        
        self.rootContainer.set("px_mousePressedAt_X", X)
        self.rootContainer.set("px_mousePressedAt_Y", Y)
        
        if toolSelected == helper.ToolSelected.none:
            
            objInFocusOld = copy.copy(self.activeGraphics.get("objectsInFocus"))
            objInFocus = self.activeGraphics.getObjectInFocus(X,Y)
            if len(set(objInFocus).intersection(set(objInFocusOld))) > 0:
                pass
            else:      
                self.activeGraphics.set("objectsInFocus", objInFocus)
                if len(objInFocus) == 0:
                    highlightObject = PyLinXDataObjects.PX_LatentPlottable_HighlightRect(coord.x(), coord.y())
                    self.activeGraphics.paste(highlightObject)
                    
            # move lines of connectors
            len_objectsInFocus  = len(objInFocus)
            if len_objectsInFocus == 1:
                activeObject = objInFocus[0]
                if activeObject.isAttr("listPoints"):
                    listPoints = copy.copy(activeObject.get("listPoints"))
                    objectInFocus = objInFocus[0]
                    shape = objectInFocus.get("Shape")
                    elem0 = objectInFocus.get("elem0")
                    X_obj = elem0.get("X")
                    Y_obj = elem0.get("Y")
                    idxPolygons = helper.point_inside_polygon(x - X_obj , y - Y_obj, shape)
                    if len(idxPolygons) == 1:
                        idxPolygon = idxPolygons[0]
                        if idxPolygon > 0:
                            self.activeGraphics.set("ConnectorToModify", activeObject )
                            self.activeGraphics.set("idxPointModified" , idxPolygon -1)
                            
                            
            # Connecting Elements
    
            bConnectorPloting = self.rootGraphics.get("bConnectorPloting")
            if bConnectorPloting:
                # Determining if there is a endpoint in focus
                keys = self.activeGraphics.getChildKeys()
                objInFocus = None
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if PyLinXDataObjects.PX_PlotableVarElement in types: 
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if objInFocus != None:
                            break
                
                if objInFocus == None:
                
                    # case there is no second element
                    proxyElem = self.activeGraphics.getb("PX_PlottableProxyElement")
                    ConnectorPloting = self.rootGraphics.get("ConnectorPloting")
                    X0 = ConnectorPloting.get("X")
                    Y0 = ConnectorPloting.get("Y")
                    listPoints = copy.copy(ConnectorPloting.get("listPoints"))
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
                    ConnectorPloting.set("listPoints", listPoints)
                    proxyElem.set("X", x)
                    proxyElem.set("Y", y)
                    
                else:
                    
                    setIdxConnectedInPins = objInFocus.get("setIdxConnectedInPins")
                    len_setIdxConnectedInPins = len(setIdxConnectedInPins)
                    bConnect = False 
                    # no pin is connected
                    if len_setIdxConnectedInPins == 0:
                        bConnect = True
                    # there are connected pins
                    if len_setIdxConnectedInPins > 1:
                        # the clicked pin is connected
                        if idxPin in setIdxConnectedInPins:
                            bConnect = False
                        # the clicked pin is not connected
                        else:
                            bConnect = True
                
                    if bConnect:
                        # connecting the connector to the second element                
                        for key in keys:        
                            element = self.activeGraphics.getb(key)
                            types = inspect.getmro(type(element))
                            if PyLinXDataObjects.PX_PlottableProxyElement in types:
                                self.activeGraphics.delete(key)
                                break
                        ConnectorPloting = self.rootGraphics.get("ConnectorPloting")
                        ConnectorPloting.set("elem1",objInFocus)
                        self.rootGraphics.set("bConnectorPloting", False)
                        #self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
                        objInFocus.set("idxActiveInPins", [])
                        self.repaint()
            else:
                # Starting connecting Elements
                keys = self.activeGraphics.getChildKeys()
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if PyLinXDataObjects.PX_PlotableVarElement in types: 
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if objInFocus != None:
                            proxyElem = PyLinXDataObjects.PX_PlottableProxyElement(x,y)
                            self.activeGraphics.paste(proxyElem)
                            newConnector = PyLinXDataObjects.PX_PlottableConnector(element, proxyElem)
                            self.activeGraphics.paste(newConnector,  bHashById=True)
                            self.rootGraphics.set("bConnectorPloting", True)
                            self.rootGraphics.set("ConnectorPloting", newConnector)
                        

        
        elif toolSelected == helper.ToolSelected.newVarElement:
        
            n = len(self.activeGraphics ._BContainer__Body.keys()) + 1
            var = PyLinXDataObjects.PX_PlotableVarElement("testvar" + str(n),X,Y, 15 )
            self.activeGraphics.paste(var, bHashById=True)
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            self.repaint()
                         
        self.repaint()

                 
    def mouseMoveEvent(self,coord):

        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.rootContainer.get("idxToolSelected")
        
        if toolSelected == helper.ToolSelected.none:

            objectsInFocus = copy.copy(self.activeGraphics.get("objectsInFocus") )
            if objectsInFocus != []:
                px_mousePressedAt_X = self.rootContainer.get("px_mousePressedAt_X")
                px_mousePressedAt_Y = self.rootContainer.get("px_mousePressedAt_Y")
                if px_mousePressedAt_X != sys.maxint:
                    xOffset = X - px_mousePressedAt_X 
                    yOffset = Y - px_mousePressedAt_Y 
                    #len_objectsInFocus = len(objectsInFocus)
                    for activeObject in objectsInFocus:
                        ConnectorToModify = self.activeGraphics.get("ConnectorToModify")
                        # move objects that have coordinates
                        if activeObject.isAttr("X") and activeObject.isAttr("Y"):
                            X_obj = activeObject.get("X")
                            Y_obj = activeObject.get("Y")
                            newX = X_obj + xOffset 
                            newY = Y_obj + yOffset 
                            activeObject.set("X", newX)
                            activeObject.set("Y", newY)
                        
                        # move lines of connectors 
                        elif ConnectorToModify  != None:
                            idxPointModified = self.activeGraphics.get("idxPointModified")
                            listPoints = copy.copy(ConnectorToModify.get("listPoints"))
                            value = listPoints[idxPointModified]
                            if idxPointModified % 2 == 0:
                                value = value + xOffset 
                            else:
                                value = value + yOffset
                            listPoints[idxPointModified] = 10 * round( 0.1 * float(value))
                            activeObject.set("listPoints", listPoints)
                                                       
                    self.rootContainer.set("px_mousePressedAt_X", X)
                    self.rootContainer.set("px_mousePressedAt_Y", Y)            
                    self.repaint()
            if self.activeGraphics.isInBody("HighlightObject"):
                highlightObject = self.activeGraphics.getb("HighlightObject")
                highlightObject.set("X1", coord.x())
                highlightObject.set("Y1", coord.y())
                self.repaint() 



            keys = self.activeGraphics.getChildKeys()
            for key in keys:
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if  PyLinXDataObjects.PX_PlotableVarElement in types:
                    element.isPinInFocus(x,y)   
                    self.repaint()
            bConnectorPloting = self.rootGraphics.get("bConnectorPloting")
            if bConnectorPloting:
                proxyElem = self.activeGraphics.getb("PX_PlottableProxyElement")
                proxyElem.set("X", X)
                proxyElem.set("Y", Y)   
                self.repaint() 

        
    def mouseReleaseEvent(self,coord):
        
        keys = self.activeGraphics.getChildKeys()
                
        toolSelected = self.rootContainer.get("idxToolSelected")        
        
        # selecting Elements
        
        if toolSelected == helper.ToolSelected.none:
            X = coord.x()
            Y = coord.y()
            px_mousePressedAt_X = self.rootContainer.get("px_mousePressedAt_X")
            px_mousePressedAt_Y = self.rootContainer.get("px_mousePressedAt_Y")
            polygons = [[(X,Y), (X,px_mousePressedAt_Y ), (px_mousePressedAt_X,px_mousePressedAt_Y),(px_mousePressedAt_X,Y)]]
            for key in keys:
                element = self.activeGraphics.getb(key)
                if element.isAttr("Shape"):
                    bFocus = True
                    shape = element.get("Shape")
                    X_obj = element.get("X")
                    Y_obj = element.get("Y")

                    for polygon in shape:
                        if polygon != None:
                            for point in polygon:
                                idxCorner = helper.point_inside_polygon(X_obj + point[0], Y_obj + point[1],polygons)
                                if len(idxCorner) == 0:
                                    bFocus = False
                    if bFocus:
                        objectsInFocus = copy.copy(self.activeGraphics.get("objectsInFocus") )
                        objectsInFocus.append(element)
                        self.activeGraphics.set("objectsInFocus", objectsInFocus)
            self.activeGraphics.set("ConnectorToModify", None )
            self.activeGraphics.set("idxPointModified" , None )            
        
        elif toolSelected == helper.ToolSelected.newConnector:
            pass
                        
        for key in keys:
            if self.activeGraphics.getb(key).get("bLatent") == True:
                self.activeGraphics.delete(key)
             
        self.rootContainer.set("px_mousePressedAt_X", sys.maxint)
        self.rootContainer.set("px_mousePressedAt_Y", sys.maxint)       
        self.repaint()
        
        
    def mouseDoubleClickEvent(self, coord):
            
        bConnectorPloting = self.rootGraphics.get("bConnectorPloting")
        if bConnectorPloting: 
            keys = self.activeGraphics.getChildKeys()
            for key in keys:        
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if PyLinXDataObjects.PX_PlottableProxyElement in types:
                    self.activeGraphics.delete(key)
                    break
            ConnectorPloting = self.rootGraphics.get("ConnectorPloting")
            self.activeGraphics.delete( ConnectorPloting.get("ID") )
            self.rootGraphics.set("bConnectorPloting", False)
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
            self.repaint()           
                        
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
