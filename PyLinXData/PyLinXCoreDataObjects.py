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
import PyLinXGui.PX_Templates as PX_Templ
import PyLinXHelper
import PyLinXCtl


import PyLinXGui


## Meta-Class for all PyLinX data Objects,

class PX_Object(BContainer.BContainer):

    def __init__(self, parent, name, headObject = None):
        
        super(PX_Object, self).__init__( name, headObject =  headObject)
        if parent != None:
            parent.paste(self)
            self.mainController = parent.getRoot(PyLinXCtl.PyLinXMainController.PyLinXMainController)
        else:
            types = inspect.getmro(type(self))
            if PyLinXCtl.PyLinXMainController.PyLinXMainController in types:
                self.mainController = self
            else:
                raise Exception("Error PX_Object.__init__: constructor called without parent")

    
        
    def delete(self, key = None):
        # This is not nice. But usint "__del__" method or using of contexts did it not for me
        
        if key != None:
            obj = self.getb(key)
            if obj.isAttrTrue(u"bExitMethod"):
                obj._exit_()
            #superObj = super(BContainer.BContainer, self)
        BContainer.BContainer.delete(self, key)
         
    def getMaxID(self, _id = 0):
        
        keys = self._BContainer__Body.keys()
        for key in keys:
            element = self._BContainer__Body[key]
            types = inspect.getmro(type(element))
            if PX_IdObject in types:
                element_id = element.ID
                if element_id > _id:
                    _id = element_id
            _id = element.getMaxID(_id)
        return _id
    
    def get(self, attr):
        return super(PX_Object, self).get(attr)
    
    
    def set(self, attr, val, options = None):
        
        super(PX_Object, self).set(attr, val, options)
    

## Classes, which should have an ID should inherit from this class

class PX_IdObject(PX_Object):
    
    __ID = 0

    def __init__(self,parent, name,  bIdSuffix = False, headObject=None):
        self._ID = PX_IdObject.__ID
        
        # some ugly code
        nameWithSuffix = name
        if name == None:
            name = unicode(self._ID)
        if bIdSuffix:
            nameWithSuffix = name + u"_id" + unicode(self._ID)        
        super(PX_IdObject, self).__init__(parent, nameWithSuffix, headObject = headObject)
        
        self._BContainer__Attributes[u"DisplayName"] = name
        
        PX_IdObject.__ID += 1
        self._BContainer__AttributesVirtual.extend([u"ID"])
        
    def get_ID(self):
        return self._ID
    
    def set_ID(self, _id):
        self._ID = _id
        
    ID = property(get_ID, set_ID)
    
    def get(self, attr):
        if attr == "ID":
            return self._ID
        else:
            return super(PX_IdObject, self).get(attr)
        
    def get_ID_from_Phrase(self, phrase, attr = u"Name"):
        try:
            elem_ID = int(phrase)
        except:
            try:
                elem_ID_string = unicode(phrase)
            except:
                raise Exception("Error PX_PlottableConnector.__init__(): Invalid Constructor argument.")
            called = self.mainController.activeFolder.call(attr, elem_ID_string)
            elem_ID = called.ID
        return elem_ID
  

## Meta-Class for all objects that can be plotted in the main drawing area

class PX_PlottableObject (PX_Object):#, QtGui.QGraphicsItem):

    # Constructor  
    
    def __init__(self, parent, name = None, bIdSuffix=False,  *var):
        super(PX_PlottableObject, self).__init__(parent, name, bIdSuffix)
        self.set(u"bVisible", False)  
        self.set(u"bOnlyVisibleInSimMode", False)
        self._BContainer__AttributesVirtual.extend([u"bUnlock"])

    
    
    ## Properties
    ################
            
    def __isActive(self):
        
        parentElement = self.getParent()
        if parentElement  == None:
            return False
        objectsInFocus = self.mainController.selection
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
    
    # Method that plots one hierarchy level
    def __plotHierarchyLevel(self, target, templ):
        paint = QtGui.QPainter()
        paint.begin(target)
        listLatent = []
        for key in self._BContainer__Body:
            element = self._BContainer__Body[key]
            if element.isAttrTrue(u"bVisible"):
                if element.isAttrTrue(u"bLatent"):
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
    
    def get(self, attr):
    
        if attr == u"bUnlock":
            mainController = self.getRoot()
            bSimulationMode = mainController.get(u"bSimulationMode")
            bOnlyVisibleInSimMode = self.get(u"bOnlyVisibleInSimMode")
            return (bOnlyVisibleInSimMode and bSimulationMode) or \
                ( (not bOnlyVisibleInSimMode) and (not bSimulationMode) )
        else:
            return super(PX_PlottableObject, self).get(attr)       
    
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
            if element.isAttrTrue(u"bVisible"): # and element.get("bUnlock"):
                if len(element.isInFocus(X,Y)) > 0:
                    returnVal = [element]
        return returnVal
    
    # method that return the object and it's clicked pinIndex. Convention: negative index: inPin, posiive index: outPin
    def getPinInFocus(self, X, Y):
        keys = self._BContainer__Body
        for key in keys:
            element = self._BContainer__Body[key]
            if element.isAttrTrue(u"bVisible"):
                pass

##  Class to store graphical elements that should not be considered as part of the data. 
##  For Instance the PX_LatentPlottable_HighlightRect

class PX_PlottableLatentGraphicsContainer(PX_PlottableObject):
    
    #def __init__(self, parent, name = "PlottableLatentGraphicsContainer", bIdSuffix = None):
    def __init__(self, parent, name, bIdSuffix = False):
        super(PX_PlottableLatentGraphicsContainer, self).__init__(parent, name, bIdSuffix = bIdSuffix)
        self._BContainer__AttributesVirtual.extend([u"bHasProxyElement"])
        
    def get(self, attr):
        if attr == u"bHasProxyElement":
            for key in self.getChildKeys():
                element = self.getb(key)
                if type(element) == PX_PlottableProxyElement:
                    return True
            return False
        else:
            return super(PX_PlottableLatentGraphicsContainer, self).get(attr)
        
    def set(self, attr, val, options = None):
        if attr == u"bHasProxyElement":
            if val == False:
                keys = self.getChildKeys()
                for key in keys:        
                    element = self.getb(key)
                    types = inspect.getmro(type(element))
                    if PX_PlottableProxyElement in types:
                        self.delete(key)
                        break
            elif val == True:
                    x = self.mainController.get("px_mousePressedAt_x")
                    y = self.mainController.get("px_mousePressedAt_y")
                    PX_PlottableProxyElement(self, x,y )
            else:
                raise Exception("Error: None logical argument PX_PlottableObject.bHasProxyElement")
                      
        else:
            super(PX_PlottableLatentGraphicsContainer, self).set(attr, val, options)

