'''
Created on 03.11.2014

@author: Waetzold Plaum
'''
# general modules to import
from PyQt4 import QtGui, QtCore
import inspect
import sys
import copy

# project specific modules to import
import BContainer
import PX_Templates as PX_Templ
import PyLinXHelper



## Meta-Class for all PyLinX data Objects

class PX_Object(BContainer.BContainer):
    
    __ID = 0
    
    def __init__(self, name, *args):
        super(PX_Object, self).__init__(name)
        self.set("ID", PX_Object.__ID)
        PX_Object.__ID += 1


## Meta-Class for all objects that can be plotted in the main drawing area

class PX_PlotableObject (PX_Object):#, QtGui.QGraphicsItem):
    
    # Constructor  
    
    def __init__(self, name = None, *var):
        super(PX_PlotableObject, self).__init__(name)
        self.set("bPlottable", True)
        if type(self) == PX_PlotableObject:
            self.set("px_mousePressedAt_X", sys.maxint)
            self.set("px_mousePressedAt_Y", sys.maxint)
            self.set("objectsInFocus", [])
            
    def __isActive(self):
        
        parentElement = self.getParent()
        if parentElement  == None:
            return False
        if parentElement.isAttr("objectsInFocus"):
            objectsInFocus = copy.copy(parentElement.get("objectsInFocus"))
        else:
            return False
        
        if self.get("ID") in [ obj.get("ID") for obj in objectsInFocus]:
            return  True
        else:
            return  False        


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
            if element.isAttrTrue("bPlottable"):
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
    
    def getObjectInFocus(self, X, Y):
        keys = self._BContainer__Body
        returnVal = []
        for key in keys:
            element = self._BContainer__Body[key] 
            if element.isAttrTrue("bPlottable"):
                if len(element.isInFocus(X,Y)) > 0:
                    returnVal.append(element)
        return returnVal
    
    # method that return the object and it's clicked pinIndex. Convention: negative index: inPin, posiive index: outPin
    
    def getPinInFocus(self, X, Y):
        keys = self._BContainer__Body
        for key in keys:
            element = self._BContainer__Body[key]
            if element.isAttrTrue("bPlottable"):
                pass

## Meta-Class for all plotalble objects that can be connected
    
class PX_PlotableElement(PX_PlotableObject):
    
    def __init__(self, name, X, Y, value = None):
        super(PX_PlotableElement, self).__init__(name, X, Y, value)
        self.set("X", X)
        self.set("Y", Y)
        
        
    def plot(self, paint, templ): 
        pass

## Proxy class used as place holder of the target object of a connector during drawing the connection

class PX_PlottableProxyElement(PX_PlotableElement):
    
    def __init__(self, X, Y):
        
        super(PX_PlottableProxyElement, self).__init__("PX_PlottableProxyElement", X, Y, None)
        self.set("listInPins", [(0,0,0,0)])
        #self.set("listPoints", [])
    
    def isInFocus(self, X, Y):
        return []

## Class for variable Elements

