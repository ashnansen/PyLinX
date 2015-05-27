'''
Created on 12.12.2014

@author: Waetzold Plaum
'''
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
import numpy as np
import math
import time
import cProfile

# test parameters

# number of test oscis
N_OSCIS = 6 #  has to be an even integer
TIME_CONSTANT = 0.03

class DataPlot2(QtGui.QWidget):

    def __init__(self, t_max = 1., *args):
        super(DataPlot2, self).__init__(*args)
        self.paint = QtGui.QPainter()
        self.t_max = t_max
        self.pen   = QPen(QtGui.QColor(0,0,0),1, QtCore.Qt.SolidLine)
        self.t     = np.array([0.1*i for i in range(201)])
        self.y     = []
        for i in range(10):
            self.y.append( np.array(np.zeros(201, np.float) ) )
        self.resize(400,200)
        self.fac_t = 360 / max(self.t)
        self.fac_y = 160 / 2
        self.counter = 0
        self.paths = []
        for i in range(N_OSCIS):
            self.paths.append( QPainterPath())
    
    def update(self, data):
        for i in range(N_OSCIS):
            self.y[i] = np.concatenate((self.y[i][1:], self.y[i][:1]), 1)
            self.y[i][-1] = data[i]
        # faster
        QtGui.QWidget.update(self)
        # slower
        # QtGui.QWidget.repaint(self)
        
    def paintEvent(self, event=None):
        #if self.counter %3 == 0:
        self.paint.begin(self)
        self.paint.fillRect(20, 20, 360, 160, QtGui.QColor(255,255,255))
        self.paint.drawRect(20, 20, 360, 160)
        for j in range(N_OSCIS):
            y_j = self.y[j]
            path = QPainterPath()
            path.moveTo(20, 100)
            for i in range(1, len(self.t)):
                path.lineTo(20 + self.fac_t * self.t[i] , 100 + self.fac_y * y_j[i] ) 
            self.paint.drawPath(path)
            
            
#             self.paths[j].moveTo(20, 100)
#             for i in range(1, len(self.t)):
#                 self.paths[j].lineTo(20 + self.fac_t * self.t[i] , 100 + self.fac_y * self.y[j][i] ) 
#             self.paint.drawPath(self.paths[j])

        self.paint.end()
        #QApplication.processEvents()
        self.counter += 1


class MainWidget(QtGui.QWidget):
    def __init__(self):
        super(MainWidget,self).__init__()
        widget2 = QtGui.QWidget()
        widget3 = QtGui.QWidget()
        vLayout1 = QtGui.QVBoxLayout()
        vLayout2 = QtGui.QVBoxLayout()

        self.mainLayout = QtGui.QHBoxLayout()
        self._thread = UpdateThread(self)
        self._thread.updated.connect(self.update, QtCore.Qt.BlockingQueuedConnection)
        #self._thread.updated.connect(self.update)
        self._thread.start()

        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(widget2)   
        self.mainLayout.addWidget(widget3)   
        widget2.setLayout(vLayout1)
        widget3.setLayout(vLayout2)
        self.listWidgets = []
        self.listDataFactories = []
        self.DataFactory = DataFactory(100)
        for i in range(N_OSCIS):
            self.listWidgets.append(DataPlot2(t_max = 5.))
            self.listWidgets[-1].resize(500,180)
            self.listDataFactories.append(DataFactory(10))
        for i in range(N_OSCIS/2):
            vLayout1.addWidget(self.listWidgets[i])
        for i in range(N_OSCIS/2,N_OSCIS):
            vLayout2.addWidget(self.listWidgets[i])
        self.resize(1100,1000)
        self.show()
    
    def update(self):
        result = self.DataFactory.get()
        for i in range(N_OSCIS):
            self.listWidgets[i].update(result[(10*i):(10*(i + 1))])

class DataFactory(object):
    
    def __init__(self,_n=1):
        self.n = _n
        self.t =  0 
        self.results = [None for x in range(self.n)]
        
    def fun(self, t,par):
        return 0.14 * par * math.cos(0.1 * t * 0.5 * par )
    
    def get(self):
        for i in range(len(self.results)):
            result = self.fun(self.t, 0.4 * math.sqrt(float(i)))
            self.results[i] = result 
        self.t += 1
        return self.results

class UpdateThread(QtCore.QThread):
     
    updated = QtCore.pyqtSignal(str)
    
    def run(self):
        #time.sleep(1.)
        i = 0
        QApplication.processEvents()
        while True:
            #time.sleep(TIME_CONSTANT)
            self.updated.emit(str(1))
            i+=1
            
class QtApp(object):
    
    def __init__(self):
        super(QtApp, self).__init__()
        self.oszi = MainWidget()
        self.oszi.show()

def run():

    app = QtGui.QApplication(sys.argv)
    qtapp = QtApp() 
    app.exec_()  

if __name__ == '__main__':

    PROFILE = True
    
    if PROFILE:
        cProfile.run('run()')
    else:
        run()