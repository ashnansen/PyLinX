'''
Created on 13.11.2014

@author: wplaum
'''

from   PyQt4 import QtGui
import inspect
import string


class ToolSelected():
    none                = 0
    newVarElement       = 1
    newPlus             = 2
    newMinus            = 3
    newMultiplication   = 4
    newDivision         = 5
    max                 = newDivision
    
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs. This function was taken from 
# http://www.ariel.com.au/a/python-point-int-poly.html
# and does not fall under the terms of licence of PyLinXSS

def point_inside_polygon(x,y,polygons):
    
    idxPolygons = []
    
    if polygons != None:
        for l in range(len(polygons)):
            inside = False
            poly = polygons[l]
            #print "poly: ",  poly
            if poly != None:
                n = len(poly)
                p1x,p1y = poly[0]
                for i in range(n+1):
                    p2x,p2y = poly[i % n]
                    if y > min(p1y,p2y):
                        if y <= max(p1y,p2y):
                            if x <= max(p1x,p2x):
                                if p1y != p2y:
                                    xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                                if p1x == p2x or x <= xinters:
                                    inside = not inside
                    p1x,p1y = p2x,p2y
                if inside == True:
                    idxPolygons.append(l)
            
    return idxPolygons

def error(strErrorMessage):
    msgBox = QtGui.QMessageBox()
    msgBox.setIcon(QtGui.QMessageBox.Critical)
    msgBox.setText(strErrorMessage)
    msgBox.addButton(QtGui.QPushButton('OK'), QtGui.QMessageBox.YesRole)
    msgBox.setWindowTitle("Error")
    msgBox.exec_()
    
def checkType(obj, _type):
    types = inspect.getmro(type(obj))
    return _type in types

def getAttributeAndValue(stri):
    listStri = string.split(stri)
    if len(listStri) == 0:
        return None
    else:
        return listStri[0], listStri[2]