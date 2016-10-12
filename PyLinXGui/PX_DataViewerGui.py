import sys
import math
import numpy as np
import copy

from PyQt4 import QtGui, QtCore
from PyLinXCompiler import PyLinXRunEngine
from PyLinXData import PyLinXCoreDataObjects


class DataViewerGui(QtGui.QMainWindow):
    
    def __init__(self, varDispObj, idx = 0, t_max = 1.,  mainGui = None, mainController = None):
        super (DataViewerGui, self).__init__()
        
        global DataDictionary
        
        self.setWindowIcon(QtGui.QIcon(r"pylinx_16.png"))
        
        self.varDispObj = varDispObj
        self.mainController = mainController
         
        self.idx = idx        
        
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setGeometry(405,300,598,410)
        
        self.checkview = False
        ###########################
        ### Toolbar
        
        
        toolbar = QtGui.QToolBar()      
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        self.plotterWidget = PlotterWidget(self.varDispObj, self, self.mainController)
        self.setCentralWidget(self.plotterWidget)
        ################################################################################
#         self.items = QtGui.QDockWidget("Data List",self)
#         self.labelview =  QtGui.QTableView()        
#         self.tablemodel = self.plotterWidget.getTableModel()
#         self.items.setWidget(self.labelview)
#         self.items.setFloating(False)
#         self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
#         
#         self.itemslider = QtGui.QDockWidget("Slider",self)
#         self.labelviewslider =  QtGui.QTableView()        
#         self.tablemodelslider = self.plotterWidget.getTableModel()
#         self.itemslider.setWidget(self.labelviewslider)
#         self.itemslider.setFloating(False)
#         self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.itemslider)
#         self.itemslider.hide()

        self.items = QtGui.QDockWidget("Data List",self)
        self.labelview =  QtGui.QTableView()        
        self.tablemodel = self.plotterWidget.getTableModel()
        self.items.setWidget(self.labelview)
        self.items.setFloating(False)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
            
            
            
          
        #######  Hiding number
        self.labelview.verticalHeader().setVisible(False)
        self.items.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures |
                                       QtGui.QDockWidget.DockWidgetMovable) 
        ################################################################################# 
        ###########################
        ### Actions
        self.adjustAction = QtGui.QAction('Adjust', self)
        self.adjustAction.setShortcut('Ctrl+A')
        self.adjustAction.triggered.connect(self.__onActionAdjust)
        toolbar.addAction(self.adjustAction)
        self.walkAxisAction = QtGui.QAction('Walking Axis', self)
        self.walkAxisAction.setShortcut('Ctrl+W')
        self.walkAxisAction.triggered.connect(self.__onActionWalkingAxis)
        self.walkAxisAction.setCheckable(True)
        toolbar.addAction(self.walkAxisAction)

        self.saveAction = QtGui.QAction('Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.__onActionSave)
        toolbar.addAction(self.saveAction)

        self.osziAction = QtGui.QAction('Show Oszi', self)
        self.osziAction.setShortcut('Ctrl+O')
        #self.osziAction.triggered.connect(self.__onActionOszi)
        self.osziAction.triggered.connect(self.__onActionLegendOszi)        
        self.osziAction.setCheckable(True) 
        self.osziAction.setChecked(True)
        
        toolbar.addAction(self.osziAction)


        self.legendAction = QtGui.QAction('Show Data List', self)
        self.legendAction.setShortcut('Ctrl+L')
        self.plotterWidget.show()
        self.items.hide()
        #self.legendAction.triggered.connect(self.__onActionLegend)
        self.legendAction.triggered.connect(self.__onActionLegendOszi)
        self.legendAction.setCheckable(True)
        self.legendAction.setDisabled(False)
        toolbar.addAction(self.legendAction)
        
        self.sliderAction = QtGui.QAction('Slider', self)
        self.sliderAction.setShortcut('Ctrl+S')
        self.sliderAction.triggered.connect(self.__onActionSlider)
        self.sliderAction.setCheckable(True)
        toolbar.addAction(self.sliderAction)
        self.sliderAction.setEnabled(False)
        
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Data-Viewer " + str(self.idx))
        
        self.listVars = list(self.varDispObj.get(u"setVars"))
        
        self.oldDockWidgetArea = 0
        self.newDockWidgetArea = QtCore.Qt.RightDockWidgetArea
        self.items.dockLocationChanged.connect(self.__on_dockLocationChanged)
        
    def __onActionSlider(self):
       #
        geometry = copy.copy(self.geometry())
        x = geometry.x()
        width = self.width()
        height = self.height()
        
        if self.sliderAction.isChecked():
            
            self.plotterWidget.checkTrue()
            self.checkview = True
            self.labelview.setColumnWidth(1,66)
            self.labelview.setColumnWidth(2,66)
            self.labelview.setColumnWidth(3,66)
       
            if self.legendAction.isChecked():
                self.items.hide()
            if self.newDockWidgetArea in (QtCore.Qt.LeftDockWidgetArea, \
                                              QtCore.Qt.RightDockWidgetArea)\
                        and not self.items.isVisible():
                width += self.items.width()
            if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, \
                                               QtCore.Qt.BottomDockWidgetArea)\
                        and not self.items.isVisible():
                height += self.items.height()
                 
         
            
            self.items.show()
            self.plotterWidget.setLine()
            self.plotterWidget.refreshPixmap()
