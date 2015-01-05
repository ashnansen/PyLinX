'''
Created on 03.11.2014

@author: Waetzold Plaum
'''
# general modules to import
from PyQt4 import QtGui, QtCore
import inspect
import sys
import copy
import math


# project specific modules to import
import BContainer
import PX_Templates as PX_Templ
import PyLinXHelper


## Meta-Class for all PyLinX data Objects,

class PX_Object(BContainer.BContainer):
    
    def __init__(self, name, *args):
        
        super(PX_Object, self).__init__(name, *args)
        
    def getMaxID(self, _id = 0):
        
        keys = self._BContainer__Body.keys()
        for key in keys:
            element = self._BContainer__Body[key]
            types = inspect.getmro(type(element))
            if PX_IdObject in types:
                #element_id = element.get("ID")
                element_id = element.ID
                if element_id > _id:
                    _id = element_id
            _id = element.getMaxID(_id)
        return _id
    

## Classes, which should have an ID should inherit from this class

class PX_IdObject(PX_Object):
    
    __ID = 0
    
    def __init__(self, name, *args):
        super(PX_IdObject, self).__init__(name)
        self._ID = PX_IdObject.__ID
        PX_IdObject.__ID += 1
        
    def get_ID(self):
        return self._ID
    
    def set_ID(self, _id):
        self._ID = _id
        
    ID = property(get_ID, set_ID)


## Meta-Class for all objects that can be plotted in the main drawing area

class PX_PlotableObject (PX_Object):#, QtGui.QGraphicsItem):
    
    # Constructor  
    
    def __init__(self, name = None, *var):
        super(PX_PlotableObject, self).__init__(name)
        self.set("bVisible", False)
#         if type(self) == PX_PlotableObject:
#             self.set("px_mousePressedAt_X", sys.maxint)
#             self.set("px_mousePressedAt_Y", sys.maxint)
#             self._objectsInFocus = []
        self.set("px_mousePressedAt_X", sys.maxint)
        self.set("px_mousePressedAt_Y", sys.maxint)
        self._objectsInFocus = []

    
    
    ## Properties
    ################
            
    def get_objectsInFocus(self):
        return self._objectsInFocus
    
    def set_objectsInFocus(self, objectsInFocus):
        self._objectsInFocus = objectsInFocus
        
    objectsInFocus = property(get_objectsInFocus, set_objectsInFocus)
        
            
    def __isActive(self):
        
        parentElement = self.getParent()
        if parentElement  == None:
            return False
        objectsInFocus = copy.copy(parentElement.objectsInFocus)
        if self.ID in [ obj.ID for obj in objectsInFocus]:
            return  True
        else:
            return  False
    
    ## Method that gets an hulling polygon 
    
    def __getPolygon(self, x0,y0, x1, y1):
            delta = PX_Templ.Template.Gui.px_CONNECTOR_activeZone()
            # vertical
            if x0 == x1:
                if y0 < y1:
                    return [(x0, y0), (x0+delta,y0+delta), (x1+delta,y1-delta), (x1,y1), (x1 - delta,y1-delta), (x0-delta,y0+delta)]
                else:
                    return [(x1, y1), (x1+delta,y1+delta), (x0+delta,y0-delta), (x0,y0), (x0 - delta,y0-delta), (x1-delta,y1+delta)]
            # horicontal 
            elif y0 == y1:
                if x0 < x1:
                    return [(x0,y0),(x0 + delta,y0 + delta),(x1 - delta,y1 + delta),(x1,y1),(x1 - delta,y1 - delta),(x0+delta,y0-delta)]
                else:
                    return [(x1,y1),(x1 + delta,y1 + delta),(x0 - delta,y0 + delta),(x0,y0),(x0 - delta,y0 - delta),(x1+delta,y1-delta)]
            else:
                return None
            
  
    # general write method
    
    def write(self, obj, para = None):
        types = inspect.getmro(type(obj))
        if QtGui.QWidget in types:
            self.__plotHierarchyLevel(obj, para)
        else:
            pass
        
    
    # Method that plots one hierarchy level
    
    def __plotHierarchyLevel(self, target, templ):
        paint = QtGui.QPainter()
        paint.begin(target)
        listLatent = []
        for key in self._BContainer__Body:
            element = self._BContainer__Body[key]
            if element.isAttrTrue("bVisible"):
                if element.isAttrTrue("bLatent"):
                    listLatent.append(element)
                    continue
                element.plot(paint, templ)
        # latent elements has to be plottet on top
        for element in listLatent:
            element.plot(paint, templ)
        paint.end()    
        
    # Method that plots an element
    
    def plot(self, paint, templ):
        pass
    
    # Method that returns the object, that is in focus or none
    
    def getObjectInFocus(self, coord):
        x = coord.x()
        y = coord.y()
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))        
        keys = self._BContainer__Body
        returnVal = []
        for key in keys:
            element = self._BContainer__Body[key] 
            if element.isAttrTrue("bVisible"):
                if len(element.isInFocus(X,Y)) > 0:
                    returnVal.append(element)
        return returnVal
    
    # method that return the object and it's clicked pinIndex. Convention: negative index: inPin, posiive index: outPin
    
    def getPinInFocus(self, X, Y):
        keys = self._BContainer__Body
        for key in keys:
            element = self._BContainer__Body[key]
            if element.isAttrTrue("bVisible"):
                pass

  
