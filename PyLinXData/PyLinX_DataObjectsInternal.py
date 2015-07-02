'''
Created on 26.11.2014

@author: Waetzold Plaum
'''

import BContainer
import PyLinXHelper
from PyQt4 import QtGui, QtCore, uic, Qt
import inspect

import PX_Templates as PX_Templ
import PyLinXDataObjects 



class RootContainer(BContainer.BContainer):
    '''
    classdocs
    '''

    def __init__(self, mainWindow):
        '''
        Constructor
        '''
        super(RootContainer, self).__init__(u"root")
        self.__mainWindow = mainWindow
        self.__listActions = [None, mainWindow.ui.actionNewElement, mainWindow.ui.actionNewPlus,\
                              mainWindow.ui.actionOsci, mainWindow.ui.actionNewMinus, \
                              mainWindow.ui.actionNewMultiplication, mainWindow.ui.actionNewDivision]
        self.set(u"listDataDispObj", [])
        
    def get(self, attr):
    
        if attr == u"mainWindow":
            #return self.__mainWindow.ui.DrawWidget
            return self.__mainWindow
        elif attr == u"drawWidget":
            return self.__mainWindow.drawWidget
        else:
            return super(RootContainer, self).get(attr)  
        
    def set(self, attr, value):
        
        if attr == u"idxToolSelected":
            idxToolSelectedOld = self.get(u"idxToolSelected")
            if idxToolSelectedOld not in [None, 0]:
                oldAction = self.__listActions[idxToolSelectedOld]
                oldAction.setChecked(False)
            if value > 0 and value <= PyLinXHelper.ToolSelected.max:
                self.__listActions[value].setChecked(True)
                return BContainer.BContainer.set(self,u"idxToolSelected", value)
            elif value == 0:
                return BContainer.BContainer.set(self,u"idxToolSelected", 0)
            
        elif attr == u"bSimulationMode":
            
            if value == True:
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.backgroundSim)
                self.__mainWindow.drawWidget.setPalette(pal)                
                self.__mainWindow.ui.actionRun.setEnabled(True)
                self.__mainWindow.ui.actionOsci.setEnabled(True)
                self.__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(True)
                self.__mainWindow.ui.actionNewElement.setEnabled(False)
                self.__mainWindow.ui.actionNewPlus.setEnabled(False)
                self.__mainWindow.ui.actionNewMinus.setEnabled(False)
                self.__mainWindow.ui.actionNewMultiplication.setEnabled(False)
                self.__mainWindow.ui.actionNewDivision.setEnabled(False)
                self.__mainWindow.ui.actionStop.setEnabled(True)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"widgetShow", ())
                return BContainer.BContainer.set(self,u"bSimulationMode", True)
            
            elif value == False:
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
                self.__mainWindow.drawWidget.setPalette(pal)
                self.__mainWindow.ui.actionRun.setEnabled(False)
                self.__mainWindow.ui.actionOsci.setEnabled(False)
                self.__mainWindow.ui.actionActivate_Simulation_Mode.setChecked(False)
                self.__mainWindow.ui.actionNewElement.setEnabled(True)
                self.__mainWindow.ui.actionNewPlus.setEnabled(True)
                self.__mainWindow.ui.actionNewMinus.setEnabled(True)
                self.__mainWindow.ui.actionNewMultiplication.setEnabled(True)
                self.__mainWindow.ui.actionNewDivision.setEnabled(True)
                self.__mainWindow.ui.actionStop.setEnabled(False)
                rootGraphics = self.getb(u"rootGraphics")
                rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"widgetHide", ())
                return BContainer.BContainer.set(self,u"bSimulationMode", False)
                
        else:
            return super(RootContainer, self).set(attr,value)
    
    # Method that synchronizes the DataDictionary with the data hold for graphical representation in the DataViewer
      
    
    def sync(self):
        self.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"sync", ())
        