#             self.legendAction.setEnabled(False)
#             self.osziAction.setEnabled(False)
        else:   
            self.plotterWidget.checkFalse()
            self.checkview = False
            width = 698
            self.labelview.setColumnWidth(1,100)
            self.labelview.setColumnWidth(2,100)
            self.items.hide()
#             if self.newDockWidgetArea in (QtCore.Qt.LeftDockWidgetArea, \
#                                               QtCore.Qt.RightDockWidgetArea):
#                 width -= self.items.width()
#             if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, \
#                                                QtCore.Qt.BottomDockWidgetArea)\
#                         and not self.items.isVisible():                
#                 height -= self.items.height()
#         


#             self.items = QtGui.QDockWidget("Data List",self)
#             self.labelview =  QtGui.QTableView()        
#             self.tablemodel = self.plotterWidget.getTableModel()
#             self.items.setWidget(self.labelview)
#             self.items.setFloating(False)
#             self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
#             #self.sliderAction.setEnabled(True)
#             self.items.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures |
#                                        QtGui.QDockWidget.DockWidgetMovable) 
            ##################  ##################  ##################  ##################  ##################
            
            
            self.items.hide()
            if self.legendAction.isChecked():
                self.items.show()
#             self.legendAction.setEnabled(True)
#             self.osziAction.setEnabled(True)
        width = 698
        
        self.setGeometry(x, geometry.y(), width,  height)
        #self.plotterWidget.setLine()
    def __on_dockLocationChanged(self, newLocation):
        self.newDockWidgetArea = newLocation
        
    def __onActionAdjust(self):
        self.plotterWidget.adjust()  
        
    def __onActionSave(self):
        print "ActionSave"
        
    def  __onActionLegendOszi(self):
        
        geometry = copy.copy(self.geometry())
        x = geometry.x()
        
        width = self.width()
        height = self.height()
        if self.legendAction.isChecked():
            if self.newDockWidgetArea in (QtCore.Qt.LeftDockWidgetArea, \
                                              QtCore.Qt.RightDockWidgetArea)\
                        and not self.items.isVisible():
                width += self.items.width()
            if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, \
                                               QtCore.Qt.BottomDockWidgetArea)\
                        and not self.items.isVisible():
                height += self.items.height()
            if self.osziAction.isChecked():
                #self.sliderAction.setEnabled(False)
                self.labelview.setColumnWidth(0,40)
                self.labelview.setColumnWidth(1,100)
                self.labelview.setColumnWidth(2,100)
                if not self.plotterWidget.isVisible():
                    if self.newDockWidgetArea == QtCore.Qt.LeftDockWidgetArea:
                        x -= self.plotterWidget.width()
                    if self.newDockWidgetArea in ( QtCore.Qt.LeftDockWidgetArea, QtCore.Qt.RightDockWidgetArea):
                        width += self.plotterWidget.width()
                    if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, \
                                               QtCore.Qt.BottomDockWidgetArea):
                        height += self.plotterWidget.height()
                self.plotterWidget.show()
                self.adjustAction.setVisible(True) 
                self.walkAxisAction.setVisible(True)                                
                self.legendAction.setEnabled(True)
                self.sliderAction.setEnabled(True)
                self.osziAction.setEnabled(True)
                self.items.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures |
                                       QtGui.QDockWidget.DockWidgetMovable)                  
            else:
                
                if self.plotterWidget.isVisible() and \
                        self.newDockWidgetArea == QtCore.Qt.LeftDockWidgetArea:
                    x += self.plotterWidget.width()
                if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, QtCore.Qt.BottomDockWidgetArea)\
                            and self.plotterWidget.isVisible():
                    height -= self.plotterWidget.height()
                if self.newDockWidgetArea in ( QtCore.Qt.LeftDockWidgetArea, QtCore.Qt.RightDockWidgetArea):
                    width -= self.plotterWidget.width()
                self.labelview.setColumnWidth(0,1)
                self.labelview.setColumnWidth(1,125)
                self.labelview.setColumnWidth(2,125)
                
                self.plotterWidget.hide()
                self.adjustAction.setVisible(False) 
                self.walkAxisAction.setVisible(False)                
                self.legendAction.setEnabled(False)
                self.sliderAction.setEnabled(False)
                self.osziAction.setEnabled(True)
                self.items.setFloating(False)
                self.items.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures |
                                       QtGui.QDockWidget.DockWidgetMovable) 
            self.items.show()
        else:
            self.sliderAction.setEnabled(True)
            if self.osziAction.isChecked(): 
                    
                self.items.hide()
                if self.newDockWidgetArea in (QtCore.Qt.LeftDockWidgetArea, \
                                                  QtCore.Qt.RightDockWidgetArea):
                    width -= self.items.width()
                if self.newDockWidgetArea in (QtCore.Qt.TopDockWidgetArea, \
                                                   QtCore.Qt.BottomDockWidgetArea)\
                            and not self.items.isVisible():                
                    height -= self.items.height()
                self.plotterWidget.show()
                self.adjustAction.setVisible(True) 
                self.walkAxisAction.setVisible(True)                 
                self.legendAction.setEnabled(True)
                self.osziAction.setEnabled(False)
        
        self.setGeometry(x, geometry.y(), width,  height)
        
    def __onActionWalkingAxis(self):
        if self.walkAxisAction.isChecked():
            self.plotterWidget.setBWalkingAxis(True)
        else:
            self.plotterWidget.setBWalkingAxis(False)
            
    def updateValues(self):
            
        self.plotterWidget.updateValues()
        self.labelview.setModel(self.tablemodel)
        self.tablemodel.dataChanged.emit(self.tablemodel.index(0,0), self.tablemodel.index(3,3))
        
        self.labelview.setColumnWidth(0,40)
        if self.checkview == True:
            self.labelview.setColumnWidth(1,66)
            self.labelview.setColumnWidth(2,66)
            self.labelview.setColumnWidth(3,66)
        else:
            self.labelview.setColumnWidth(1,100)
            self.labelview.setColumnWidth(2,100)
            
        if self.osziAction.isChecked() == False and self.legendAction.isChecked():
            self.labelview.setColumnWidth(0,1)
            self.labelview.setColumnWidth(1,125)
            self.labelview.setColumnWidth(2,125)
            self.sliderAction.setEnabled(True)
        
        self.plotterWidget.checkFalse()
        self.checkview = False
        
        self.items.setMinimumWidth(243)
        self.items.setMaximumWidth(243)
        
        #self.items.update()
        if self.mainController.get(u"bSimulationRuning") == True:
            self.sliderAction.setEnabled(False)
            
    def addVar(self, varName):
        print "addVar"
        self.plotterWidget.addVar(varName)
            
    def delVar(self, varName):
        print "delVar"
        self.plotterWidget.delVar(varName)
        
    def stop_run(self):
        if self.sliderAction.isChecked():
            self.plotterWidget.checkTrue()
            self.checkview = True
            self.plotterWidget.refreshPixmap()
        self.plotterWidget.setLine()
        if self.osziAction.isChecked() == False and self.legendAction.isChecked():
            self.sliderAction.setEnabled(False)
        else:    
            self.sliderAction.setEnabled(True)
        self.plotterWidget.stop_run()
        
        


        