## Meta-Class for all plotalble objects that can be connected
    
class PX_PlotableElement(PX_PlotableObject, PX_IdObject):

    # some static data structures 
    penBold                = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
    penBold.setJoinStyle(QtCore.Qt.MiterJoin)
    penLight               = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
    penNoBorder            = QtGui.QPen(PX_Templ.color.black,0, QtCore.Qt.SolidLine)
    penShadow              = QtGui.QPen(PX_Templ.color.grayLight, PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
    penHighlight           = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_ELEMENT_Highlight(), QtCore.Qt.SolidLine)
    penHighlight.setJoinStyle(QtCore.Qt.MiterJoin)
    penSimulationModeBold  = QtGui.QPen(PX_Templ.color.green,PX_Templ.Template.Gui.px_ELEMENT_PinSimulationWidth(), QtCore.Qt.SolidLine)
    penSimulationModeNone  = QtGui.QPen(PX_Templ.color.green,0, QtCore.Qt.SolidLine)
    fontStdVar             = QtGui.QFont("FreeSans", PX_Templ.Template.Gui.px_ELEMENT_stdFontSize())
    fontStdVarMetrics      = QtGui.QFontMetrics(fontStdVar)

    
    def __init__(self, name, X, Y, value = None):
        super(PX_PlotableElement, self).__init__(name, X, Y, value)
        self._X = X
        self._Y = Y
        
        #  Configuration
        self._idxActiveInPins = []
        self._idxActiveOutPins = []
        self._listOutPins = []
        self._listInPins  = []
        
        self.set("bMethodIsInFocus", True)
        self.set("setIdxConnectedInPins", set([]))
        self.set("setIdxConnectedOutPins", set([]))
        self.set("bVisible", True)        
        self.calcDimensions()
        
    ## Properties
    #############
    
    def set_X(self, X):
        self._X = X
        
    def get_X(self):
        return self._X
    
    X = property(get_X, set_X)
    
    def set_Y(self,Y):
        self._Y = Y
        
    def get_Y(self):
        return self._Y
    
    Y = property(get_Y, set_Y)
    
    def set_idxActiveOutPins(self, idxActiveOutPins):
        self._idxActiveOutPins = idxActiveOutPins
        
    def get_idxActiveOutPins(self):
        return self._idxActiveOutPins
    
    idxActiveOutPins = property(get_idxActiveOutPins, set_idxActiveOutPins)
    
    def set_idxActiveInPins(self, idxActiveInPins):
        self._idxActiveInPins = idxActiveInPins
        
    def get_idxActiveInPins(self):
        return self._idxActiveInPins
    
    idxActiveInPins = property(get_idxActiveInPins, set_idxActiveInPins)
    
    def set_listOutPins(self, listOutPins):
        self._listOutPins = listOutPins
        
    def get_listOutPins(self):
        return self._listOutPins
    
    listOutPins = property(get_listOutPins, set_listOutPins)
    
    def set_listInPins(self, listInPins):
        self._listInPins = listInPins
        
    def get_listInPins(self):
        return self._listInPins
    
    listInPins = property(get_listInPins, set_listInPins)     
    

    def calcDimensions(self,width         = PX_Templ.Template.Gui.px_ELEMENT_minWidth(),\
                              heigth        = PX_Templ.Template.Gui.px_EMELENT_minHeigth(),\
                              tupleInPins   = ((0,""),),\
                              tupleOutPins  = ((0,""),)):
        
        self.elementWidth       = width
        self.elementHeigth      = heigth
        self.border             = PX_Templ.Template.Gui.px_ELEMENT_Border()
        self.halfBorder           = 0.5 * self.border
        pinLength               = PX_Templ.Template.Gui.px_ELEMENT_pinLength() 
        elementWidth_half       = 0.5 * self.elementWidth
        elementHeigth_half      = 0.5 * self.elementHeigth
        px_ELEMENT_pinHeigth    = PX_Templ.Template.Gui.px_ELEMENT_pinHeigth()
        self.triangleOffset     = px_ELEMENT_pinHeigth * PX_Templ.Template.Gui.r_60deg()
        self.pinHalfHeigth      = 0.5 * px_ELEMENT_pinHeigth
        lengthWholePin          = self.triangleOffset + pinLength
        rightEndpoint_x         = lengthWholePin  + elementWidth_half
        self.x                  = self._X - elementWidth_half
        self.y                  = self._Y - elementHeigth_half 
        self.x_end              = self.x + self.elementWidth
        self.y_end              = self.y + 0.5 * self.elementHeigth
        self.bActive            = self._PX_PlotableObject__isActive()
        
        # Shape
        
        self.set("Shape",[[(- elementWidth_half, - elementHeigth_half),\
                           (  elementWidth_half, - elementHeigth_half),\
                           (  elementWidth_half,   elementHeigth_half),\
                           (- elementWidth_half,   elementHeigth_half),\
                           ]])
        
        # In- and Outpins
        listInPins   = [(- rightEndpoint_x, inPin[0], - elementWidth_half, inPin[0],  inPin[1])  for inPin  in tupleInPins]
        listOutPins  = [(  rightEndpoint_x, outPin[0],  elementWidth_half, outPin[0], outPin[1]) for outPin in tupleOutPins]       
        ShapeInPins =  [self._PX_PlotableObject__getPolygon(*inPin[0:4])  for inPin  in listInPins]
        ShapeOutPins = [self._PX_PlotableObject__getPolygon(*outPin[0:4]) for outPin in listOutPins]
                
        self._listInPins = listInPins
        self._listOutPins = listOutPins
        self.set("ShapeInPins",  ShapeInPins )
        self.set("ShapeOutPins", ShapeOutPins )
        
        
    ## Method to plot the main square of the Element
        
    def plotBasicElement(self, paint, templ):
    
        
        ## plot the main square of the Element
                
        if self.bActive:
            paint.setPen(PX_PlotableElement.penHighlight)
            paint.setBrush(PX_Templ.brush.Highlight)
            paint.drawRect(self.x,self.y, self.elementWidth, self.elementHeigth)
        else:
            # background shadow
            paint.setPen(PX_PlotableElement.penShadow)
            paint.drawRect(self.x + self.border ,self.y + self.border, self.elementWidth, self.elementHeigth)
            
        # main square
        paint.setPen(PX_PlotableElement.penBold)
        paint.setBrush(PX_Templ.brush.white)
        paint.drawRect(self.x,self.y, self.elementWidth, self.elementHeigth)


        ## plots Connoctor Inputs
    
        paint.setPen(PX_PlotableElement.penNoBorder)
        paint.setBrush(PX_Templ.brush.black)
        listInPins = self.listInPins
        paint.setPen(PX_PlotableElement.penNoBorder)
        paint.setBrush(PX_Templ.brush.black)
        idxActiveInPins = self.idxActiveInPins
        
        for i in range(len(listInPins)):
            paint.setPen(self.penNoBorder)
            inPin = listInPins[i]
            path        = QtGui.QPainterPath()
            x_pin       = inPin[0] + self._X
            y_pin       = inPin[1] + self._Y
            x_pinEnd    = inPin[2] + self._X
            #y_pinEnd    = inPin[3] 
            x_arrow = x_pinEnd - self.triangleOffset   

            path.moveTo(    x_arrow,    y_pin - self.pinHalfHeigth)
            path.lineTo(    x_pinEnd,   inPin[3] + self.Y)
            path.lineTo(    x_arrow,    y_pin + self.pinHalfHeigth)
            path.lineTo(    x_arrow,    y_pin - self.pinHalfHeigth)
            
            paint.drawPath(path)

            if -i-1 in idxActiveInPins:
                paint.setPen(PX_PlotableElement.penBold)
            else:
                paint.setPen(PX_PlotableElement.penLight)
            paint.drawLine( x_pin,y_pin,x_arrow ,y_pin)                
   
    
        ## plot Connoctor Outputs
     
        paint.setPen(PX_PlotableElement.penLight)
        paint.setBrush(PX_Templ.brush.white)
        listOutPins = self.listOutPins
        paint.setPen(PX_PlotableElement.penNoBorder)
        paint.setBrush(PX_Templ.brush.white)
        idxActiveOutPins = self.idxActiveOutPins

        for i in range(len(listOutPins)):
            paint.setPen(self.penNoBorder)
            outPin = listOutPins[i]
            path        = QtGui.QPainterPath()
            x_pin       = outPin[0] + self._X
            y_pin       = outPin[1] + self._Y
            x_pinEnd    = outPin[2] + self._X + self.halfBorder
            #y_pinEnd    = inPin[3] 
            x_arrow = x_pinEnd + self.triangleOffset   

            path.moveTo(    x_pinEnd,    y_pin - self.pinHalfHeigth)
            path.lineTo(    x_arrow,     outPin[3] + self.Y)
            path.lineTo(    x_pinEnd,    y_pin + self.pinHalfHeigth)
            path.lineTo(    x_pinEnd,    y_pin - self.pinHalfHeigth)
            
            paint.drawPath(path)
            
            if i in idxActiveOutPins:
                paint.setPen(PX_PlotableElement.penBold)
            else:
                paint.setPen(PX_PlotableElement.penLight)
            paint.drawLine( x_pin,y_pin,x_arrow ,y_pin)
            

    # Method which determins if a point is inside the pin of the element 
    
    def isPinInFocus(self, X, Y):
        
        x = self._X
        y = self._Y

        X = X - x
        Y = Y - y  
        
        ShapeInPins  = self.get("ShapeInPins")
        ShapeOutPins = self.get("ShapeOutPins")
        
        #idxInPins  = PyLinXHelper.point_inside_polygon(X, Y, ShapeInPins)
        idxInPins  = PyLinXHelper.point_inside_polygon(X, Y, ShapeInPins) 
        #print "idxInPins: ", idxInPins
        
        if idxInPins != []:
            idxInPins = [-idx -1 for idx in idxInPins]
            self.idxActiveInPins = idxInPins
            return self, idxInPins  
        
        idxOutPins = PyLinXHelper.point_inside_polygon(X, Y, ShapeOutPins)
        
        if idxOutPins != []:
            self.idxActiveOutPins = idxOutPins
            return self, idxOutPins
        
        self.idxActiveInPins = []
        self.idxActiveOutPins = []
        
        return None, []


    # Method which determins if a point is inside the shape of the element
    
    def isInFocus(self, X, Y):
        
        x = self._X
        y = self._Y

        X = X - x
        Y = Y - y
        
        return PyLinXHelper.point_inside_polygon(X, Y, self.get("Shape"))

