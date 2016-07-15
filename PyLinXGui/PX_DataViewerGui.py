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
        
        ###########################
        ### Toolbar
        toolbar = QtGui.QToolBar()
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        self.plotterWidget = PlotterWidget(self.varDispObj, self, self.mainController)
        self.setCentralWidget(self.plotterWidget)

        ###########################
        ### Actions
        self.adjustAction = QtGui.QAction('Adjust', self)
        self.adjustAction.setShortcut('Ctrl+A')
        self.adjustAction.triggered.connect(self.__onActionAdjust)
        toolbar.addAction(self.adjustAction)

        self.walkAxisAction = QtGui.QAction('Walking Axi s', self)
        self.walkAxisAction.setShortcut('Ctrl+W')
        self.walkAxisAction.triggered.connect(self.__onActionWalkingAxis)
        self.walkAxisAction.setCheckable(True)
        toolbar.addAction(self.walkAxisAction)

        self.saveAction = QtGui.QAction('Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.__onActionSave)
        toolbar.addAction(self.saveAction)

        self.legendAction = QtGui.QAction('Show Legend', self)
        self.legendAction.setShortcut('Ctrl+L')
        self.legendAction.triggered.connect(self.__onActionLegend)
        toolbar.addAction(self.legendAction)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Data-Viewer " + str(self.idx))
        
        self.listVars = list(self.varDispObj.get(u"setVars"))

    def __onActionAdjust(self):
        self.plotterWidget.adjust()    
        
    def __onActionSave(self):
        print "ActionSave"
        
    def __onActionLegend(self):
        print "ActionLegend"
        
    def __onActionWalkingAxis(self):
        if self.walkAxisAction.isChecked():
            self.plotterWidget.setBWalkingAxis(True)
        else:
            self.plotterWidget.setBWalkingAxis(False)
            
    def updateValues(self):
        self.plotterWidget.updateValues()

    def addVar(self, varName):
        print "addVar"
        self.plotterWidget.addVar(varName)
            
    def delVar(self, varName):
        print "delVar"
        self.plotterWidget.delVar(varName)
        
    def stop_run(self):
        self.plotterWidget.stop_run()

class PlotterWidget(QtGui.QWidget):
    
    def __init__(self, varDispObj,  mainWidget = None, mainController = None, parent = None ):
        super(PlotterWidget, self).__init__(parent)
        
        #Members
        self.mainController = mainController
        self.DataDictionary = self.mainController.getb("DataDictionary")
        self.margin = 50
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
        
        iniSettings = PlotSettings()
        self.setPlotSettings(iniSettings)       

        if self.listVars != None:
            for var in self.listVars:
                self.curveMap[var]=[]
                self.curveMapMemory[var] = []
          
        self.RunConfigDictionary = self.mainController.getb(u"RunConfigDictionary")
        
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
        if self.listVars != None:
            if len(self.listVars) > 0:
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

                self.refreshPixmap()
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
         
        return QtCore.QSize(6*self.margin,4*self.margin)
         
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
                    
    def mouseMoveEvent(self,event):
        if self.rubberBandIsShown:
            self.updateRubberBandRegion()
            self.rubberBandRect.setBottomRight(event.pos())
            self.updateRubberBandRegion()
            
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

    def __zoomToRect(self, rect, bAdjust = True):
        
            prevSettings = self.zoomStack[self.curZoom]                    
            settings = PlotSettings()
            
            dx = prevSettings.spanX() / (self.width() - 2*self.margin)
            dy = prevSettings.spanY() / (self.height()- 2*self.margin)
            
            
            settings.minX = prevSettings.minX + dx * (rect.left() - self.margin)
            settings.maxX = settings.minX + dx * (rect.right() - rect.left())
            settings.maxY = prevSettings.maxY - dy * (rect.top() - self.margin)
            settings.minY = settings.maxY - dy * (rect.bottom() - rect.top())

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
             
        self.pixmap = QtGui.QPixmap(self.size())
        self.pixmap.fill(self, 0,0)
        
        painter = QtGui.QPainter(self.pixmap)
        painter.initFrom(self)
        
        self.drawGrid(painter)
        self.drawCurves(painter)
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
            i += 1

            
    def stop_run(self):
        for var in self.listVars: 
            copyValues = copy.copy(self.curveMap[var])
            copyValuesMemory = copy.copy(self.curveMapMemory[var])
            self.curveMap[var] = copyValuesMemory
            self.curveMap[var].extend(copyValues )
        self.refreshPixmap()
            

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
    