class PlotterWidget(QtGui.QWidget):
    def __init__(self, varDispObj,  mainWidget = None, mainController = None, parent = None ):
        super(PlotterWidget, self).__init__(parent)
        
        
        #Members
        self.mainController = mainController
        self.DataDictionary = self.mainController.getb("DataDictionary")
        self.margin = 50
#         self.LineA = 120
#         self.LineB = 200
        self.FlagA = True
        self.FlagB = True
        self.checkslider = False
        self.sliderdataA = 0
        self.sliderdataB = 0
#         self.dxa = 0
#         self.dxb = 0
        
        self.dataslider = []
        self.slideridxA = 0
        self.slideridxB = 0
        
        self.zoomStack = []
        self.curveMap = {}   
        self.curveMapMemory = {}                                                            
        self.curZoom = 0      #int
        self.rubberBandIsShown = False
        self.pixmap = QtGui.QPixmap()
        self.rubberBandRect = QtCore.QRect()
        self.colorLight = self.palette().light().color()
        self.penDashLine = QtGui.QPen(QtGui.QBrush(QtCore.Qt.white), 1, QtCore.Qt.DashLine)
        self.delta_t = 0.1
        self.t     = np.array([self.delta_t*i for i in range(200)])
        self.varDispObj = varDispObj
        self.setStyleSheet("background-color:black")
        self.setAutoFillBackground(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.listVars = list(self.varDispObj.get(u"setVars"))
        self.colorFactory = ColorFactory()
        self.dictVarColors = {}
        
        self.LineA = 137
        
        self.LineB = 313
        
        iniSettings = PlotSettings()
        self.setPlotSettings(iniSettings)       

        if self.listVars != None:
            for var in self.listVars:
                self.curveMap[var]=[]
                self.curveMapMemory[var] = []
          
        self.RunConfigDictionary = self.mainController.getb(u"RunConfigDictionary")
        
        self.model = PlotterWidget.MyTableModel(self)
       
    class MyTableModel(QtCore.QAbstractTableModel):
        
        def __init__(self, plotterWidget, parent= None, *args ):
            QtCore.QAbstractTableModel.__init__(self, parent , *args)
            
            self.plotterWidget = plotterWidget
            

        def rowCount(self, parent):
            if self.plotterWidget.checkslider == False:
                return len(self.plotterWidget.listVars)
            else:
                return 1
    
        def columnCount(self, parent):
            if self.plotterWidget.checkslider == False:
                return 4
            else:
                return 4
            
    
        def data(self, index, role):
            if self.plotterWidget.checkslider == False:
                if not index.isValid():
                    return QtCore.QVariant()
                
                elif role == QtCore.Qt.BackgroundRole:
                    if index.column() == 0:
                        retVal = self.plotterWidget.dictVarColors[self.plotterWidget.listVars[index.row()]]
                        return QtGui.QBrush(retVal)
    
    
                #######################
                elif role != QtCore.Qt.DisplayRole:
                    return None
                
                elif index.column()==2:
                    retVal = self.plotterWidget.curveMap[self.plotterWidget.listVars[index.row()]][-1].y() 
                    return retVal 
                
                elif index.column()==1:
                    retVal = self.plotterWidget.listVars[index.row()]               
                    return retVal
                
                elif role == QtCore.Qt.CheckStateRole:
                    return("")
    
                return QtCore.QVariant("")
            
            else:
#######################      
                if not index.isValid():
                    return QtCore.QVariant()
                
                elif role == QtCore.Qt.BackgroundRole:
                    if index.column() == 0:
                        retVal = self.plotterWidget.dictVarColors[self.plotterWidget.listVars[index.row()]]
                        return QtGui.QBrush(retVal)
    
    
                #######################
                elif role != QtCore.Qt.DisplayRole:
                    return None
                
                elif index.column() == 0:
                    retVal = self.plotterWidget.sliderdataA 
                    return QtGui.QBrush(retVal)
            
                elif index.column()==2:
                    retVal = self.plotterWidget.sliderdataB  
                    return retVal 
                
                elif index.column()==1:
                    retVal = self.plotterWidget.sliderdataA        
                    return retVal
                
                elif index.column()==3:
                    retVal = self.plotterWidget.sliderdataA - self.plotterWidget.sliderdataB   
                    return retVal 
                
                elif role == QtCore.Qt.CheckStateRole:
                    return("")
    
                return QtCore.QVariant("")
        
        def headerData(self,col,orientation,role):   
            if self.plotterWidget.checkslider == False:
                self.headerdata =['color','Label','Data','']
            else:
                self.headerdata = ['color','Slider A','Slider B','Diff']
                   
            if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerdata[col])
            return QtCore.QVariant()
        
        def flags(self,index):
            return(QtCore.Qt.ItemIsEnabled| QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable)
        
 
    def getTableModel(self):
        return self.model
    

    
    def adjust(self):
        self.zoomStack[self.curZoom].adjust()
        self.refreshPixmap()
        
    def setBWalkingAxis(self, boolean):
        self.zoomStack[self.curZoom].setBWalkingAxis(boolean)
        self.refreshPixmap()
    
    def updateValues(self):
        self.listVars = list(self.varDispObj.get(u"setVars"))
        self.t = np.append(self.t, self.RunConfigDictionary[u"t"])
        self.settings.minX = self.t[-1] - 201 * self.RunConfigDictionary[u"delta_t"]
        self.settings.maxX = self.t[-1]
        #print "self.t[-1] ", self.t[-1]        
        if self.listVars != None:
            if len(self.listVars) > 0:
            #if self.t[-1] > 0:  
                
                for var in self.listVars:
                    if self.t[-1] == 0:
                        self.curveMap[var]=   []
                        self.curveMapMemory[var] = []                        
                    if var not in self.curveMap:
                        self.curveMap[var]=   []
                        self.curveMapMemory[var] = []
                    if len(self.curveMap[var]) > 200:
                        self.curveMapMemory[var].append(self.curveMap[var].pop(0))
                    self.curveMap[var].append(QtCore.QPointF(self.settings.maxX,\
                                                  self.DataDictionary[var]))
                  #  print self.DataDictionary
                    #print "PyLinXRunEngine.DataDictionary[" + str(var) + "]", PyLinXRunEngine.DataDictionary[var]             
                self.refreshPixmap()
                #self.repaint()

                QtGui.QWidget.update(self)
                
    
    def setPlotSettings(self,settings):                         
        self.zoomStack = []
        self.zoomStack.append(settings)
        self.curZoom = 0
        self.refreshPixmap()

    def setCurveData(self, idNum, data):
        self.curveMap[idNum] = data
        
    
    def clearCurve(self, idNum):
        if self.curveMap.has_key(idNum):
            self.curveMap.remove(idNum)
        self.refreshPixmap()
        print self.curveMap    
        
    def minimumSizeHint(self):
        return QtCore.QSize(0*self.margin,2*self.margin)
         
    def sizeHint(self):
        return QtCore.QSize(12*self.margin,8*self.margin)
    
    def zoomOut(self):
        if(self.curZoom > 0):
