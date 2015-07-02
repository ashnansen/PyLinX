'''
Created on 12.12.2014

@author: Waetzold Plaum
'''
from PyQt4 import QtGui, QtCore
import numpy as np
from PyLinXCodeGen import PyLinXRunEngine

class DataViewerGui(QtGui.QDialog):

    def __init__(self, varDispObj, idx = 0, t_max = 1.,  mainGui = None):
    
        super(DataViewerGui, self).__init__()
        
        global DataDictionary
        
        self.varDispObj = varDispObj
        self.listVars = list(self.varDispObj.get(u"setVars"))
         
        self.idx = idx
        
        size_x = 400
        size_y = 200
        self.numXPints = 201
    
        self.paint = QtGui.QPainter()
        self.t_max = t_max
        self.pen   = QtGui.QPen(QtGui.QColor(0,0,0),1, QtCore.Qt.SolidLine)
        self.t     = np.array([0.1*i for i in range(201)])
        self.y     = {}
        if self.listVars != None:
            for var in self.listVars:
                self.y[var]=np.array(np.zeros(self.numXPints , np.float) ) 
        self.resize(size_x,size_y)
        self.fac_t = 360 / max(self.t)
        self.fac_y = 160 / 2
        
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle("Data-Viewer " + str(self.idx))

    def update(self):
        self.listVars = list(self.varDispObj.get(u"setVars"))
        if self.listVars != None:
            if len(self.listVars) > 0:
                for var in self.listVars:
                    if var not in self.y:
                        self.y[var]=np.array(np.zeros(self.numXPints , np.float) ) 
                    y = self.y[var]
                    y = np.concatenate((y[1:], y[:1]), 1)
                    y[-1] = PyLinXRunEngine.DataDictionary[var]
                    self.y[var] = y
                QtGui.QWidget.update(self)
           
    def paintEvent(self, event=None):
        self.paint.begin(self)
        self.paint.fillRect(20, 20, 360, 160, QtGui.QColor(255,255,255))
        self.paint.drawRect(20, 20, 360, 160)
        for var in self.listVars:
            path = QtGui.QPainterPath()
            path.moveTo(20, 100)
            y = self.y[var]
            for i in range(1, len(self.t)):
                path.lineTo(20 + self.fac_t * self.t[i] , 100 + self.fac_y * y[i] ) 
            self.paint.drawPath(path)
        self.paint.end()
        
    def addVar(self, varName):
        
        global DataDictionary
        if varName not in DataDictionary:
            raise Exception(u"Error: Variable could not be displayed!")
        else:
            if not varName in self.listVars: 
                self.listVars.append(varName)
            
    def delVar(self, varName):
        
        global DataDictionary
        if varName not in DataDictionary:
            raise Exception(u"Error: Variable could not be deleted!")
        else:
            self.listVars.pop(varName)