## Proxy class used as place holder of the target object of a connector during drawing the connection

class PX_PlottableProxyElement(PX_PlotableElement):
    
    def __init__(self, X, Y):
        
        super(PX_PlottableProxyElement, self).__init__("PX_PlottableProxyElement", X, Y, None)
        self.listInPins = [(0,0,0,0)]
    
    def isInFocus(self, X, Y):
        return []


## Class for variable Elements

class  PX_PlotableVarElement(PX_PlotableElement):
    
    def __init__(self, name, X, Y, value = None):
        
        super(PX_PlotableVarElement, self).__init__(name, X, Y)
        self.__Head = value 
        PX_PlotableElement.calcDimensions(self)
        #self.set("bMeasure", False)
        #self.set("bSimulation", False)
        self.set("bStimulate", False)
        self.set("bMeasure", False)
        
        
    def plot(self, paint, templ):

        ## Method to plot the color bar of a variable element
        
        def __plotElementSpecifier():
            
            # color bar 
            paint.setPen(PX_PlotableElement.penLight)
            paint.setBrush(PX_Templ.brush.blueLocalVar)
            paint.drawRect(self.x + self.halfBorder,\
                           self.y + self.halfBorder,\
                           PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar(),\
                           PX_Templ.Template.Gui.px_EMELENT_minHeigth() - self.halfBorder)
            posText_x = self.x + PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar() + whiteSpace
            posText_y = self.y + 0.5 * (PX_PlotableElement.fontStdVarMetrics.ascent() + PX_Templ.Template.Gui.px_EMELENT_minHeigth()) 
            paint.drawText(posText_x, posText_y, name)
            
        def __drawStimulationPoint():
            
            paint.setPen(PX_PlotableElement.penSimulationModeBold)
            paint.setBrush(PX_Templ.brush.green)

            x0 = self._X + PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x()
            y0 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation()
            x1 = x0
            y1 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_MediumLight() - \
                        PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() * PX_Templ.Template.Gui.r_60deg()            
            paint.drawLine( x0,y0,x1 ,y1)
                        
            paint.setPen(PX_PlotableElement.penSimulationModeNone)
            x0 = self._X + PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x() 
            y0 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            x1_offset = PX_Templ.Template.Gui.r_60deg() * PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() 
            x1 = x0 - x1_offset 
            x2 = x0 + x1_offset
            y2 = y1

            path        = QtGui.QPainterPath()
            path.moveTo( x0,y0)
            path.lineTo(x1,y1)
            path.lineTo(x2,y2)
            path.lineTo(x0,y0)
            paint.drawPath(path)     


        def __drawMeasurePoint():
            
            paint.setPen(PX_PlotableElement.penSimulationModeBold)
            paint.setBrush(PX_Templ.brush.green)

            x0 = self._X - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x()
            y0 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            x1 = x0
            y1 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_MediumLight() - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation() + \
                        PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() * PX_Templ.Template.Gui.r_60deg()            
            paint.drawLine( x0,y0,x1 ,y1)
                        
            paint.setPen(PX_PlotableElement.penSimulationModeNone)
            x0 = self._X - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x() 
            y0 = self._Y - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation()
            x1_offset = PX_Templ.Template.Gui.r_60deg() * PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() 
            x1 = x0 - x1_offset 
            x2 = x0 + x1_offset
            y2 = y1

            path  = QtGui.QPainterPath()
            path.moveTo( x0,y0)
            path.lineTo(x1,y1)
            path.lineTo(x2,y2)
            path.lineTo(x0,y0)
            paint.drawPath(path)       
            
        paint.setFont(PX_PlotableElement.fontStdVar)
        name = self.get("Name")
        widthName  = PX_PlotableElement.fontStdVarMetrics.width(name)
        whiteSpace = PX_Templ.Template.Gui.px_ELEMENT_whiteSpace()
        width_raw = PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar() + 2 *  whiteSpace  + 4 *  self.border + widthName 
        # round!
        width  = 20 * math.ceil(0.05 * float(width_raw) )
        heigth = PX_Templ.Template.Gui.px_EMELENT_minHeigth()
        
        PX_PlotableElement.calcDimensions(self,width, heigth)
        PX_PlotableElement.plotBasicElement(self, paint, templ)
        __plotElementSpecifier()
        
        rootContainer = self.getRoot()
        bSimulationMode = rootContainer.get("bSimulationMode")
                
        if bSimulationMode:
        
            if self.get("bStimulate"):
                __drawStimulationPoint()
            if self.get("bMeasure"):
                __drawMeasurePoint()