#             self.zoomOutButton.setEnabled(self.curZoom > 0)
#             self.zoomInButton.setEnabled(True)
#             self.zoomInButton.show()
            self.refreshPixmap()
        
    def zoomIn(self):
        if(self.curZoom < len(self.zoomStack) - 1):
            self.curZoom = self.curZoom + 1
#             self.zoomInButton.setEnabled(self.curZoom < len(self.zoomStack) - 1)
#             self.zoomOutButton.setEnabled(True)
#             self.zoomOutButton.show()
            self.refreshPixmap()
    
    def paintEvent(self, event):
        painter = QtGui.QStylePainter(self)             
        painter.drawPixmap(0, 0, self.pixmap)
 

        if self.rubberBandIsShown: 
            painter.setPen(self.palette().light().color()) 
            painter.drawRect(self.rubberBandRect.normalized().adjusted(0,0,-1,-1)) 
            painter.setPen(QtCore.Qt.red) 
        
        if self.hasFocus(): 
            option = QtGui.QStyleOptionFocusRect() 
            option.initFrom(self) 
            option.backgroundColor = self.palette().dark().color() 
            option.backgroundColor = self.palette().shadow().color() 
            painter.drawPrimitive(QtGui.QStyle.PE_FrameFocusRect, option)
        
    def resizeEvent(self, event):
        self.refreshPixmap()
    
    def mousePressEvent(self, event):
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2*self.margin, self.height() - 2*self.margin)
        if (event.button() == QtCore.Qt.LeftButton):
            if (rect.contains(event.pos())):
                self.rubberBandIsShown = True
                self.rubberBandRect.setTopLeft(event.pos())
                self.rubberBandRect.setBottomRight(event.pos())
                self.updateRubberBandRegion()
                self.setCursor(QtCore.Qt.CrossCursor)
        
        if self.checkslider == True:
            if self.sliderA.containsPoint(event.pos(), QtCore.Qt.OddEvenFill):
                self.FlagA = False
                self.FlagB = True
                
            if self.sliderB.containsPoint(event.pos(), QtCore.Qt.OddEvenFill):
                self.FlagB = False
                self.FlagA = True
                
        
        for var in self.listVars:
            self.dataslider = self.curveMap[var]
        
      
        print event.pos()
        print self.width()
        print 'A',self.LineA
        print 'B',self.LineB
        
    def mouseMoveEvent(self,event):
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2*self.margin, self.height() - 2*self.margin)
        if self.rubberBandIsShown:
            self.updateRubberBandRegion()
            self.rubberBandRect.setBottomRight(event.pos())
            self.updateRubberBandRegion()
      
        if self.checkslider == True:
            if self.FlagA == False:
                self.LineA = event.pos().x()
                if self.LineA < self.margin:
                    self.LineA = self.margin
                    self.refreshPixmap()     
                    
                elif self.LineB - self.LineA <=10:
                    self.LineA = self.LineB - 10
                    self.refreshPixmap()
                
                else:
                    self.refreshPixmap()
   
            if self.FlagB == False:
                self.LineB = event.pos().x()
                if self.LineB > self.width() -  self.margin:
                    self.LineB = self.width() -  self.margin
                    self.refreshPixmap()
                    
                elif self.LineB - self.LineA <=10:
                    self.LineB = self.LineA + 10
                    self.refreshPixmap()
                    
                else:
                    self.refreshPixmap()
             
            if len(self.dataslider) > 0:
                xa = self.LineA
                self.dxa = (xa - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX
                for i in range(len(self.dataslider)):
                    if self.dataslider[i].x() > self.dxa:
                        self.slideridxA = i
                        break
                self.sliderdataA = self.dataslider[self.slideridxA].y()
                
                xb = self.LineB
                self.dxb = (xb - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX
                for i in range(len(self.dataslider)):
                    if self.dataslider[i].x() > self.dxb:
                        self.slideridxB = i
                        break
                self.sliderdataB = self.dataslider[self.slideridxB].y()
            
        
    #         y = event.pos().y()
    #         print y
    #         dy = -(y - rect.bottom())*self.settings.spanY()/(rect.height()-1)+self.settings.minY
    #         print dy
            
        
    def printSlider(self):
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2*self.margin, self.height() - 2*self.margin)
        xa = self.LineA
        self.dxa = (xa - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX
        xb = self.LineB
        self.dxb = (xb - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX          
                   
            
    def mouseReleaseEvent(self,event):
        if (event.button() == QtCore.Qt.LeftButton) and self.rubberBandIsShown :
            self.rubberBandIsShown = False
            self.updateRubberBandRegion()
            self.unsetCursor()
            
            rect =  self.rubberBandRect.normalized()
            if rect.width() < 4 or rect.height() < 4 :
                return
            
            self.__zoomToRect(rect)
            self.zoomIn()
        self.model.dataChanged.emit(self.model.index(0,0), self.model.index(3,3))
        self.FlagA = True
        self.FlagB = True

    def __zoomToRect(self, rect, bAdjust = True):
        
            prevSettings = self.zoomStack[self.curZoom]                    
            settings = PlotSettings()
            dx = prevSettings.spanX() / (self.width() - 2*self.margin)
            dy = prevSettings.spanY() / (self.height()- 2*self.margin)
            
#             print self.sliderdataA
#             print self.dxa
            settings.minX = prevSettings.minX + dx * (rect.left() - self.margin)
            settings.maxX = settings.minX + dx * (rect.right() - rect.left())
            settings.maxY = prevSettings.maxY - dy * (rect.top() - self.margin)
            settings.minY = settings.maxY - dy * (rect.bottom() - rect.top())
            xaa = self.dxa- settings.minX
            self.LineA = self.margin + (xaa * (self.width()-100)/(settings.maxX - settings.minX))
            xbb = self.dxb- settings.minX
            self.LineB = self.margin + (xbb * (self.width()-100)/(settings.maxX - settings.minX))
            
            self.zoomStack.append(settings)
            
         
    def keyPressEvent(self, event):
        
        e = event.key()
        
        if e == QtCore.Qt.Key_Plus:
            self.zoomIn()
            
        elif e == QtCore.Qt.Key_Minus:
            self.zoomOut()
        
        elif e == QtCore.Qt.Key_Left:
            self.zoomStack[self.curZoom].scroll(-1,0)
            self.refreshPixmap()
            
        elif e == QtCore.Qt.Key_Right:
            self.zoomStack[self.curZoom].scroll(+1,0)
            self.refreshPixmap()
            
        elif e == QtCore.Qt.Key_Down:
            self.zoomStack[self.curZoom].scroll(0, -1)
            self.refreshPixmap()
            
        elif e == QtCore.Qt.Key_Up:
            self.zoomStack[self.curZoom].scroll(0, +1)
            self.refreshPixmap()
            
        else:
            super(PlotterWidget, self).keyPressEvent(event)
    
        
 
    def wheelEvent(self, event):
        modifier = QtGui.QApplication.keyboardModifiers()
        border = 15
        zoonRatio = 0.86      
        rect_zoom_x = QtCore.QRect( self.margin + border, self.margin, self.width() - 2*self.margin - border, self.height() - 2*self.margin + border)
        rect_zoom_y = QtCore.QRect( self.margin - border, self.margin, self.width() - 2*self.margin + border, self.height() - 2*self.margin - border)
        
        
        if self.LineB > self.width() -  self.margin:
            self.LineB = self.width() -  self.margin
            
        if self.LineA > self.width() -  self.margin:
            self.LineA = self.LineB-10
        
        if modifier == QtCore.Qt.ControlModifier:
            
            numDegrees = event.delta( ) / 8
            self.numTicks = numDegrees / 15
            
            if self.numTicks > 0:
                zoomFac = zoonRatio
            elif self.numTicks < 0:
                zoomFac = 1 / zoonRatio
            else:
                zoomFac = 1.0
                
            x = event.x()
            y = event.y()

            if (rect_zoom_x.contains(event.pos()))  :
                deltaX = self.width() -self.margin - x  
                facX = float(deltaX) / (self.width() - 2 * self.margin)
                rectZoom_width = zoomFac * (self.width() - 2 * self.margin)
                rectZoom_x = x - (1 - facX) * rectZoom_width
#                 rectZoom_x = max(self.margin, rectZoom_x)
#                 rectZoom_x = min(rectZoom_x, self.width() - self.margin)
                    
            else:
                rectZoom_width = self.width() - 2 * self.margin
                rectZoom_x = self.margin

            if (rect_zoom_y.contains(event.pos())):
                deltaY = self.height() - self.margin - y 
                facY = float(deltaY) / (self.height() - 2 * self.margin)
                rectZoom_height = zoomFac * (self.height() - 2 * self.margin)
                rectZoom_y = y - (1 - facY) * rectZoom_height
            else:
                rectZoom_height = self.height() - 2 * self.margin
                rectZoom_y      = self.margin
            
            rectZoom = QtCore.QRect(rectZoom_x, rectZoom_y,rectZoom_width,rectZoom_height )             
            self.__zoomToRect(rectZoom)
            
            self.zoomIn()  

        else:
            numDegrees = event.delta() / 8
            numTicks = numDegrees / 15;
            if modifier == QtCore.Qt.ShiftModifier:
                self.zoomStack[self.curZoom].scroll(-numTicks,0, xMax = self.t[-1] )
            else:
                self.zoomStack[self.curZoom].scroll(0, numTicks)

            self.refreshPixmap()

        event.accept()
    
    def updateRubberBandRegion(self):
        rect =  self.rubberBandRect.normalized() 
        self.update(rect.left(), rect.top(), rect.width(), 1)
        self.update(rect.left(), rect.top(),1, rect.height())
        self.update(rect.left(), rect.bottom(), rect.width(), 1)
        self.update(rect.right(), rect.top(),1 , rect.height() )
#        
    def refreshPixmap(self):
            # hide action slider
            # set checked = false
        self.pixmap = QtGui.QPixmap(self.size())
        self.pixmap.fill(self, 0,0)
        
        painter = QtGui.QPainter(self.pixmap)
        painter.initFrom(self)
        
        self.drawGrid(painter)
        
        if self.checkslider == True:
            self.drawSlider(painter)
        self.drawCurves(painter)
        
        
        
        if self.LineB > self.width() -  self.margin:
            self.LineB = self.width() -  self.margin
            
        if self.LineA > self.width() -  self.margin:
            self.LineA = self.LineB-10

        if hasattr(self, 'dxa'):
            if self.FlagA == True and self.FlagB == True:
                if self.dxa > 0:
                    xaa = self.dxa- self.settings.minX
                    self.LineA = self.margin + (xaa * (self.width()-100)/(self.settings.maxX - self.settings.minX))
                    xbb = self.dxb- self.settings.minX
                    self.LineB = self.margin + (xbb * (self.width()-100)/(self.settings.maxX - self.settings.minX))
    
                    if self.LineB > self.width() -  self.margin:
                        self.LineB = self.width() -  self.margin
                
                    if self.LineA > self.width() -  self.margin:
                        self.LineA = self.LineB-10
            
        self.update()
        
     
        
    
 
    def drawGrid(self, painter):   
        
        def __drawXAxis():
            painter.setPen(self.penDashLine)
            painter.drawLine(x, rect.top(), x, rect.bottom())
            painter.setPen(self.colorLight)
            painter.drawLine(x, rect.bottom(), x, rect.bottom() + 5 )
            painter.drawText(x - 50, rect.bottom() + 5, 100, 20, 
                             QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,  unicode('%0.2f' % label)) 
        
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2* self.margin, self.height() - 2* self.margin)
            
        if not rect.isValid():
            return
        settings = self.zoomStack[self.curZoom]
         
        # Draw vertical Lines
        deltaX = settings.spanX() / settings.numXTicks
        minXAxis = math.floor(settings.minX / deltaX)*deltaX                      
        if settings.bWalkingAxis:      
            minXAxisPx = rect.left() - ( float(settings.minX - minXAxis) / settings.spanX() ) * rect.width()  
            for i in range(settings.numXTicks +1):                
                x = minXAxisPx + ( i * (rect.width() - 1) / settings.numXTicks)
                if x >= rect.left():
                    label = minXAxis + ( i * deltaX )
                    __drawXAxis()

        else:
            for i in range(settings.numXTicks +1):              
                x = rect.left() + ( i * (rect.width() - 1) / settings.numXTicks)
                label = settings.minX + (  i * settings.spanX() / settings.numXTicks )
                __drawXAxis()
        
        #Draw horizontal Lines
        deltaY = settings.spanY() / settings.numYTicks
        for j in range(settings.numYTicks + 1):
            
            y = rect.bottom() - ( j * (rect.height() - 1) / settings.numYTicks)
            label = settings.minY + ( j * deltaY )
            painter.setPen(self.penDashLine)            
            painter.drawLine(rect.left(), y, rect.right(), y)
            painter.setPen(self.colorLight)
            painter.drawLine(rect.left() - 5, y, rect.left(), y )
            painter.drawText(rect.left() - self.margin, y - 10,self.margin - 5,  20, 
                             QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, unicode('%0.2f' % label))          #***********
            
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        
        
    def drawSlider(self, painter):
        
        
        pen = QtGui.QPen(QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine)
        
        painter.setPen(pen)
        painter.drawLine(self.LineA, 50, self.LineA, self.height() - self.margin-2)
        pen.setStyle(QtCore.Qt.DashLine)  
        
        painter.drawLine(self.LineB, 50, self.LineB , self.height() - self.margin-2)
 
        pen.setStyle(QtCore.Qt.DashLine)  
        
    #def drawPolygon(self, qp):
        
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.gray)

        self.sliderA = QtGui.QPolygon([QtCore.QPoint( self.LineA - 5, 35 ), QtCore.QPoint( self.LineA + 5, 35 ),
                   QtCore.QPoint( self.LineA + 5, 45), QtCore.QPoint( self.LineA, 50 ),
                   QtCore.QPoint( self.LineA - 5, 45 )])
        painter.drawPolygon(self.sliderA)
        
        self.sliderB = QtGui.QPolygon([ QtCore.QPoint( self.LineB - 5, 35 ), QtCore.QPoint( self.LineB + 5, 35 ),
                           QtCore.QPoint( self.LineB + 5, 45), QtCore.QPoint( self.LineB, 50 ),
                           QtCore.QPoint( self.LineB - 5, 45 )])
        painter.drawPolygon(self.sliderB)
        
 #   def drawText(self,qp):
        painter.setPen(QtCore.Qt.white)
        painter.setFont(QtGui.QFont('Decorative', 6))
        painter.drawText(QtCore.QPoint(self.LineA-2, 43) , 'A') 
        painter.setFont(QtGui.QFont('Decorative', 6))
        painter.drawText(QtCore.QPoint(self.LineB - 2, 43) , 'B')

    
    def drawCurves(self,  painter):
    
        colorForIds = [QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue, QtCore.Qt.cyan, QtCore.Qt.magenta, QtCore.Qt.yellow]
        self.settings = self.zoomStack[self.curZoom]
        
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2*self.margin, self.height() - 2*self.margin)
        
        if not rect.isValid():
            return
        
        painter.setClipRect(rect.adjusted(1, 1, -1, -1)) 
        
        i = 0
        for var in self.listVars:
            data = self.curveMap[var]
            polyline = QtGui.QPolygonF()
            

            for j in range(len(data)): 
                dx = data[j].x() - self.settings.minX 
                dy = data[j].y() - self.settings.minY
                
                x = rect.left() + (dx * (rect.width()-1)/self.settings.spanX()) 
                y = rect.bottom() - (dy * (rect.height()-1)/self.settings.spanY()) 
                polyline.append(QtCore.QPointF(x,y))

            
            if var in self.dictVarColors:
                color = self.dictVarColors[var]
            else:
                color = self.colorFactory.getColor()
                self.dictVarColors[var] = color
            painter.setPen(color) 
            painter.drawPolyline(polyline)
            #self.
            i += 1
    
       
            
    def stop_run(self):
        for var in self.listVars: 
            copyValues = copy.copy(self.curveMap[var])
            copyValuesMemory = copy.copy(self.curveMapMemory[var])
            self.curveMap[var] = copyValuesMemory
            self.curveMap[var].extend(copyValues )
