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
import jsonpickle
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys

# Project specific Libraries - alphabedic order
from PyLinXData import * 
import PX_Templates as PX_Templ
import PyLinXData.PyLinXHelper as helper


class PyLinXMain(QtGui.QMainWindow):

    def __init__(self):
 
        super(PyLinXMain, self).__init__()    
        uiString = "PyLinX_v0_3.ui"
        self.ui = uic.loadUi(uiString)
        self.ui.setWindowIcon(QtGui.QIcon('pylinx.png'))
        self.ui.setWindowTitle('PyLinX')
        # self.ui.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)
        # self.ui.statusbar.hide()
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('cleanlooks') )
        
        # ExampleData
        self.rootContainer = PyLinX_DataObjectsInternal.RootContainer(self.ui)
        rootGraphics = PyLinXDataObjects.PX_PlotableObject("rootGraphics")
        testvar  = PyLinXDataObjects.PX_PlotableVarElement("TestVar_0", 150,100, 15 )
        rootGraphics.paste(testvar, bHashById=True)
        testvar2 = PyLinXDataObjects.PX_PlotableVarElement("TestVar_1", 400,200, 15 )
        #rootGraphics.paste(testvar2, bHashById=True)
        connector1 = PyLinXDataObjects.PX_PlottableConnector(testvar, testvar2, [300]) 
        #rootGraphics.paste(connector1, bHashById = True)   
        plusOperator = PyLinXDataObjects.PX_BasicOperator(300,200, "+")
        rootGraphics.paste(plusOperator, bHashById = True) 
        rootGraphics.set("bConnectorPloting", False)     
        self.rootContainer.paste(rootGraphics)
        


        # Configuration
        
        # idx that indicates the selected tool
        self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.rootContainer.set("ID_activeConnector", -1)
        rootGraphics.set("idxOutPinConnectorPloting", None)
        
        
        # Drawing GUI
        
        scrollingArea = QtGui.QScrollArea()
        horizongalLayout2 = QtGui.QHBoxLayout()
        drawWidget = DrawWidget(self.rootContainer, self)
        self.drawWidget = drawWidget
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
        self.ui.splitter.setStretchFactor(1,1)

        ## new UI
        if uiString == "PyLinX_v0_4.ui":
            self.ui.tabWidget.setTabText(0,"Elements")
            self.ui.tabWidget.setTabText(1,"Libraries")
        
        #self.scene.addWidget(self.drawWidget)
        #self.ui.graphicsView.setScene(self.scene)

        self.ui.show()
        self.ui.actionClose.triggered.connect(self.closeApplication)
        self.ui.actionNewElement.triggered.connect(self.on_actionNewElement)
        self.ui.actionLoadProject.triggered.connect(self.on_actionLoadProject)
        self.ui.actionSave.triggered.connect(self.on_actionSave)
        self.ui.actionSave_As.triggered.connect(self.on_actionSave_As)
        #self.ui.actionNewConnector.triggered.connect(self.on_actionNewConnector)
        self.ui.actionNewElement.setCheckable(True)
        self.ui.actionNewPlus.triggered.connect(self.on_actionNewPlus)
        self.ui.actionNewPlus.setCheckable(True)
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
            
    def on_actionNewPlus(self):
        
        if self.rootContainer.get("idxToolSelected") == helper.ToolSelected.none:
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.newPlus) 
        else:
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)

            
    def on_actionSave(self):
        rootGraphics = self.rootContainer.getb("rootGraphics")
        if rootGraphics .isAttr("strSavePath"):
            strSavePath = rootGraphics.get("strSavePath")
            self.__saveProject(strSavePath)
        else:
            self.on_actionSave_As()

    
    def on_actionSave_As(self):
        if self.rootContainer.isAttr("strSavePath"):
            strSavePath_old = self.rootContainer.get("strSavePath")
            (strPath, strSavePath_old_file) = os.path.split(strSavePath_old)
        else:
            strPath = os.getcwd()
        strSavePath= self.__showFileSaveSelectionDialog(strPath, bDir = False, strExt = "pson", strHeader ="Select File to save Project...")
        (strSavePath_base,strSavePath_ext) = os.path.splitext(strSavePath)
        if not  strSavePath_ext == ".pson":
            strSavePath = strSavePath_base + ".pson"
        self.__saveProject(strSavePath)

     
    def __saveProject(self, strSavePath):    
        
        _file = open(strSavePath, "w")
        project = self.rootContainer.getb("rootGraphics")
        project._BContainer__parent = None
        _file.write(jsonpickle.encode(project, keys=True))
        _file.close()
        rootGraphics = self.rootContainer.getb("rootGraphics")
        rootGraphics.set("strSavePath", strSavePath)  

   
    def on_actionLoadProject(self):
        strPath = os.getcwd()
        strSavePath= self.__showFileSelectionLoadDialog(strPath, bDir = False,strHeader ="Select File to load Project...")  
        _file = open(strSavePath)
        newProject = jsonpickle.decode(_file.read(), keys=True)
        oldProject = self.rootContainer.getb("rootGraphics")
        self.rootContainer.paste(newProject,"rootGraphics",  bForceOverwrite = True)
        self.drawWidget.newProject(newProject)
        del oldProject
        maxID = newProject.getMaxID()
        PyLinXDataObjects.PX_IdObject._PX_IdObject__ID = maxID + 1
        self.drawWidget.repaint()
        

    def __showFileSaveSelectionDialog(self,strPath = None, bDir = False, strExt= None, strHeader = None):
        
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = "Select Directory..."
            else:
                strHeader = "Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getSaveFileName(self.ui,strHeader,strPath,strExt))
    

    def __showFileSelectionLoadDialog(self, strPath = None, bDir = False, strExt = "", strHeader = None):
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = "Select Directory..."
            else:
                strHeader = "Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getOpenFileName(self.ui,strHeader,strPath,strExt))
        


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
    
    def newProject(self, rootGraphics):
        self.rootGraphics   = rootGraphics
        self.activeGraphics = rootGraphics
    
    def paintEvent(self, event = None):
        self.activeGraphics.write(self,PX_Templ.Plot_Target.Gui)
        #print "Max-ID: ", self.activeGraphics.getMaxID(0)
        

    def keyPressEvent(self, qKeyEvent):
        
        # Deleting Objects
        if qKeyEvent.key() == QtCore.Qt.Key_Delete:
            keys = self.activeGraphics.getChildKeys()
            objectsInFocus = list(self.activeGraphics.objectsInFocus)
            setDelete = set([])
            for key in keys:
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if (PyLinXDataObjects.PX_PlottableConnector in types):
                    # deleting all connectors which are connected to an object, that is deleted
                    elem0 = element.elem0
                    if elem0 in objectsInFocus:
                        setDelete.add(element.ID)
                    elem1 = element.elem1
                    if elem1 in objectsInFocus:
                        setDelete.add(element.ID)
                # deleting all objects in focus
                if element in objectsInFocus:
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
                    #print "elem0: ", elem0
                    #print "elem1: ", elem1
                    setIdxConnectedOutPins = elem0.get("setIdxConnectedOutPins")
                    setIdxConnectedInPins  = elem1.get("setIdxConnectedInPins")
                    #print "setIdxConnectedOutPins: ", setIdxConnectedOutPins 
                    #print "setIdxConnectedInPins: ", setIdxConnectedInPins
                    #print "idxOutPin: ", idxOutPin
                    #print "idxInPin: ", idxInPin
                    if idxOutPin in setIdxConnectedOutPins: 
                        setIdxConnectedOutPins.remove(idxOutPin)
                    if idxInPin in setIdxConnectedInPins: 
                        setIdxConnectedInPins.remove(idxInPin)
                    #print "setIdxConnectedOutPins (1): ", setIdxConnectedOutPins 
                    #print "setIdxConnectedInPins (1): ", setIdxConnectedInPins
                    elem0.set("setIdxConnectedOutPins", setIdxConnectedOutPins)
                    elem1.set("setIdxConnectedInPins", setIdxConnectedInPins)
                    
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
            
            objInFocusOld = list(self.activeGraphics.objectsInFocus)
            objInFocus = self.activeGraphics.getObjectInFocus(X,Y)
            if len(set(objInFocus).intersection(set(objInFocusOld))) > 0:
                pass
            else:      
                self.activeGraphics.objectsInFocus = objInFocus
                if len(objInFocus) == 0:
                    highlightObject = PyLinXDataObjects.PX_LatentPlottable_HighlightRect(coord.x(), coord.y())
                    self.activeGraphics.paste(highlightObject)
                    
            # move lines of connectors
            len_objectsInFocus  = len(objInFocus)
            if len_objectsInFocus == 1:
                activeObject = objInFocus[0]
                if activeObject.isAttr("listPoints"):
                    listPoints = list(activeObject.get("listPoints"))
                    objectInFocus = objInFocus[0]
                    shape = objectInFocus.get("Shape")
                    elem0 = objectInFocus.elem0
                    X_obj = elem0.X
                    Y_obj = elem0.Y
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
                    if PyLinXDataObjects.PX_PlotableElement in types: 
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if objInFocus != None:
                            if len(idxPin) == 1:
                                idxPin = idxPin[0]
                            break  
                #print "idxPin(2): ", idxPin
                #print "objInFocus: ", objInFocus 
                if objInFocus == None:
                
                    # case there is no second element
                    proxyElem = self.activeGraphics.getb("PX_PlottableProxyElement")
                    ConnectorPloting = self.rootGraphics.get("ConnectorPloting")
                    X0 = ConnectorPloting.X
                    Y0 = ConnectorPloting.Y
                    listPoints = list(ConnectorPloting.get("listPoints"))
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
                    proxyElem.X = x
                    proxyElem.Y = y
                    
                else:
                    # idxPin determined as the index of Pins in focus
                    setIdxConnectedInPins = objInFocus.get("setIdxConnectedInPins")
                    #print "setIdxConnectedInPins (2): ", setIdxConnectedInPins
                    if idxPin in setIdxConnectedInPins:
                        bConnect = False
                    else:
                        bConnect = True
                
                    #print "bConnect: ", bConnect
                    if bConnect:
                        # connecting the connector to the second element                
                        for key in keys:        
                            element = self.activeGraphics.getb(key)
                            types = inspect.getmro(type(element))
                            if PyLinXDataObjects.PX_PlottableProxyElement in types:
                                self.activeGraphics.delete(key)
                                #print "Proxy Deleted!"
                                break
                        ConnectorPloting = self.rootGraphics.get("ConnectorPloting")
                        ConnectorPloting.elem1 = objInFocus
                        #ConnectorPloting.idxInPin = idxPin 
                        # TODO: the convention for the idx of input Puns is not consistent ?
                        #print "-->idxPin: ", idxPin
                        #print "id(0): ", id(ConnectorPloting) 
                        ConnectorPloting.idxInPin = idxPin
                        #print "id(1): ", id(ConnectorPloting)
                        setIdxConnectedInPins.add(idxPin)
                        objInFocus.set("setIdxConnectedInPins", setIdxConnectedInPins)
                        self.rootGraphics.set("bConnectorPloting", False)
                        objInFocus.idxActiveInPins = []
                        
                        elem0 = ConnectorPloting.elem0
                        setIdxConnectedOutPins = elem0.get("setIdxConnectedOutPins")
                        idxOutPinConnectorPloting = self.rootGraphics.get("idxOutPinConnectorPloting")
                        setIdxConnectedOutPins.add(idxOutPinConnectorPloting)
                        elem0.set("setIdxConnectedOutPins", setIdxConnectedOutPins)
                        self.rootGraphics.set("idxOutPinConnectorPloting", None)

            else:
                # Starting connecting Elements
                keys = self.activeGraphics.getChildKeys()
                for key in keys:
                    element = self.activeGraphics.getb(key)
                    types = inspect.getmro(type(element))
                    if PyLinXDataObjects.PX_PlotableElement in types:
                        objInFocus, idxPin = element.isPinInFocus(x,y)
                        if len(idxPin) > 0:
                            idxPin = idxPin[0]                         
                        #print "objInFocus: ", objInFocus
                        #print "idxPin (3): ", idxPin 
                        if objInFocus != None and (idxPin > -1):
                            proxyElem = PyLinXDataObjects.PX_PlottableProxyElement(x,y)
                            self.activeGraphics.paste(proxyElem)
                            newConnector = PyLinXDataObjects.PX_PlottableConnector(element, proxyElem)
                            self.activeGraphics.paste(newConnector,  bHashById=True)
                            self.rootGraphics.set("bConnectorPloting", True)
                            self.rootGraphics.set("idxOutPinConnectorPloting", idxPin)
                            self.rootGraphics.set("ConnectorPloting", newConnector)
                        

        
        elif toolSelected == helper.ToolSelected.newVarElement:
        
            n = len(self.activeGraphics ._BContainer__Body.keys()) + 1
            var = PyLinXDataObjects.PX_PlotableVarElement("Variable_" + str(n),X,Y, 15 )
            self.activeGraphics.paste(var, bHashById=True)
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
            
        elif toolSelected == helper.ToolSelected.newPlus:
            
            plus = PyLinXDataObjects.PX_BasicOperator(X,Y,"+")
            self.activeGraphics.paste(plus, bHashById=True)
            self.rootContainer.set("idxToolSelected", helper.ToolSelected.none)
            self.mainWindow.ui.actionNewElement.setChecked(False)
            
      
        self.repaint()
         
    def mouseMoveEvent(self,coord):

        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))
        toolSelected = self.rootContainer.get("idxToolSelected")
        
        if toolSelected == helper.ToolSelected.none:

            # Moving objects
            objectsInFocus = list(self.activeGraphics.objectsInFocus)
            if objectsInFocus != []:
                px_mousePressedAt_X = self.rootContainer.get("px_mousePressedAt_X")
                px_mousePressedAt_Y = self.rootContainer.get("px_mousePressedAt_Y")
                if px_mousePressedAt_X != sys.maxint:
                    xOffset = X - px_mousePressedAt_X 
                    yOffset = Y - px_mousePressedAt_Y 
                    for activeObject in objectsInFocus:
                        ConnectorToModify = self.activeGraphics.get("ConnectorToModify")
                        # move objects that have coordinates
                        types = inspect.getmro(type(activeObject))
                        if (PyLinXDataObjects.PX_PlotableElement in types):
                            X_obj = activeObject.X
                            Y_obj = activeObject.Y
                            newX = X_obj + xOffset 
                            newY = Y_obj + yOffset 
                            activeObject.X = newX
                            activeObject.Y = newY
                        
                        # move lines of connectors 
                        elif ConnectorToModify  != None:
                            idxPointModified = self.activeGraphics.get("idxPointModified")
                            listPoints = list(ConnectorToModify.get("listPoints"))
                            value = listPoints[idxPointModified]
                            if idxPointModified % 2 == 0:
                                value = value + xOffset 
                            else:
                                value = value + yOffset
                            listPoints[idxPointModified] = 10 * round( 0.1 * float(value))
                            activeObject.set("listPoints", listPoints)
                                                       
                    self.rootContainer.set("px_mousePressedAt_X", X)
                    self.rootContainer.set("px_mousePressedAt_Y", Y)            
                    #self.repaint()
                    
            # Ploting the selection frame
            if self.activeGraphics.isInBody("HighlightObject"):
                highlightObject = self.activeGraphics.getb("HighlightObject")
                highlightObject.set("X1", coord.x())
                highlightObject.set("Y1", coord.y())

            keys = self.activeGraphics.getChildKeys()
            for key in keys:
                element = self.activeGraphics.getb(key)
                types = inspect.getmro(type(element))
                if PyLinXDataObjects.PX_PlotableElement  in types:
                    element.isPinInFocus(x,y)
                    
            # change coordinates of the proxyElement, that is a placeholder for the finally connected element
            bConnectorPloting = self.rootGraphics.get("bConnectorPloting")
            if bConnectorPloting:
                proxyElem = self.activeGraphics.getb("PX_PlottableProxyElement")
                proxyElem.X = X
                proxyElem.Y = Y   
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
                    X_obj = element.X
                    Y_obj = element.Y

                    for polygon in shape:
                        if polygon != None:
                            for point in polygon:
                                idxCorner = helper.point_inside_polygon(X_obj + point[0], Y_obj + point[1],polygons)
                                if len(idxCorner) == 0:
                                    bFocus = False
                    if bFocus:
                        objectsInFocus = list(self.activeGraphics.objectsInFocus )
                        objectsInFocus.append(element)
                        self.activeGraphics.objectsInFocus = objectsInFocus
            self.activeGraphics.set("ConnectorToModify", None )
            self.activeGraphics.set("idxPointModified" , None )            
                        
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
            #self.activeGraphics.delete( ConnectorPloting.get("ID") )
            self.activeGraphics.delete( ConnectorPloting.ID )
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
