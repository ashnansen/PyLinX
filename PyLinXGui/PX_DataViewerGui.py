'''
Created on 12.12.2014

@author: Waetzold Plaum
'''
#import sys
from PyQt4 import QtGui, QtCore
import numpy as np
#import math
#import time
from PyLinXCodeGen import PyLinXRunEngine

#class DataViewerGui(QtGui.QWidget):

class DataViewerGui(QtGui.QDialog):

    def __init__(self, listVars = [], t_max = 1.,  mainGui = None):
    
    
        global DataDictionary
        
        self.listVars    = listVars
        self.listVarAttr = [{} for var in listVars]
        
        size_x = 400
        size_y = 200
        numXPints = 201
    
        
        super(DataViewerGui, self).__init__()
        self.paint = QtGui.QPainter()
        self.t_max = t_max
        self.pen   = QtGui.QPen(QtGui.QColor(0,0,0),1, QtCore.Qt.SolidLine)
        self.t     = np.array([0.1*i for i in range(201)])
        self.y     = []
        for i in range(len(self.listVars )):
            self.y.append( np.array(np.zeros(numXPints, np.float) ) )
        self.resize(size_x,size_y)
        self.fac_t = 360 / max(self.t)
        self.fac_y = 160 / 2
        
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        self._thread = UpdateThread(self)
        self._thread.updated.connect(self.update, QtCore.Qt.BlockingQueuedConnection)
        #self._thread.updated.connect(self.update)
        #self._thread.start()
    
    #def update(self, data):
    def update(self):
        #global DataDictionary
        if PyLinXRunEngine.DataDictionary["*bGuiToUpdate"]:
            for i in range(len(self.listVars )):
                self.y[i] = np.concatenate((self.y[i][1:], self.y[i][:1]), 1)
                self.y[i][-1] = PyLinXRunEngine.DataDictionary[self.listVars[i]]
                print "updating: ", self.y[i][-1] 
            PyLinXRunEngine.DataDictionary["*bGuiToUpdate"] = False
        QtGui.QWidget.update(self)
           
    def paintEvent(self, event=None):
        self.paint.begin(self)
        self.paint.fillRect(20, 20, 360, 160, QtGui.QColor(255,255,255))
        self.paint.drawRect(20, 20, 360, 160)
        for j in range(len(self.listVars)):
            path = QtGui.QPainterPath()
            path.moveTo(20, 100)
            for i in range(1, len(self.t)):
                path.lineTo(20 + self.fac_t * self.t[i] , 100 + self.fac_y * self.y[j][i] ) 
            self.paint.drawPath(path)
        self.paint.end()
        
    def addVar(self, varName):
        
        global DataDictionary
        if varName not in DataDictionary:
            raise Exception("Error: Variable could not be displayed!")
        else:
            if not varName in self.listVars: 
                self.listVars.append(varName)
            
    def delVar(self, varName):
        
        global DataDictionary
        if varName not in DataDictionary:
            raise Exception("Error: Variable could not be deleted!")
        else:
            self.listVars.pop(varName)
    
class UpdateThread(QtCore.QThread):
     
    updated = QtCore.pyqtSignal(str)
    
    def run(self):
        #time.sleep(1.)
        i = 0
        QtGui.QApplication.processEvents()
        while True:
            #time.sleep(TIME_CONSTANT)
            self.updated.emit(str(1))
            i+=1