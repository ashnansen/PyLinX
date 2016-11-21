'''
Created on 13.11.2014

@author: wplaum
'''

from   PyQt4 import QtGui
import inspect
import string
import os


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
    


def showFileSelectionDialog(ui, strPath = None, bDir = False, strExt= u"", strHeader = None, \
                              dialogType = u"load", bFileObject = True):
    # ui          widget from which the dialog is called
    # strPath     path to the directory shown when dialog is opened
    # strExt      An expression like "*.doc" to restrict the display to special file endings
    # strHeader   header of the dialog
    # dialogTyoe  "load" for load dialogs and "save for save dialogs
    # bFileObject if true the function returns the file object if false only the string of the path is returned
    
    if strPath == None:
        strPath = os.getcwd()
    if strHeader == None:
        if bDir:
            strHeader = u"Select Directory..."
        else:
            strHeader = u"Select File..."
    if bDir:
        strExt = strPath,QtGui.QFileDialog.ShowDirsOnly
    if dialogType == u"save":            
        strSavePath = unicode(QtGui.QFileDialog.getSaveFileName(ui,strHeader,strPath,strExt))
    elif dialogType == u"load":
        strSavePath = unicode(QtGui.QFileDialog.getOpenFileName(ui,strHeader,strPath,strExt))
    else:
        strSavePath = u""
    
    if len(strSavePath):
        try:
            if bFileObject:
                _file = open(strSavePath)
                return _file, strSavePath
            else:
                return strSavePath
        except:
            error(u"Error opening " + strSavePath)
            return None
    else:
            return None
        
def loadAction(widget= None, \
               IconPath = u"", \
               ToolTip = u"", \
               ShortCut = u"", \
               Callback = None, \
               ToolBar = None, \
               checkable = False):     

    action = QtGui.QAction(QtGui.QIcon(IconPath), ToolTip, widget)
    action.setShortcut(ShortCut)
    action.setCheckable(checkable)
    action.triggered.connect(Callback)
    ToolBar.addAction(action)
    return action

# Low level method to do a proper split. String phrases like "test text" may contain white space but should result in one 
# list entry
def split(command):
    command.strip()
    commandList = []
    word = u""
    bStringPhrase = False
    letterOld = None
    for letter in command:
        if letter == "\"":
            word += letter
            if not bStringPhrase:
                if letterOld in (u" ", None):
                    bStringPhrase = True
            else:
                commandList.append(word)
                word = u""
                bStringPhrase = False
                continue
        else:
            if not bStringPhrase:
                if letter != u" ":
                    word += letter
            else:
                word += letter
                continue
        if letter == u" " and word != u"":
            commandList.append(word)
            word = u""
        letterOld = letter
    if word != u"":
        commandList.append(word)
    return commandList