###################################################################################
#         if self.checkslider == False:
#             self.checkslider = True
        
##################################################################################  
        self.refreshPixmap()
    
    def checkTrue(self):
        self.checkslider = True
        self.refreshPixmap()
        
    def checkFalse(self):
        self.checkslider =False
        self.refreshPixmap()
        
    def setLine(self):
        rect = QtCore.QRect( self.margin, self.margin, self.width() - 2*self.margin, self.height() - 2*self.margin)
        self.LineA = self.margin + (self.width()-100)/4
        xa = self.LineA
        self.dxa = (xa - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX
        self.LineB = self.margin + 3*(self.width()-100)/4
        xb = self.LineB
        self.dxb = (xb - rect.left())*self.settings.spanX()/(rect.width()-1)+self.settings.minX
    

class PlotSettings(QtGui.QWidget):
    def __init__(self):
        super(PlotSettings, self).__init__()
        self.minX = -10.0
        self.maxX = 0
        self.numXTicks = 5
        self.minY = 0
        self.maxY = 10.0
        self.numYTicks = 5
        self.bWalkingAxis = False
        
    # This function increments or drcrements minX, minY, maxX, maxY.Basically the function is used in PlotterWidget- KeyPressedEvent(). 
    def scroll(self,dx,dy, xMax = None):  

        stepX = self.spanX() / self.numXTicks
        minX = self.minX + dx * stepX
        maxX = self.maxX  + dx * stepX

        # Prevent scrolling to regions without Data
        if minX < 0:
            spanX = self.spanX()
            self.minX = 0
            self.maxX = spanX
        elif xMax != None:
            if maxX > xMax:
                spanX = self.spanX()
                self.maxX = xMax
                self.minX = xMax - spanX
            else:
                self.maxX = maxX
                self.minX = minX                
        else:
            self.maxX = maxX
            self.minX = minX
        
        stepY = self.spanY() / self.numYTicks
        self.minY += dy * stepY
        self.maxY += dy * stepY
        
    #Used by mouseReleaseEvent() to round of axis parameters to nice values and to determine appropriate ticks for each axis.takes one axix at a time.
    def adjust(self):
     
        self.minX, self.maxX, self.numXticks = self.adjustAxis(self.minX, self.maxX, self.numXTicks)
        self.minY, self.maxY, self.numYticks = self.adjustAxis(self.minY, self.maxY, self.numYTicks)      #****check******

    def spanX(self):
        return self.maxX - self.minX

    def spanY(self):
        return self.maxY - self.minY
    
    def adjustAxis(self, mini, maxi, numTicks):            
        MinTicks = 4
        grossStep = (maxi - mini) / MinTicks
        step = math.pow(10.0, math.floor(math.log10(grossStep))) 
        
        if 5*step < grossStep:
            step *= 5
        elif 2*step < grossStep:
            step *= 2
            
        numTicks = int(math.ceil(maxi / step)) - math.floor(mini / step)
        
        if numTicks < MinTicks:
            numTicks = MinTicks
        mini = math.floor(mini / step) * step
        maxi = math.ceil(maxi / step) * step

        return mini, maxi, numTicks
    
    def setBWalkingAxis(self, boolean):
        if boolean == False:
            self.bWalkingAxis = False
        elif boolean == True:
            self.bWalkingAxis = True
        else:
            raise Exception("Error!")

    def addVar(self, varName):
        
        print "self.listVars (0)", self.listVars

        global DataDictionary
        if varName not in DataDictionary:
            raise Exception(u"Error: Variable could not be displayed!")
        else:
            if not varName in self.listVars: 
                self.listVars.append(varName)
        print "self.listVars (1)", self.listVars
            
    def delVar(self, varName):
        
        global DataDictionary
        if varName not in DataDictionary:
            raise Exception(u"Error: Variable could not be deleted!")
        else:
            self.listVars.pop(varName)
            
    
class ColorFactory(object):
    
    def __init__(self):
        super(ColorFactory, self).__init__()
        self.listColor = [QtCore.Qt.red, \
                          QtCore.Qt.green, \
                          QtCore.Qt.lightGray,\
                          QtCore.Qt.cyan, \
                          QtCore.Qt.magenta, \
                          QtCore.Qt.yellow]
        self.idxColor = 0
        
        
    def getColor(self):
        idx = self.idxColor
        self.idxColor = (self.idxColor + 1) % len(self.listColor)
        return self.listColor[idx] 