class PX_PlotableVarElement(PX_PlotableElement):
    
    def __init__(self, name, X, Y, value = None):
        super(PX_PlotableVarElement, self).__init__(name, X, Y)
        self.__Head = value
        
        #  Configuration
        self.set("bMethodIsInFocus", True)
        self.set("idxActiveInPins", [])
        self.set("idxActiveOutPins", [])
        self.set("setIdxConnectedInPins", set([]))
        
        # some static data structures 
        self.pen                = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
        self.pen2               = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
        self.pen3               = QtGui.QPen(PX_Templ.color.black,0, QtCore.Qt.SolidLine)
        self.penShadow          = QtGui.QPen(PX_Templ.color.grayLight,PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
        self.__calcDimensions() 
        
    def __calcDimensions(self):
        
        self.border             = PX_Templ.Template.Gui.px_ELEMENT_Border()
        self.elementWidth       = PX_Templ.Template.Gui.px_ELEMENT_minWidth()
        self.elementHeigth      = PX_Templ.Template.Gui.px_EMELENT_minHeigth()
        self.halfLine           = 0.5 * self.border
        self.pinLength          = PX_Templ.Template.Gui.px_ELEMENT_pinLength() 
        self.elementWidth_half  = 0.5 * self.elementWidth
        self.elementHeigth_half = 0.5 * self.elementHeigth
        self.triangleOffset     = 0.5 * self.elementHeigth * PX_Templ.Template.Gui.r_60deg()
        self.pinHeigth          = 0.25 * self.elementHeigth 
        self.lengthWholePin     = self.triangleOffset + self.pinLength
        self.rightEndpoint_x    = self.lengthWholePin  + self.elementWidth_half       

        self.set("Shape",[[(- self.elementWidth_half, - self.elementHeigth_half),\
                           (  self.elementWidth_half, - self.elementHeigth_half),\
                           (  self.elementWidth_half,   self.elementHeigth_half),\
                           (- self.elementWidth_half,   self.elementHeigth_half),\
                           ]])
        
        listInPins  =  [(- self.rightEndpoint_x, 0, - self.elementWidth_half, 0)]
        listOutPins =  [(  self.rightEndpoint_x, 0,   self.elementWidth_half, 0)]
        
        ShapeInPins =  [self._PX_PlotableObject__getPolygon(*inPin)  for inPin  in listInPins]
        ShapeOutPins = [self._PX_PlotableObject__getPolygon(*outPin) for outPin in listOutPins]
                
        #print "ShapeInPins: ", ShapeInPins 
        #print "ShapeOutPins: ", ShapeOutPins   
                
        self.set("listInPins",   listInPins  )
        self.set("listOutPins",  listOutPins )
        self.set("ShapeInPins",  ShapeInPins )
        self.set("ShapeOutPins", ShapeOutPins )

        
    def plot(self, paint, templ):

        ## preparing data
        
        x = self.get("X")
        y = self.get("Y")
        
        #paint.setRenderHint(QtGui.QPainter.Antialiasing)
        
        x = x - self.elementWidth_half
        y = y - self.elementHeigth_half
        
        x_end        = x + self.elementWidth
        y_end        = y + 0.5 * self.elementHeigth
            
        bActive = self._PX_PlotableObject__isActive()
            
        self.__calcDimensions()

        self.pen.setJoinStyle(QtCore.Qt.MiterJoin)

        # The attribute Shape contains a list of x-y-coordinates forming a polygone of the chape of the plotte element 
        
        if bActive:
            penHighlight = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_ELEMENT_Highlight(), QtCore.Qt.SolidLine)
            penHighlight.setJoinStyle(QtCore.Qt.MiterJoin)
            paint.setPen(penHighlight)
            paint.setBrush(PX_Templ.brush.Highlight)
            paint.drawRect(x,y, self.elementWidth, self.elementHeigth)
        else:
            # background shadow
            paint.setPen(self.penShadow)
            paint.drawRect(x+ self.border ,y + self.border, self.elementWidth, self.elementHeigth)
            

        # connector input
        paint.setPen(self.pen3)
        paint.setBrush(PX_Templ.brush.black)
        path = QtGui.QPainterPath()
        
        x_begin = x - self.triangleOffset   
        path.moveTo(x_begin , y + self.pinHeigth)
        path.lineTo(x , y + 2 * self.pinHeigth)
        path.lineTo(x_begin ,y  + 3 * self.pinHeigth)
        path.lineTo(x_begin , y + self.pinHeigth)
        paint.drawPath(path)
        idxActiveInPins = self.get("idxActiveInPins")
        if idxActiveInPins == []:
            paint.setPen(self.pen2)
        else:
            paint.setPen(self.pen)
        paint.drawLine( x_begin - self.pinLength,y + 2 * self.pinHeigth,x_begin ,y + 2 * self.pinHeigth) 
         
        # connector output    
        paint.setPen(self.pen2)
        paint.setBrush(PX_Templ.brush.white)
        path = QtGui.QPainterPath()
        path.moveTo(x_end , y_end - self.pinHeigth)
        x_endpoint = x_end +  self.triangleOffset
        path.lineTo(x_endpoint , y_end)
        path.lineTo(x_end, y_end + self.pinHeigth)
        paint.drawPath(path)
        idxActiveOutPins = self.get("idxActiveOutPins")
        if idxActiveOutPins == []:
            paint.setPen(self.pen2)
        else:
            paint.setPen(self.pen)
        paint.drawLine(x_endpoint , y_end, x_endpoint + self.pinLength, y_end )

        # highlighting the Element
        
    
        # meon square
        paint.setPen(self.pen)
        paint.setBrush(PX_Templ.brush.white)
        paint.drawRect(x,y, self.elementWidth, self.elementHeigth)
        
        
        # color bar 
        paint.setPen(self.pen2)
        paint.setBrush(PX_Templ.brush.blueLocalVar)
        paint.drawRect(x + self.halfLine,\
                       y + self.halfLine,\
                       PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar(),\
                       PX_Templ.Template.Gui.px_EMELENT_minHeigth() - self.halfLine)
        

            


        
    # Method which determins if a point is inside the shape of the element
    
    def isInFocus(self, X, Y):
        
        x = self.get("X")
        y = self.get("Y")

        X = X - x
        Y = Y - y
        
        return PyLinXHelper.point_inside_polygon(X, Y, self.get("Shape"))


    # Method which determins if a point is inside the pin of the element 
    
    def isPinInFocus(self, X, Y):
        
        x = self.get("X")
        y = self.get("Y")

        X = X - x
        Y = Y - y  
        
        ShapeInPins  = self.get("ShapeInPins")
        ShapeOutPins = self.get("ShapeOutPins")
        
        idxInPins  = PyLinXHelper.point_inside_polygon(X, Y, ShapeInPins)
        idxOutPins = PyLinXHelper.point_inside_polygon(X, Y, ShapeOutPins)
        
        if idxInPins != []:
            idxInPins = [-idx for idx in idxInPins]
            self.set("idxActiveInPins", idxInPins)
            return self, idxInPins  
        
        if idxOutPins != []:
            self.set("idxActiveOutPins", idxOutPins)
            return self, idxOutPins
        
        self.set("idxActiveInPins", [])
        self.set("idxActiveOutPins", [])
        
        return None, []
    
    
    def get(self, attr):
        
        if attr == "setIdxConnectedInPins":
            return self.__get_setIdxConnectedInPins()
        else:
            return PX_PlotableObject.get(self,attr)
        
    def __get_setIdxConnectedInPins(self):
        
        ## TODO: for complex models this method has to be modified 
        
        parent = self.getParent()
        keys = parent.getChildKeys()
        
        listIDs = []
        
        for key in keys:
            element = parent.getb(key)