# Meta-Class for all persistent Objects that could be plotted

class PX_PlottableIdObject(PX_PlottableObject, PX_IdObject ):
    
    def __init__(self, parent, name = "<none>", mainController = None, bIdSuffix = False, * args):
        super(PX_PlottableIdObject, self).__init__(parent, name, \
                                                   bIdSuffix=bIdSuffix,  *args)
        

    def delete(self, argsDelete):

        if (type(argsDelete) == unicode) or (type(argsDelete) == str):
            super(PX_PlottableIdObject, self).delete(argsDelete)
            
        if type(argsDelete) == list:    
            # removing the deleted connectors from the list of connected pins of the connected elements
            for _id in argsDelete:
                element = self.getb(unicode(_id))
                types = inspect.getmro(type(element))
                if PX_PlottableConnector in types:
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
                    
            if u"DataDictionary" in self.mainController.getChildKeys():
                DataDictionary = self.mainController.getb(u"DataDictionary")
            else:
                DataDictionary = None
            bDictionary = (DataDictionary != None)
            for element in argsDelete:
                elementObject = self.getb(element)
                Name = elementObject.get(u"Name")
                if bDictionary:
                    if Name in DataDictionary:
                        DataDictionary.pop(Name)
                super(PX_PlottableIdObject, self).delete(Name)

class PX_PlottableGraphicsContainer(PX_PlottableIdObject):
    
    def __init__(self, parent, name = "<none>", mainController = None, * args):
        super(PX_PlottableGraphicsContainer, self).__init__(parent, name = name, mainController = mainController, *args)
        self._BContainer__AttributesVirtual.extend([u"ConnectModInfo"])

        
    def set(self, attr, val, options = None):
        
        if attr == u"ConnectModInfo":
            self.mainController.set(attr, val, options)
        else:
            super(PX_PlottableGraphicsContainer, self).set(attr,val, options)
            
    def get(self,attr):
        
        if attr == u"ConnectModInfo":
            return self.mainController.get(attr)
        else:
            return super(PX_PlottableGraphicsContainer, self).get(attr)  

## Meta-Class for all plotalble objects that can be connected
    