## Class for binary Operators

class PX_PlotableBasicOperator(PX_PlotableElement):
    
    penSpecifier   = QtGui.QPen(PX_Templ.color.blue,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
    brushSpecifier = QtGui.QBrush(PX_Templ.color.blueTransp)
    
    def __init__(self, X, Y, value = None):
        n = PX_IdObject._PX_IdObject__ID + 1
        name = "Operator_" + value + "_id" + str(n)
        super(PX_PlotableBasicOperator, self).__init__(name, X, Y)
        self._BContainer__Head = value
        PX_PlotableElement.calcDimensions(self)
        
    def plot(self,paint,templ):
        
        def __plotPlusSpecifier():
            
            paint.setPen(PX_PlotableBasicOperator.penSpecifier)
            paint.setBrush(PX_PlotableBasicOperator.brushSpecifier)
            
            innerDiam = PX_Templ.Template.Gui.px_PLOTABLEELEMOPERATOR_innerDiameter()
            outerDiam = PX_Templ.Template.Gui.px_PLOTABLEELEMOPERATOR_outerDiameter()
            
            #plotting the "+" 
            path = QtGui.QPainterPath()
            path.moveTo( self._X + innerDiam, self._Y + innerDiam)
            path.lineTo( self._X + innerDiam, self._Y + outerDiam)
            path.lineTo( self._X - innerDiam, self._Y + outerDiam)
            path.lineTo( self._X - innerDiam, self._Y + innerDiam)
            path.lineTo( self._X - outerDiam, self._Y + innerDiam)
            path.lineTo( self._X - outerDiam, self._Y - innerDiam)
            path.lineTo( self._X - innerDiam, self._Y - innerDiam)
            path.lineTo( self._X - innerDiam, self._Y - outerDiam)
            path.lineTo( self._X + innerDiam, self._Y - outerDiam)
            path.lineTo( self._X + innerDiam, self._Y - innerDiam)
            path.lineTo( self._X + outerDiam, self._Y - innerDiam)
            path.lineTo( self._X + outerDiam, self._Y + innerDiam)
            path.lineTo( self._X + innerDiam, self._Y + innerDiam)
            paint.drawPath(path)        

        size = PX_Templ.Template.Gui.px_PLOTABLEELEMOPERATOR_size()
        stdPinDistance =  PX_Templ.Template.Gui.px_ELEMENT_stdPinDistance()
        stdPinDistance_half = 0.5 * stdPinDistance 
        
        PX_PlotableElement.calcDimensions(self, size, size,((-stdPinDistance_half, ""), (stdPinDistance_half, "")))
        PX_PlotableElement.plotBasicElement(self, paint, templ)
        
        if self._BContainer__Head == "+":
            __plotPlusSpecifier()
        elif self._BContainer__Head == "-":
            pass
        
        
## Meta-Class for all connections of objects from the type PX_Variables

class PX_PlottableConnector(PX_PlotableObject, PX_IdObject):
    
    def __init__(self, elem0, elem1 = None, listPoints = [], idxOutPin = 0, idxInPin = -1):
        
        super(PX_PlottableConnector, self).__init__()
        id_0 = elem0.ID
        self.set("ID_0", id_0)
        self._elem0 = elem0
        self.set("bVisible", True)
        self._idxOutPin = idxOutPin
        self._idxInPin = idxInPin
        
        if elem1 != None:
            id_1 = elem1.ID
            self.set("ID_1", id_1)
            self._elem1 = elem1
        else:
            self.set("ID_1", None)
            self._elem1 = None
            
        X = elem0.X
        Y = elem0.Y
        
        # list points saves for odd indices x-values and for even indices y-values of the corresponding corners of the connector
        for i in range(len(listPoints)):
            #x-value
            if i%2==0:
                listPoints[i] = listPoints[i] - X 
            #y-value
            else:
                listPoints[i] = listPoints[i] - Y       
        self.set("listPoints", listPoints)
        
        self.rad = PX_Templ.Template.Gui.px_CONNECTOR_rad()
        self.diam = 2 * self.rad
        self.__calcDimensions()
            
    ## Properties
    #######################
    
    @property
    def X(self):
        return self.X0
    
    @property
    def Y(self):
        return self.Y0 
    
    def get_elem0(self):
        return self._elem0
    
    def set_elem0(self, elem0):
        self._elem0 = elem0
        
    elem0 = property(get_elem0, set_elem0)

    def get_elem1(self):
        return self._elem1
    
    def set_elem1(self, elem1):
        id_1 = elem1.ID
        self._elem1 = elem1
        BContainer.BContainer.set(self,"ID_1", id_1)
        
    elem1 = property(get_elem1, set_elem1)
    
    def get_listOutPins(self):
        return self._listOutPins
    
    def set_listOutPins(self, listOutPins):
        self._listOutPins = listOutPins
        
    listOutPins = property(get_listOutPins, set_listOutPins)
    
    def get_listInPins(self):
        return self._listInPins
    
    def set_listInPins(self, listInPins):

        self._listInPins = listInPins

        
    listInPins = property(get_listInPins, set_listInPins)
    
    def get_idxOutPin(self):
        return self._idxOutPin
    
    def set_idxOutPin(self, idxOutPin):
        self._idxOutPin = idxOutPin
        
    idxOutPin = property(get_idxOutPin, set_idxOutPin)    


    def get_idxInPin(self):
        return self._idxInPin
    
    def set_idxInPin(self, idxInPin):
        self._idxInPin = idxInPin
        
    idxInPin = property(get_idxInPin, set_idxInPin)
    
    
    
           
    def __calcDimensions(self):

        # Getting data
        ############################
        
        elem0 = self.elem0
        elem1 = self.elem1
        self.X0 = elem0._X
        self.Y0 = elem0._Y
        self.X1 = elem1._X
        self.Y1 = elem1._Y
        self.listOutPins0 = elem0.listOutPins
        self.listInPins1  = elem1.listInPins
        
        self.listPoints = list(self.get("listPoints"))
                
        idxOutPin = self.idxOutPin
        idxInPin = self.idxInPin
        
        self.outPin_x =  self.listOutPins0[ idxOutPin ][0]
        self.outPin_y =  self.listOutPins0[ idxOutPin ][1] 
        idxInPin_transformed =  - idxInPin - 1 
        self.inPin_x  =  self.listInPins1 [ idxInPin_transformed  ][0]
        self.inPin_y  =  self.listInPins1 [ idxInPin_transformed  ][1]

        
        len_listPoints = len(self.listPoints)
        
        # determine if the connector is finished or not
        
        types = inspect.getmro(type(elem1))
        if PX_PlottableProxyElement in types:
            self.bNoFinalConnection = True
        else:
            self.bNoFinalConnection = False
        
        # This code is quite complicated. It inserts extra points to listPoints
        # to make drawing more convenient to the user. There is no abstract princoble
        # applied but the conditions have grown by time. Maybe this could be done more
        # elegant...
        ###############################################################################
        
        #Case final connection
        if self.bNoFinalConnection == False:
        
            if len_listPoints > 0:
                # x-Values
                if len_listPoints %2==0:
                    pass
                    self.listPoints[-1] = self.inPin_y + self.Y1 - self.Y0 
                # y-Values
                else:
                    if len_listPoints > 1:
                        if self.listPoints[-2] != self.outPin_y:
                            self.listPoints.append(self.inPin_y + self.Y1 - self.Y0 )
                    else:
                        if self.Y0 != self.Y1:
                            self.listPoints.append(self.inPin_y + self.Y1 - self.Y0 )
                            
            else:
                self.listPoints.append(self.inPin_x + self.X1 - self.X0 - self.rad )
                self.listPoints.append(self.Y1 - self.Y0 +  self.inPin_y  )
                            
        #Case no final connection
        else:
            if len_listPoints %2==0:
                self.listPoints.append(self.X1 - self.X0 )
            else:
                # self.listPoints.append(self.Y1 - self.Y0  )
                self.listPoints.append(self.Y1 - self.Y0 + self.inPin_y )
        
        len_listPoints = len(self.listPoints)
        len_listPoints_minus_1 = len_listPoints - 1 
        
        #Case final connection
        if self.bNoFinalConnection == False:
            self.set("listPoints", self.listPoints)
        
        # Determining the shape of the connector
        # From the "Shape" the GUI knows where an object
        # is located. The "Shape" has not be the real 
        # visible shape of the graphical object.
        # the "Shape" of the connector is composed by
        # six point polygones and is  broader than the
        # visible shape for convenience reasons
        ##############################################
        
        shape = []
        
        x1_cache = self.outPin_x
        y1_cache = self.outPin_y
        
        for i in range(0, len_listPoints):

            x0 = x1_cache
            y0 = y1_cache
            if i%2 == 0:
                x1 = self.listPoints[i]
                y1 = y1_cache
            else:
                x1 = x1_cache
                y1 = self.listPoints[i]
            shape.append(self._PX_PlotableObject__getPolygon(x0,y0,x1,y1))
            #print "x0: ", x0, "y0: ", y0, "x1: ", x1, "y1: ", y1 
            x1_cache = x1
            y1_cache = y1
            if i == len_listPoints_minus_1:
                x0 = x1_cache
                y0 = y1_cache
                x1 = self.inPin_x + self.X1 - self.X0
                #y1 = self.inPin_y + self.Y1 - self.Y0 
                y1 = self.inPin_y + self.Y1 - self.Y0 
                shape.append(self._PX_PlotableObject__getPolygon(x0,y0,x1,y1))
                #print "x0: ", x0, "y0: ", y0, "x1: ", x1, "y1: ", y1 
   
        self.set("Shape",shape )
  
    def plot(self, paint, templ):
        
        # preparing plotting
        ####################
        
        self.__calcDimensions()
        bActive = self._PX_PlotableObject__isActive()
        path    = QtGui.QPainterPath()
        path.moveTo(self.outPin_x + self.X0, self.outPin_y + self.Y0)

        x1=0
        y1=0
        listPoints = copy.copy(self.listPoints)
 
        
        # transforming the relative coordinates to absolute coordinates
        #
        # Convention listPoints = [x_0,y_0, x_1, y_1, x_2, y_2...]
        # The first  corner is always from horizontal line to vertical  line
        # the second corner is always from vertical  line to horizontal line        
        #
        ###############################################################
        
        for i in range(len(listPoints)):

            #x-value
            if i%2==0:
                listPoints[i] = listPoints[i] + self.X0
            #y-value
            else:
                listPoints[i] = listPoints[i] + self.Y0
        
        # Going through all corners of the connector
        ################################################################
        
        len_listPoints = len(listPoints)
        
        for i in range(len_listPoints):

            # Determining three points. 
            #   (x0, y0) The point of the last corner
            #   (x1, y1) the point of the current corner
            #   (x2, y2) the point of the next corner 
            ############################################

            if i == 0:
                x0 = self.outPin_x + self.X0
                y0 = self.outPin_y + self.Y0
            else:
                x0 = x1
                y0 = y1
            # x-Values
            if i%2==0:
                x1 = listPoints[i]
                y1 = y0
            # y-Values
            else:
                x1 = x0
                y1 = listPoints[i]
            if i == (len_listPoints - 1):
                x2 = self.inPin_x + self.X1
                y2 = self.inPin_y + self.Y1
            else:
                # x-Values
                if i%2==0:
                    x2 = listPoints[i]
                    y2 = listPoints[i+1]
                # y-Values
                else:
                    x2 = listPoints[i + 1]
                    y2 = listPoints[i]  
            #print "-------------------------"              
            #print "x0: ", x0, "y0: ", y0
            #print "x1: ", x1, "y1: ", y1
            #print "x2: ", x2, "y2: ", y2
            
            if (self.bNoFinalConnection and i == (len_listPoints - 1)) \
                      or y0 == y2 \
                      or x0 == x2:            
                radOffset = 0
            else:
                radOffset = self.rad    
            
            # Ploting of the rounded corners of the connector
            #################################################
            
            # x-Values
            if i%2==0:
                if x0 > x1:
                    path.lineTo(x1 + radOffset, y1)
                    if radOffset != 0:
                        if y2 < y1:
                            path.arcTo(x1,             y1 - self.diam, self.diam, self.diam,270,-90)
                        else:
                            path.arcTo(x1,             y1            , self.diam, self.diam,90,90)
                else:
                    path.lineTo(x1 - radOffset, y1)
                    if radOffset != 0:                    
                        if y2 < y1:
                            path.arcTo(x1 - self.diam, y1 - self.diam, self.diam, self.diam,270,90)
                        else:
                            path.arcTo(x1 - self.diam, y1            , self.diam, self.diam,90,-90)
                
            #y-Values
            else:
                if y0 < y1:
                    path.lineTo(x1, y1 - radOffset)
                    if radOffset != 0:
                        if x2 > x1:
                            path.arcTo(x1,             y1 - self.diam, self.diam, self.diam,180,90)
                        else:
                            path.arcTo(x1 - self.diam, y1 - self.diam, self.diam, self.diam,0,-90)
                else:
                    path.lineTo(x1, y1 + radOffset)
                    if radOffset != 0:
                        if x2 > x1:
                            path.arcTo(x1,             y1            , self.diam, self.diam,180,-90)
                        else:
                            path.arcTo(x1 - self.diam, y1            , self.diam, self.diam,0,90)
                    
        
        x2 = self.inPin_x + self.X1
        y2 = self.inPin_y + self.Y1
        if self.bNoFinalConnection == False:
            path.lineTo(x2,y2)  
        
        
        # Ploting the final path
        ########################       
        
        paint.setBrush(PX_Templ.brush.transparent)
        
        if bActive:
            # Connector is highlighted
            pen2 = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_CONNECTOR_highlight(), QtCore.Qt.SolidLine) 
            paint.setPen(pen2)
            paint.drawPath(path) 
        
        pen  = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_CONNECTOR_line(), QtCore.Qt.SolidLine)    
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        paint.setPen(pen)       
        paint.drawPath(path)   
        
    def isInFocus(self, X, Y):
        
        x = self.X
        y = self.Y

        X = X - x
        Y = Y - y
        
        return PyLinXHelper.point_inside_polygon(X, Y, self.get("Shape"))


## Class for highlightning

class PX_LatentPlottable_HighlightRect(PX_PlotableObject):
    
    def __init__(self, X, Y):
        
        super(PX_LatentPlottable_HighlightRect, self).__init__()
        self.set("bLatent", True)
        self.set("X0", X)
        self.set("Y0", Y)
        self.set("X1", X)
        self.set("Y1", Y)
        self.set("Name", "HighlightObject")
        self.set("bVisible", True)
        
        
    def plot(self, paint, templ):
        
        X0 = self.get("X0")
        Y0 = self.get("Y0")
        X1 = self.get("X1")
        Y1 = self.get("Y1")
        
        pen = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_HIGHLIGHT_border(), QtCore.Qt.SolidLine)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        paint.setPen(pen)
        paint.setBrush(PX_Templ.brush.HighlightTransp)
        paint.drawRect(X0, Y0, X1-X0, Y1-Y0)
        
        
    def isInFocus(self, X, Y):
        return []