#             attrs = element .getAttrs()
#             if "ID_1" in attrs:
            if element.isAttr("ID_1"):
                id_1 = element.get("ID_1")
                if id_1 != None:
                    listIDs.append(id_1)
                    
        if self.get("ID") in listIDs:
            return set([0])
        else:
            return set([])
       
        
## Meta-Class for all connections of objects from the type PX_Variables

class PX_PlottableConnector(PX_PlotableObject):
    
    def __init__(self, elem0, elem1 = None, listPoints = []):
        
        super(PX_PlottableConnector, self).__init__()
        id_0 = elem0.get("ID")
        self.set("ID_0", id_0)
        self.set("elem0", elem0)
        
        if elem1 != None:
            id_1 = elem1.get("ID")
            self.set("ID_1", id_1)
            self.set("elem1", elem1)
        else:
            self.set("ID_1", None)
            self.set("elem1", None)
            
        
        X = elem0.get("X")
        Y = elem0.get("Y")

#         if id_1 == None:
#             self.set("bLatent", True)
#         else:
#             self.set("bLatent", False)
        
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
        
           
    def __calcDimensions(self):

        elem0 = self.get("elem0")
        elem1 = self.get("elem1")
        self.X0 = elem0.get("X")
        self.Y0 = elem0.get("Y")
        self.X1 = elem1.get("X")
        self.Y1 = elem1.get("Y")
        self.listOutPins0 = elem0.get("listOutPins")
        self.listInPins1  = elem1.get("listInPins")

        self.listPoints = copy.copy(self.get("listPoints"))
       
        self.outPin_x =  self.listOutPins0[0][0]
        self.outPin_y =  self.listOutPins0[0][1]
        self.inPin_x  =  self.listInPins1[0][0]
        self.inPin_y  =  self.listInPins1[0][1]
        #self.delta_x  =  self.outPin_x - self.inPin_x
        #self.delta_y  =  self.outPin_y - self.inPin_y
        
        len_listPoints = len(self.listPoints)
        
        #print "self.listPoints (0): ", self.listPoints

        # determine the shape polygons of the connector
        
        #print "listPoint (0): ", self.listPoints
        
        types = inspect.getmro(type(elem1))
        if PX_PlottableProxyElement in types:
            self.bNoFinalConnection = True
        else:
            self.bNoFinalConnection = False
        
        if self.bNoFinalConnection == False:
        
            if len_listPoints > 0:
                pass
                # x-Values
                if len_listPoints %2==0:
                    self.listPoints[-1] = self.outPin_y + self.Y1 - self.Y0
                # y-Values
                else:
                    if len_listPoints > 1:
                        if self.listPoints[-2] != self.outPin_y:
                            self.listPoints.append(self.inPin_y + self.Y1 - self.Y0)
                    else:
                        if self.Y0 != self.Y1:
                            self.listPoints.append(self.inPin_y + self.Y1 - self.Y0)
                            
            else:
                self.listPoints.append(self.inPin_x + self.X1 - self.X0 - self.rad )
                self.listPoints.append(self.Y1 - self.Y0) 
                            
        else:
            if len_listPoints %2==0:
                self.listPoints.append(self.X1 - self.X0)
            else:
                #print "append"
                self.listPoints.append(self.Y1 - self.Y0)

        
        #print "listPoint (1): ", self.listPoints
        
        len_listPoints = len(self.listPoints)
        len_listPoints_minus_1 = len_listPoints - 1 
        
        if self.bNoFinalConnection == False:
            self.set("listPoints", self.listPoints)
        
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
                y1 = self.inPin_y + self.Y1 - self.Y0
                shape.append(self._PX_PlotableObject__getPolygon(x0,y0,x1,y1))
                #print "x0: ", x0, "y0: ", y0, "x1: ", x1, "y1: ", y1 
        
        #print "Shape: ", shape    
        self.set("Shape",shape )
         

    def get(self, attr):
        
        if attr == "X":
            return self.X0
        elif attr == "Y":
            return self.Y0
        else:
            #return BContainer.BContainer.get(self,attr)
            return PX_PlotableObject.get(self,attr)
        
        
    
    def plot(self, paint, templ):
        
        #print "=============================="
        
        # preparing painting
        
        self.__calcDimensions()
        bActive = self._PX_PlotableObject__isActive()
        path    = QtGui.QPainterPath()
        path.moveTo(self.outPin_x + self.X0, self.outPin_y + self.Y0)

        x1=0
        y1=0
        listPoints = copy.copy(self.listPoints)
 
        
        for i in range(len(listPoints)):

            #x-value
            if i%2==0:
                listPoints[i] = listPoints[i] + self.X0
            #y-value
            else:
                listPoints[i] = listPoints[i] + self.Y0
        
        len_listPoints = len(listPoints)
        
        for i in range(len_listPoints):
            
        
            
            # determining the last, the current and the next point
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
                    #y2 = self.inPin_y + self.Y1
                    y2 = listPoints[i+1]
                # y-Values
                else:
                    #x2 = self.inPin_x + self.X1
                    x2 = listPoints[i + 1]
                    y2 = listPoints[i]  
            #print "-------------------------"              
            #print "x0: ", x0, "y0: ", y0
            #print "x1: ", x1, "y1: ", y1
            #print "x2: ", x2, "y2: ", y2
            
            #print "listPoints[-1]; ", listPoints[-1]
            #print "listPoints[-1] == 0.0: ", listPoints[-1] == 0.0
            #print "i == (len_listPoints - 1) ", i == (len_listPoints - 1) 
            
            if (self.bNoFinalConnection and i == (len_listPoints - 1)) \
                      or  (i == (len_listPoints - 1) and y0 == y2) \
                      or  (i == (len_listPoints - 2) and y0 == y2):
                        #(self.Y0 == self.Y1 and i == (len_listPoints - 1)):
                        
                radOffset = 0
            else:
                radOffset = self.rad    
            
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
                    
        
        #if len_listPoints == 0:
        x2 = self.inPin_x + self.X1
        y2 = self.inPin_y + self.Y1
        if self.bNoFinalConnection == False:
            path.lineTo(x2,y2)  

        pen2 = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_CONNECTOR_highlight(), QtCore.Qt.SolidLine)     
        pen = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_CONNECTOR_line(), QtCore.Qt.SolidLine)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        paint.setBrush(PX_Templ.brush.transparent)
       
        if bActive:
            paint.setPen(pen2)
            paint.drawPath(path) 
        paint.setPen(pen)       
        paint.drawPath(path)   
        
    def isInFocus(self, X, Y):
        
        x = self.get("X")
        y = self.get("Y")

        X = X - x
        Y = Y - y
        
        return PyLinXHelper.point_inside_polygon(X, Y, self.get("Shape"))
    

    def set(self, attr, value):
        
        if attr == "elem1":
            id_1 = value.get("ID")
            BContainer.BContainer.set(self,"elem1", value)
            BContainer.BContainer.set(self,"ID_1", id_1)
        else:
            #BContainer.BContainer.set(self,attr, value)
            PX_PlotableObject.set(self,attr, value)    

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
        #self.pen = 
        
        
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

## Base ckass for operators, which have two inputs by default, but can have more inputs

class PX_PlotableBinOperator(PX_PlotableObject):
    
    def __init__(self):
        self.set("numPins", 2)
        self.set("bInputsChanged", False)
    
    def __calcDimensions(self):
        pass
    
    def plot(self, paint, templ):
        pass
    
    def isInFocus(self, X, Y):
        pass
    
    def isPinInFocus(self, X, Y):
        pass