class PX_PlottableElement(PX_PlottableIdObject):

    # some static data structures 
    penBold                   = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
    penBold.setJoinStyle(QtCore.Qt.MiterJoin)
    penBoldGreen              = QtGui.QPen(PX_Templ.color.green,PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
    penBoldGreen.setJoinStyle(QtCore.Qt.MiterJoin)
    penLight                  = QtGui.QPen(PX_Templ.color.black,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
    penLightGreen             = QtGui.QPen(PX_Templ.color.green,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
    penNoBorder               = QtGui.QPen(PX_Templ.color.black,0, QtCore.Qt.SolidLine)
    penTransparent            = QtGui.QPen(QtGui.QColor(0,0,0,0), 0)
    penShadow                 = QtGui.QPen(PX_Templ.color.grayLight, PX_Templ.Template.Gui.px_ELEMENT_Border(), QtCore.Qt.SolidLine)
    penHighlight              = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_ELEMENT_Highlight(), QtCore.Qt.SolidLine)
    penHighlight.setJoinStyle(QtCore.Qt.MiterJoin)
    penSimulationModeBold     = QtGui.QPen(PX_Templ.color.green,PX_Templ.Template.Gui.px_ELEMENT_PinSimulationWidth(), QtCore.Qt.SolidLine)
    penSimulationModeNone     = QtGui.QPen(PX_Templ.color.green,0, QtCore.Qt.SolidLine)
    fontStdVar                = QtGui.QFont(u"FreeSans", PX_Templ.Template.Gui.px_ELEMENT_stdFontSize())
    fontStdVarMetrics         = QtGui.QFontMetrics(fontStdVar)
    fontStdVarDispNum         = QtGui.QFont(u"FreeSans", PX_Templ.Template.Gui.px_ELEMENT_OsciFontSize(), QtGui.QFont.Bold)
    fontStdVarDispNumMetrics  = QtGui.QFontMetrics(fontStdVarDispNum)
    
    def __init__(self,parent,  name, X, Y, value = None, tupleInPins = (), tupleOutPins = (), bIdSuffix = False):
        super(PX_PlottableElement, self).__init__(parent, name, bIdSuffix=bIdSuffix)
        self._X = X
        self._Y = Y
        
        #  Configuration
        self._idxActiveInPins = []
        self._idxActiveOutPins = []
        self._listOutPins = []
        self._listInPins  = []
        
        self.set(u"bMethodIsInFocus", True)
        self.set(u"setIdxConnectedInPins", set([]))
        self.set(u"setIdxConnectedOutPins", set([]))
        self.set(u"bVisible", True)  
        self._BContainer__AttributesVirtual.extend([u"xy"])
        PX_PlottableElement.calcDimensions(self, tupleInPins = tupleInPins, tupleOutPins = tupleOutPins)
        
    ## Properties
    #############
    
    def set_X(self, X, options = None):
        if options == None:
            self._X = X
        else:
            if options == u"-p":
                self._X = self._X + X
        
    def get_X(self):
        return self._X
    
    X = property(get_X, set_X)
    
    def set_Y(self,Y, options = None):
        if options == None:
            self._Y = Y
        else:
            self._Y = self._Y + Y
        
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
    
    def get_bActive(self):
        return self._PX_PlottableObject__isActive()
    
    bActive = property(get_bActive)
    

    def calcDimensions(self,width         = PX_Templ.Template.Gui.px_ELEMENT_minWidth(),\
                              heigth        = PX_Templ.Template.Gui.px_EMELENT_minHeigth(),\
                              tupleInPins   = (),\
                              tupleOutPins  = ()):
        
        self.elementWidth       = width  
        self.elementHeigth      = heigth
        self.border             = PX_Templ.Template.Gui.px_ELEMENT_Border()
        self.halfBorder           = 0.5 * self.border
        pinLength               = PX_Templ.Template.Gui.px_ELEMENT_pinLength() 
        elementWidth_half       = 0.5 * self.elementWidth
        elementHeight_half      = 0.5 * self.elementHeigth

        px_ELEMENT_pinHeigth    = PX_Templ.Template.Gui.px_ELEMENT_pinHeigth()
        self.triangleOffset     = px_ELEMENT_pinHeigth * PX_Templ.Template.Gui.r_60deg()
        self.pinHalfHeigth      = 0.5 * px_ELEMENT_pinHeigth
        lengthWholePin          = self.triangleOffset + pinLength
        rightEndpoint_x         = lengthWholePin  + elementWidth_half
        # left upper corner of the basic rectangular
        self.x                  = self._X - elementWidth_half
        self.y                  = self._Y - elementHeight_half 
        self.x_end              = self.x + self.elementWidth
        self.y_end              = self.y + 0.5 * self.elementHeigth
        
        # Shape
        self.set(u"Shape",[[(self._X - elementWidth_half, self._Y - elementHeight_half ),\
                           (self._X + elementWidth_half, self._Y - elementHeight_half ),\
                           (self._X + elementWidth_half, self._Y + elementHeight_half ),\
                           (self._X - elementWidth_half, self._Y + elementHeight_half ),\
                           ]])
        
        # In- and Outpins
        listInPins   = [(- rightEndpoint_x, inPin[0], - elementWidth_half, inPin[0],  inPin[1])  for inPin  in tupleInPins]
        listOutPins  = [(  rightEndpoint_x, outPin[0],  elementWidth_half, outPin[0], outPin[1]) for outPin in tupleOutPins]       
        ShapeInPins =  [self._PX_PlottableObject__getPolygon(*inPin[0:4])  for inPin  in listInPins]
        ShapeOutPins = [self._PX_PlottableObject__getPolygon(*outPin[0:4]) for outPin in listOutPins]
                
        types = inspect.getmro(type(self))
        
        self._listInPins = listInPins
        self._listOutPins = listOutPins
        self.set(u"ShapeInPins",  ShapeInPins )
        self.set(u"ShapeOutPins", ShapeOutPins )

    
    ## Method to plot the main square of the Element
        
    def plotBasicElement(self, paint, templ, bSimulationMode = False):
    
        
        ## plot the main square of the Element
                
        if self.bActive:
            paint.setPen(PX_PlottableElement.penHighlight)
            paint.setBrush(PX_Templ.brush.Highlight)
            paint.drawRect(self.x,self.y, self.elementWidth, self.elementHeigth)
        else:
            # background shadow
            paint.setPen(PX_PlottableElement.penShadow)
            paint.drawRect(self.x + self.border ,self.y + self.border, self.elementWidth, self.elementHeigth)
            
        # main square
        if bSimulationMode:
            paint.setPen(PX_PlottableElement.penBoldGreen)
        else:
            paint.setPen(PX_PlottableElement.penBold)
        paint.setBrush(PX_Templ.brush.white)
        paint.drawRect(self.x,self.y, self.elementWidth, self.elementHeigth)


        ## plots Connoctor Inputs
    
        listInPins = self.listInPins
        if len(listInPins) > 0:
            paint.setPen(PX_PlottableElement.penNoBorder)
            paint.setBrush(PX_Templ.brush.black)
            paint.setPen(PX_PlottableElement.penNoBorder)
            paint.setBrush(PX_Templ.brush.black)
            idxActiveInPins = self.idxActiveInPins
            
            for i in range(len(listInPins)):
                paint.setPen(self.penNoBorder)
                inPin = listInPins[i]
                path        = QtGui.QPainterPath()
                x_pin       = inPin[0] + self._X
                y_pin       = inPin[1] + self._Y
                x_pinEnd    = inPin[2] + self._X
                x_arrow = x_pinEnd - self.triangleOffset   
    
                path.moveTo(    x_arrow,    y_pin - self.pinHalfHeigth)
                path.lineTo(    x_pinEnd,   inPin[3] + self.Y)
                path.lineTo(    x_arrow,    y_pin + self.pinHalfHeigth)
                path.lineTo(    x_arrow,    y_pin - self.pinHalfHeigth)
                
                paint.drawPath(path)
    
                if -i-1 in idxActiveInPins:
                    paint.setPen(PX_PlottableElement.penBold)
                else:
                    paint.setPen(PX_PlottableElement.penLight)
                paint.drawLine( x_pin,y_pin,x_arrow ,y_pin)                
   
    
        ## plot Connoctor Outputs

        listOutPins = self.listOutPins
        if len(listOutPins) > 0:
            paint.setPen(PX_PlottableElement.penLight)
            paint.setBrush(PX_Templ.brush.white)
            paint.setPen(PX_PlottableElement.penNoBorder)
            paint.setBrush(PX_Templ.brush.white)
            idxActiveOutPins = self.idxActiveOutPins
    
            for i in range(len(listOutPins)):
                paint.setPen(self.penNoBorder)
                outPin = listOutPins[i]
                path        = QtGui.QPainterPath()
                x_pin       = outPin[0] + self._X
                y_pin       = outPin[1] + self._Y
                x_pinEnd    = outPin[2] + self._X + self.halfBorder
                x_arrow = x_pinEnd + self.triangleOffset   
    
                path.moveTo(    x_pinEnd,    y_pin - self.pinHalfHeigth)
                path.lineTo(    x_arrow,     outPin[3] + self.Y)
                path.lineTo(    x_pinEnd,    y_pin + self.pinHalfHeigth)
                path.lineTo(    x_pinEnd,    y_pin - self.pinHalfHeigth)
                
                paint.drawPath(path)
                
                if i in idxActiveOutPins:
                    paint.setPen(PX_PlottableElement.penBold)
                else:
                    paint.setPen(PX_PlottableElement.penLight)
                paint.drawLine( x_pin,y_pin,x_arrow ,y_pin)
            

    # Method which determins if a point is inside the pin of the element 
    
    def isPinInFocus(self, X, Y):
        
        x = self._X
        y = self._Y

        X = X - x
        Y = Y - y  
                
        ShapeInPins  = self.get(u"ShapeInPins")
        ShapeOutPins = self.get(u"ShapeOutPins")
        idxInPins  = PyLinXHelper.point_inside_polygon(X, Y, ShapeInPins) 
        
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
          
        return PyLinXHelper.point_inside_polygon(X, Y, self.get(u"Shape"))

    # Method which sets parameters. Partiallly overwrites the set-Method of the BContainer class
    
    def set(self, attr, val, options = None):
        if attr == u"xy":
            if self.get(u"bUnlock"):
                self.set_X(val[0], options)
                self.set_Y(val[1], options)
        else:
            return super(PX_PlottableElement, self).set(attr, val, options)

    # Method which gets parameters. Partiallly overwrites the set-Method of the BContainer class
    
    def get(self, attr):
        if attr == u"xy":
            return (self.get_X(), self.get_Y())
        else:
            return super(PX_PlottableElement, self).get(attr)


## Proxy class used as place holder of the target object of a connector during drawing the connection

class PX_PlottableProxyElement(PX_PlottableElement):
    
    def __init__(self,parent,  X, Y):#, mainController = None):
        
        super(PX_PlottableProxyElement, self).__init__(parent, u"PX_PlottableProxyElement", X, Y, None)
        self.listInPins = [(0,0,0,0)]
        self.rootGraphics = self.mainController.getb(u"rootGraphics")
    
    def isInFocus(self, X, Y):
        return []


    # Method which sets parameters. Partiallly overwrites the set-Method of the BContainer class
    
    def set(self, attr, val, options = None):
        if attr == "xy":
            self.__set_xy(val)
        else:
            return super(PX_PlottableProxyElement, self).set(attr, val, options)

    def __set_xy(self, val):
        
        x = val[0]
        y = val[1]
        X = 10 * round( 0.1 * float(x))
        Y = 10 * round( 0.1 * float(y))        
        
        ConnectorPloting = self.mainController.get(u"ConnectorPloting")
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
        self.X = x
        self.Y = y

## Class for variable Elements

class  PX_PlottableVarElement(PX_PlottableElement):
    
    def __init__(self,parent, name, X, Y, value = None, mainController = None, refName = None):
        
        if name==None:
            raise Exception(u"Error PX_PlottableVarElement.__init__: Name None not allowed!")
        
        tupleInPins  = ((0,u""),)
        tupleOutPins = ((0,u""),)
        bRefName = (refName == None)
        if bRefName:
            bIdSuffix = True
        else:
            bIdSuffix = False
            displayName = name
            name = refName
        super(PX_PlottableVarElement, self).__init__(parent, name, float(X), float(Y), value = value,\
                            tupleInPins = tupleInPins, tupleOutPins = tupleOutPins, bIdSuffix = bIdSuffix)
        
        if not bRefName:
            self._BContainer__Attributes[u"DisplayName"] = displayName
            
        # Has to be done ACFTER the DisplayName is overwritten. Otherwise the registration 
        # cannot be done correct
        self.__refObject = self.mainController.objectHandler.register(self)            
            
        self.__refObject._BContainer__Head = value 
        self.set(u"tupleInPins", tupleInPins)
        self.set(u"tupleOutPins", tupleOutPins)
        self._BContainer__AttributesVirtual.extend([u"bMeasure"])
        
        
    def calcDimensions(self,bStimulate,bMeasure):
        
        if bStimulate:
            self.x0_stim = self._X + PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x() 
            self.y0_stim = self._Y - 0.5 * PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            x1_offset = PX_Templ.Template.Gui.r_60deg() * PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() 
            self.x1_stim = self.x0_stim - x1_offset 
            self.y1_stim = self._Y - 0.5 * PX_Templ.Template.Gui.px_ELEMENT_MediumLight() - \
                        PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() * PX_Templ.Template.Gui.r_60deg()         
            
            self.x2_stim = self.x0_stim - PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            self.y2_stim = self.y1_stim
            self.x3_stim = self.x2_stim
            self.y3_stim = self._Y - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation()
            self.x4_stim = self.x0_stim + PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            self.y4_stim = self.y3_stim
            self.x5_stim = self.x4_stim
            self.y5_stim = self.y1_stim
            self.x6_stim = self.x0_stim + x1_offset
            self.y6_stim = self.y1_stim
            
            self.set(u"Shape_stim", [[(self.x0_stim,self.y0_stim),\
                                     (self.x1_stim,self.y1_stim),\
                                     (self.x2_stim,self.y2_stim),\
                                     (self.x3_stim,self.y3_stim),\
                                     (self.x4_stim,self.y4_stim),\
                                     (self.x5_stim,self.y5_stim),\
                                     (self.x6_stim,self.y6_stim),\
                                     ]])
        else:
            self.set(u"Shape_stim", [])
        
        if bMeasure:
            self.x0_meas = self._X - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_x() 
            self.y0_meas = self._Y - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation() - 0.5 * PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            x1_offset = PX_Templ.Template.Gui.r_60deg() * PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() 
            self.x1_meas = self.x0_meas - x1_offset 
            self.y1_meas = self._Y - 0.5 * PX_Templ.Template.Gui.px_ELEMENT_MediumLight() - PX_Templ.Template.Gui.px_ELEMENT_PinSimulation() + \
                         PX_Templ.Template.Gui.px_ELEMENT_PinSimulation_Arrow() * PX_Templ.Template.Gui.r_60deg() 
            self.x2_meas = self.x0_meas - PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            self.y2_meas = self.y1_meas
            self.x3_meas = self.x2_meas
            self.y3_meas = self._Y - 0.5 * PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            self.x4_meas = self.x0_meas + PX_Templ.Template.Gui.px_ELEMENT_MediumLight()
            self.y4_meas = self.y3_meas
            self.x5_meas = self.x4_meas
            self.y5_meas = self.y1_meas
            self.x6_meas = self.x0_meas + x1_offset
            self.y6_meas = self.y1_meas 
        
            self.set(u"Shape_meas", [[(self.x0_meas,self.y0_meas),\
                                     (self.x1_meas,self.y1_meas),\
                                     (self.x2_meas,self.y2_meas),\
                                     (self.x3_meas,self.y3_meas),\
                                     (self.x4_meas,self.y4_meas),\
                                     (self.x5_meas,self.y5_meas),\
                                     (self.x6_meas,self.y6_meas),\
                                     ]])
            
        else:
            self.set(u"Shape_meas", [])       
                               
    def plot(self, paint, templ):

        ## Method to plot the color bar of a variable element
        
        def __plotElementSpecifier():
            
            # color bar 
            paint.setPen(PX_PlottableElement.penLight)
            paint.setBrush(PX_Templ.brush.blueLocalVar)
            paint.drawRect(self.x + self.halfBorder,\
                           self.y + self.halfBorder,\
                           PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar(),\
                           PX_Templ.Template.Gui.px_EMELENT_minHeigth() - self.halfBorder)
            posText_x = self.x + PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar() + whiteSpace
            posText_y = self.y + 0.5 * (PX_PlottableElement.fontStdVarMetrics.ascent() + PX_Templ.Template.Gui.px_EMELENT_minHeigth()) 
            paint.drawText(posText_x, posText_y, name)

            
        def __drawStimulationPoint():
            
            #paint.setPen(PX_PlottableElement.penSimulationModeBold)
            paint.setBrush(PX_Templ.brush.green)                        
            paint.setPen(PX_PlottableElement.penSimulationModeNone)

            path = QtGui.QPainterPath()
            path.moveTo(self.x0_stim,self.y0_stim)
            path.lineTo(self.x1_stim,self.y1_stim) 
            path.lineTo(self.x2_stim,self.y2_stim)
            path.lineTo(self.x3_stim,self.y3_stim)
            path.lineTo(self.x4_stim,self.y4_stim)
            path.lineTo(self.x5_stim,self.y5_stim)
            path.lineTo(self.x6_stim,self.y6_stim)
            path.lineTo(self.x0_stim,self.y0_stim)
            paint.drawPath(path)     


        def __drawMeasurePoint():
            
            paint.setBrush(PX_Templ.brush.green)         
            paint.setPen(PX_PlottableElement.penSimulationModeNone)

            path = QtGui.QPainterPath()
            path.moveTo(self.x0_meas,self.y0_meas)
            path.lineTo(self.x1_meas,self.y1_meas)
            path.lineTo(self.x2_meas,self.y2_meas)            
            path.lineTo(self.x3_meas,self.y3_meas)
            path.lineTo(self.x4_meas,self.y4_meas)
            path.lineTo(self.x5_meas,self.y5_meas)
            path.lineTo(self.x6_meas,self.y6_meas)
            path.lineTo(self.x0_meas,self.y0_meas)
            paint.drawPath(path)
            
            listSelectedDispObj = self.get(u"listSelectedDispObj")
            strSelectedDispObj = ""
            for listItem in listSelectedDispObj:
                if strSelectedDispObj != "":
                    strSelectedDispObj += ","
                strSelectedDispObj += str(listItem)
            
            paint.setFont(PX_PlottableElement.fontStdVar)
            width = PX_PlottableElement.fontStdVarMetrics.width(strSelectedDispObj)
            paint.drawText(self.x0_meas - 0.65 * width , \
                           self.y0_meas - + PX_Templ.Template.Gui.px_ELEMENT_MediumLight() , \
                           strSelectedDispObj)
              
        def __drawValue(name):
            
            DataDictionary = self.mainController.getb(u"DataDictionary")
            #print "name: ", name
            #print "DataDictionary", DataDictionary 
            #print "id(self.mainController.getb(u\"DataDictionary\")) (2)", id(self.mainController.getb(u"DataDictionary"))
            if name in DataDictionary:
                value = DataDictionary[name]
            else:
                value = 0.
            strValue = str(value)
            widthValue  = 1.5 * PX_PlottableElement.fontStdVarMetrics.width(QtCore.QString(strValue))
            posText_x = self.X - 0.5 * widthValue 
            posText_y = self.Y - 13
            paint.setBrush(PX_Templ.brush.HighlightTransp)
            paint.setPen(PX_PlottableElement.penTransparent)
            boundingRect = PX_PlottableElement.fontStdVarMetrics.boundingRect(strValue)
            paint.drawRect(posText_x, posText_y-boundingRect.height(), 1.5 * boundingRect.width(),boundingRect.height() )
            paint.setBrush(PX_Templ.brush.green)
            paint.setPen(PX_PlottableElement.penSimulationModeNone)
            paint.drawText(posText_x, posText_y, strValue)
            
        paint.setFont(PX_PlottableElement.fontStdVar)
        name = self.get(u"DisplayName")
        widthName  = PX_PlottableElement.fontStdVarMetrics.width(name)
        whiteSpace = PX_Templ.Template.Gui.px_ELEMENT_whiteSpace()
        width_raw = PX_Templ.Template.Gui.px_ELEMENT_minWidthColorBar() + 2 *  whiteSpace  + 4 *  self.border + widthName 
        # round!
        width  = 20 * math.ceil(0.05 * float(width_raw) )
        heigth = PX_Templ.Template.Gui.px_EMELENT_minHeigth()
        
        tupleInPins = self.get(u"tupleInPins")
        tupleOutPins = self.get(u"tupleOutPins")        
        
        PX_PlottableElement.calcDimensions(self,width, heigth, tupleInPins = tupleInPins, tupleOutPins = tupleOutPins)
        PX_PlottableElement.plotBasicElement(self, paint, templ)
        __plotElementSpecifier()
        
        mainController = self.getRoot()
        bSimulationMode = mainController.get(u"bSimulationMode")
         
        if bSimulationMode:

            bStimulate = self.__refObject.get(u"bStimulate")
            bMeasure = self.__refObject.get(u"bMeasure")
            self.calcDimensions(bStimulate,bMeasure)
            
            name = self.get(u"DisplayName")
            __drawValue(name)
            if bStimulate:
                __drawStimulationPoint()
            if bMeasure:
                __drawMeasurePoint()
                
    def get(self,attr):
        
        if attr in (u"bStimulate",u"bMeasure",u"StimulationFunction",u"listSelectedDispObj", u"objPath"):
            return self.__refObject.get(attr)
        else:
            return super(PX_PlottableVarElement, self).get(attr)
        
    def set(self, attr, val, options = None):
        
        if attr in (u"bStimulate",u"StimulationFunction",u"listSelectedDispObj"):
            return self.__refObject.set(attr, val, options = None)
        else:
            return super(PX_PlottableVarElement, self).set(attr, val, options = options)
        
    def updateDataDictionary(self):
        self.__refObject.updateDataDictionary()
        
    def getRefObject(self):
        return self.__refObject
            

## Class for variable viewer object

class PX_PlottableVarDispElement(PX_PlottableElement):
    
    def __init__(self, parent, X, Y):
        
        def __getIdxDataDispObj(listDataDispObj):
            listDataDispObj.sort()
            i = 1               
            for j in listDataDispObj:
                if j > i:
                    listDataDispObj.append(i)
                    return i
                i += 1
            listDataDispObj.append(i)
            return i
                
        mainController = parent.getRoot()
        self.mainController = mainController
        listDataDispObj = mainController.get(u"listDataDispObj")
        
        idx = __getIdxDataDispObj(listDataDispObj)
        super(PX_PlottableVarDispElement, self).__init__(parent, u"VarDispElement", \
                                                         float(X), float(Y), bIdSuffix = True)
        self.set(u"setVars", set([]))
        self.set(u"idxDataDispObj", idx)
        self.set(u"bOnlyVisibleInSimMode", True)
        self.set(u"bExitMethod", True)
                            
        self.__widget = PyLinXGui.PX_DataViewerGui.DataViewerGui(self,self.get(u"idxDataDispObj"), mainController = self.mainController)
        self.__widgetGeometry = self.__widget.geometry() 
        self.__widgetPos      = self.__widget.pos()
        
        self.set(u"bVarDispVisible", False)
        
        super(PX_PlottableVarDispElement, self).calcDimensions(width = PX_Templ.Template.Gui.px_DispVarObjSize(),\
                                          heigth = PX_Templ.Template.Gui.px_DispVarObjSize())
   
    def _exit_(self):

        def delFromListSelectedDispObj(element,idx):
            keys = element.getChildKeys()
            listSelectedDispObj = element.get(u"listSelectedDispObj")
            if listSelectedDispObj != None:
                newLlistSelectedDispObj = [x for x in listSelectedDispObj if x != idx]
                element.set(u"listSelectedDispObj", newLlistSelectedDispObj)    
            for key in keys:
                elementChild = element.getb(key)
                delFromListSelectedDispObj(elementChild, idx)

        self.idx = self.get(u"idxDataDispObj")
        mainController = self.getRoot()
        listDataDispObj = mainController.get(u"listDataDispObj")
        newListDataDispObj = [x for x in listDataDispObj if x != self.idx]
        mainController.set(u"listDataDispObj", newListDataDispObj)    
        
        rootGraphics = mainController.getb(u"rootGraphics")
        delFromListSelectedDispObj(rootGraphics, self.idx)

        
        
        
    def get(self, attr):
        
        if attr == u"bVisible":
            mainController = self.getRoot()
            return mainController.get(u"bSimulationMode")
        else:
            return super(PX_PlottableVarDispElement, self).get(attr)
        
    def labelAdd(self, label, listIdx = []):
        idx = self.get(u"idxDataDispObj")
        if idx in listIdx:
            setVars = self.get(u"setVars")
            setVars.add(label)
            self.set(u"setVars",setVars)

        
    def labelRemove(self, label, listIdx = []):
        idx = self.get(u"idxDataDispObj")
        if idx in listIdx:
            setVars = self.get(u"setVars")
            if label in setVars:
                setVars.remove(label)
                self.set(u"setVars", setVars)

    
    def plot(self, paint, templ):
        
        mainController = self.getRoot()
        bSimulationMode = mainController.get(u"bSimulationMode")
        if not bSimulationMode:
            return
        
        paint.setFont(PX_PlottableElement.fontStdVarDispNum)
        idx = self.get(u"idxDataDispObj")
        strIdx = str(idx)
        widthStrIdx =  PX_PlottableElement.fontStdVarDispNumMetrics.width(strIdx)
        dim_xy = PX_Templ.Template.Gui.px_DispVarObjSize()
        PX_PlottableElement.calcDimensions(self,dim_xy, dim_xy)
        
        # Draw Basic Element
        PX_PlottableElement.plotBasicElement(self, paint, templ, True)
        
        # Draw Specifier
        paint.setPen(PX_PlottableElement.penLightGreen)
        rectangle = QtCore.QRectF(self.x + 5,self.y + 5, self.elementWidth - 10, self.elementHeigth - 15)
        paint.drawRoundedRect(rectangle, 5.0, 5.0)
        paint.drawText( self.x + 0.5 *  ( self.elementWidth - 1.2 *widthStrIdx ), \
                        self.y + 0.62 *   self.elementHeigth                 \
                        , strIdx)
        
    def set(self, attr, value, options = None):
        
        if attr == u"bVarDispVisible":
            if self.__widget == None:
                if  value == True:
                    self.__widget.show()
                    return super(PX_PlottableVarDispElement, self).set(attr, True, options)
                elif value == False:
                    return
            else:
                if value in (True, False):
                    if value == True:
                        self.__widget.show()
                    elif value == False:
                        self.__widget.hide()

        return super(PX_PlottableVarDispElement, self).set(attr, value, options)

    def stop_run(self):
        self.__widget.stop_run()

    def sync(self):
        self.__widget.updateValues()

    def widgetShow(self):
        bVarDispVisible = self.get(u"bVarDispVisible")
        if bVarDispVisible:
            self.__widget.setGeometry(self.__widgetGeometry)
            self.__widget.move(self.__widgetPos)
            self.__widget.show()
            
    
    def widgetHide(self):
        self.__widgetGeometry = self.__widget.geometry()
        self.__widgetPos = self.__widget.pos() 
        self.__widget.hide()
        
## Class for binary Operators
    
class PX_PlottableBasicOperator(PX_PlottableElement):
    
    penSpecifier   = QtGui.QPen(PX_Templ.color.blue,PX_Templ.Template.Gui.px_ELEMENT_MediumLight(), QtCore.Qt.SolidLine)
    brushSpecifier = QtGui.QBrush(PX_Templ.color.blueTransp)
    dictSyllabes   = {u"+": "plus", u"-": "minus", u"*": "mult", u"/": "div"} 
    
    def __init__(self,parent, value,  X, Y, name = None):
        n = PX_IdObject._PX_IdObject__ID + 1
        if name == None:
            name = u"Operator_" + PX_PlottableBasicOperator.dictSyllabes[value] + u"_id" + str(n)
        elif name[1:12] ==  u"Operator_id":
            raise Exception(u"Error PyLinXCoreDataObjects.PX_PlottableBasicOperator.__init__: Name of Object might not be unique!")
        stdPinDistance =  PX_Templ.Template.Gui.px_ELEMENT_stdPinDistance()
        stdPinDistance_half = 0.5 * stdPinDistance 
        tupleInPins  = ((-stdPinDistance_half, u""), (stdPinDistance_half, u""))
        tupleOutPins = ((0,u""),)
        super(PX_PlottableBasicOperator, self).__init__(parent, name, float(X), float(Y), \
                                            tupleInPins  = tupleInPins,\
                                            tupleOutPins = tupleOutPins)
        self.set(u"tupleInPins", tupleInPins)
        self.set(u"tupleOutPins", tupleOutPins)
        self._BContainer__Head = value
        PX_PlottableElement.calcDimensions(self, tupleInPins  = tupleInPins,tupleOutPins = tupleOutPins)
        
    def plot(self,paint,templ):
        
        def __plotPlusSpecifier():
            
            paint.setPen(PX_PlottableBasicOperator.penSpecifier)
            paint.setBrush(PX_PlottableBasicOperator.brushSpecifier)
            
            innerDiam = PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_innerDiameter()
            outerDiam = PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_outerDiameter()
            
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


            #plotting the "-" 
            
        def __plotMinusSpecifier():

            paint.setPen(PX_PlottableBasicOperator.penSpecifier)
            paint.setBrush(PX_PlottableBasicOperator.brushSpecifier)

            innerDiam = PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_innerDiameter()
            outerDiam = PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_outerDiameter()
            
            path = QtGui.QPainterPath()
            path.moveTo( self._X + 0.8 * outerDiam, self._Y + innerDiam)
            path.lineTo( self._X - 0.8 * outerDiam, self._Y + innerDiam)
            path.lineTo( self._X - 0.8 * outerDiam, self._Y - innerDiam)
            path.lineTo( self._X + 0.8 * outerDiam, self._Y - innerDiam) 
            path.lineTo( self._X + 0.8 * outerDiam, self._Y + innerDiam)
            paint.drawPath(path)     


        def __plotMultiplicationSpecifier():

            paint.setPen(PX_PlottableBasicOperator.penSpecifier)
            paint.setBrush(PX_PlottableBasicOperator.brushSpecifier)

            innerDiam = 1.4 * PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_innerDiameter()
            outerDiam = 0.9 * PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_outerDiameter()
            
            #plotting the "x" 
            path = QtGui.QPainterPath()
            path.moveTo( self._X + innerDiam,              self._Y                        )
            path.lineTo( self._X + outerDiam,              self._Y + outerDiam - innerDiam)
            path.lineTo( self._X + outerDiam,              self._Y + outerDiam            )
            path.lineTo( self._X + outerDiam - innerDiam , self._Y + outerDiam            )

            path.lineTo( self._X            ,              self._Y + innerDiam            )
            path.lineTo( self._X - outerDiam + innerDiam , self._Y + outerDiam            )
            path.lineTo( self._X - outerDiam,              self._Y + outerDiam            )
            path.lineTo( self._X - outerDiam,              self._Y + outerDiam - innerDiam)

            path.lineTo( self._X - innerDiam,              self._Y                        )
            path.lineTo( self._X - outerDiam,              self._Y - outerDiam + innerDiam)
            path.lineTo( self._X - outerDiam,              self._Y - outerDiam            )
            path.lineTo( self._X - outerDiam + innerDiam , self._Y - outerDiam            )

            path.lineTo( self._X            ,              self._Y - innerDiam            )
            path.lineTo( self._X + outerDiam - innerDiam , self._Y - outerDiam            )
            path.lineTo( self._X + outerDiam,              self._Y - outerDiam            )
            path.lineTo( self._X + outerDiam,              self._Y - outerDiam + innerDiam)

            path.lineTo( self._X + innerDiam,              self._Y                        )
            paint.drawPath(path)     
        
        def __plotDivisionSpecifier():
            
            paint.setPen(PX_PlottableBasicOperator.penSpecifier)
            paint.setBrush(PX_PlottableBasicOperator.brushSpecifier)

            innerDiam = 1.4 * PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_innerDiameter()
            outerDiam = 0.9 * PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_outerDiameter()
            
            #plotting the "/" 

            path = QtGui.QPainterPath()
            path.moveTo( self._X            ,              self._Y + innerDiam            )
            path.lineTo( self._X - outerDiam + innerDiam , self._Y + outerDiam            )
            path.lineTo( self._X - outerDiam,              self._Y + outerDiam            )
            path.lineTo( self._X - outerDiam,              self._Y + outerDiam - innerDiam)
 
            path.lineTo( self._X            ,              self._Y - innerDiam            )
            path.lineTo( self._X + outerDiam - innerDiam , self._Y - outerDiam            )
            path.lineTo( self._X + outerDiam,              self._Y - outerDiam            )
            path.lineTo( self._X + outerDiam,              self._Y - outerDiam + innerDiam)
 
            path.lineTo( self._X            ,              self._Y + innerDiam            )
             
            paint.drawPath(path)
            
            paint.drawEllipse(self._X + outerDiam - 2 * innerDiam,self._Y + outerDiam - 2 * innerDiam,2 * innerDiam, 2 * innerDiam )
            paint.drawEllipse(self._X - outerDiam,              self._Y - outerDiam ,2 * innerDiam, 2 * innerDiam )
            
            
            
        size = PX_Templ.Template.Gui.px_PlottableELEMOPERATOR_size()
        
        tupleInPins = self.get(u"tupleInPins")
        tupleOutPins = self.get(u"tupleOutPins")
        
        PX_PlottableElement.calcDimensions(self, size, size,tupleInPins = tupleInPins, tupleOutPins = tupleOutPins)
        PX_PlottableElement.plotBasicElement(self, paint, templ)
        
        if self._BContainer__Head == u"+":
            __plotPlusSpecifier()
        elif self._BContainer__Head == u"-":
            __plotMinusSpecifier()
        elif self._BContainer__Head == u"*":
            __plotMultiplicationSpecifier()
        elif self._BContainer__Head == u"/":
            __plotDivisionSpecifier()
        
        
## Meta-Class for all connections of objects from the type PX_Variables

class PX_PlottableConnector(PX_PlottableIdObject):
    
    def __init__(self, parent, \
                 elem0_ID_phrase, \
                 elem1_ID_phrase = None, \
                 listPoints = [], \
                 idxOutPin = 0, idxInPin = -1,\
                 mainController = None,\
                 idxOutPinConnectorPloting = None):
        
        super(PX_PlottableConnector, self).__init__(parent, mainController, bIdSuffix = True)
        
        
        #elem0_ID may also be a string of the element
        elem0_ID = self.get_ID_from_Phrase(elem0_ID_phrase)
          
        self.set(u"idxOutPinConnectorPloting", idxOutPinConnectorPloting)
        self.set(u"ID_0", elem0_ID)

        self._elem0 = self.mainController.activeFolder.call(u"ID", elem0_ID)
        self.set(u"bVisible", True)
        self._idxOutPin = idxOutPin
        self._idxInPin = idxInPin
        
        bElem1Connected = (elem1_ID_phrase != None)
        if bElem1Connected:
            elem1_ID = self.get_ID_from_Phrase(elem1_ID_phrase)
            self.set(u"ID_1", elem1_ID)
            elem1 = parent.call(u"ID", elem1_ID)
            if elem1 == None:
                raise Exception("Error!")
            self._elem1 = elem1 
            
        else:
            self.mainController.set(u"bConnectorPloting", True)
            self.mainController.set(u"ConnectorPloting", self)
            self.getParent().set(u"bHasProxyElement", True)
            proxyElement = self.mainController.latentGraphics.getb(u"PX_PlottableProxyElement")
            self._elem1 = proxyElement
            
        # list points saves for odd indices x-values and for even indices y-values of the corresponding corners of the connector
#         for i in range(len(listPoints)):
#             #x-value
#             if i%2==0:
#                 listPoints[i] = listPoints[i] - X 
#             #y-value
#             else:
#                 listPoints[i] = listPoints[i] - Y       
        self.set(u"listPoints", listPoints)
        
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
        try: 
            return self._elem1
        except:
            print "Error!"
    
    def set_elem1(self, elem1):
        id_1 = elem1.ID
        self._elem1 = elem1
        BContainer.BContainer.set(self,u"ID_1", id_1)
        
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
        
        self.listPoints = list(self.get(u"listPoints"))
                
        idxOutPin = self.idxOutPin
        idxInPin = self.idxInPin
        
        len_listPoints = len(self.listPoints)
           
        self.outPin_x =  self.listOutPins0[ idxOutPin ][0]
        self.outPin_y =  self.listOutPins0[ idxOutPin ][1] 
   
        idxInPin_transformed =  - idxInPin - 1 
        self.inPin_x  =  self.listInPins1 [ idxInPin_transformed  ][0]
        self.inPin_y  =  self.listInPins1 [ idxInPin_transformed  ][1]

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
            self.set(u"listPoints", self.listPoints)
        
        # Determining the shape of the connector
        # From the "Shape" the GUI knows where an object
        # is located. The "Shape" has not be the real 
        # visible shape of the graphical object.
        # the "Shape" of the connector is composed by
        # six point polygones and is  broader than the
        # visible shape for convenience reasons
        ##############################################
        
        shape = []
        
        x1_cache = self.X0
        y1_cache = self.Y0
        
        
        for i in range(0, len_listPoints):

            x0 = x1_cache
            y0 = y1_cache
            if i%2 == 0:
                x1 = self.listPoints[i] + self.X0
                y1 = y1_cache
            else:
                x1 = x1_cache
                y1 = self.listPoints[i] + self.Y0
            shape.append(self._PX_PlottableObject__getPolygon(x0,y0,x1,y1))
            x1_cache = x1
            y1_cache = y1
            if i == len_listPoints_minus_1:
                x0 = x1_cache
                y0 = y1_cache
                x1 = self.inPin_x + self.X1 #- self.X0
                #y1 = self.inPin_y + self.Y1 - self.Y0 
                y1 = self.inPin_y + self.Y1 #- self.Y0 
                shape.append(self._PX_PlottableObject__getPolygon(x0,y0,x1,y1))

        self.set(u"Shape",shape )

    def isInFocus(self, X, Y):
        
        return PyLinXHelper.point_inside_polygon(X, Y, self.get(u"Shape"))
  
    def plot(self, paint, templ):
        
        # preparing plotting
        ####################
        
        self.__calcDimensions()
        bActive = self._PX_PlottableObject__isActive()
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
        

    def set(self, attr, val, options = None):
        
        if attr == u"connectInfo":
            self.mainController.latentGraphics.set(u"bHasProxyElement", False)
            objInFocus = self.mainController.activeFolder.getb(val[0])
            idxInPin = val[1]
            setIdxConnectedInPins = objInFocus.get(u"setIdxConnectedInPins")
            self.elem1 = objInFocus
            self.idxInPin = idxInPin
            setIdxConnectedInPins.add(idxInPin)
            objInFocus.set(u"setIdxConnectedInPins", setIdxConnectedInPins)
            objInFocus.idxActiveInPins = []
            setIdxConnectedOutPins = self.elem0.get(u"setIdxConnectedOutPins")
            idxOutPinConnectorPloting = self.get(u"idxOutPinConnectorPloting")
            setIdxConnectedOutPins.add(idxOutPinConnectorPloting)
            self.elem0.set(u"setIdxConnectedOutPins", setIdxConnectedOutPins)
            self.mv(u"/latentGraphics/"+self.get(u"Name")+u"/", self.mainController.activeFolder)
            self.set(u"idxOutPinConnectorPloting", None, options)       
            self.mainController.set(u"bConnectorPloting", False, options)
            
        else:
            super(PX_PlottableConnector, self).set(attr, val, options)    
    
    def get(self,attr):
        
        if attr == u"connectInfo":
            return (self.elem1.get("Name"), self.idxInPin)
        else:
            return super(PX_PlottableConnector, self).get(attr) 
    
## Class for highlightning
            
class PX_LatentPlottable_HighlightRect(PX_PlottableObject):
    
    def __init__(self, parent, X, Y, bIdSuffix=None):
        
        super(PX_LatentPlottable_HighlightRect, self).__init__(parent, u"HighlightObject", bIdSuffix = bIdSuffix)
        self.set(u"bLatent", True)
        self.set(u"X0", X)
        self.set(u"Y0", Y)
        self.set(u"X1", X)
        self.set(u"Y1", Y)
        self.set(u"Name", u"HighlightObject")
        self.set(u"bVisible", True)
        self.set(u"bExitMethod", True)

        
        
    def plot(self, paint, templ):
        
        X0 = self.get(u"X0")
        Y0 = self.get(u"Y0")
        X1 = self.get(u"X1")
        Y1 = self.get(u"Y1")
        
        pen = QtGui.QPen(PX_Templ.color.Highlight,PX_Templ.Template.Gui.px_HIGHLIGHT_border(), QtCore.Qt.SolidLine)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        paint.setPen(pen)
        paint.setBrush(PX_Templ.brush.HighlightTransp)
        paint.drawRect(X0, Y0, X1-X0, Y1-Y0)
        
        
    def isInFocus(self, X, Y):
        return []
    
    def _exit_(self):
        
        X = self.get(u"X1")
        Y = self.get(u"Y1")
        px_mousePressedAt_X = self.mainController.get(u"px_mousePressedAt_X")
        px_mousePressedAt_Y = self.mainController.get(u"px_mousePressedAt_Y")
        activeGraphics = self.mainController.activeFolder
        if px_mousePressedAt_X != sys.maxint and px_mousePressedAt_Y != sys.maxint: 
            polygons = [[(X,Y), (X,px_mousePressedAt_Y ), (px_mousePressedAt_X,px_mousePressedAt_Y),(px_mousePressedAt_X,Y)]]
            keys = activeGraphics.getChildKeys()
            objInFocusTemp = []
            keysObjInFocus = []
            for key in keys:            
                element = activeGraphics.getb(key)                               
                if element.isAttr(u"Shape"):
                    bFocus = True
                    shape = element.get(u"Shape")
                    for polygon in shape:
                        if polygon != None:
                            for point in polygon:
                                idxCorner = PyLinXHelper.point_inside_polygon(point[0], point[1],polygons)
                                if len(idxCorner) == 0:
                                    bFocus = False
                    if bFocus: 
                        if element.get(u"bUnlock"):
                            objInFocusTemp.append(element)
                            keysObjInFocus.append(key)
            Selection_listKeys = self.mainController.get(u"Selection_listKeys")
            if set(keysObjInFocus) != set(Selection_listKeys):
                ustrExecCommand = u"select " + u" ".join([unicode(key) for key in keysObjInFocus])
                self.mainController.execCommand(ustrExecCommand)
