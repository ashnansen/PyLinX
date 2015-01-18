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
        super(RootContainer, self).__init__("root")
        self.__mainWindow = mainWindow
        self.__listActions = [None, mainWindow.ui.actionNewElement, mainWindow.ui.actionNewPlus]
        
        
    
        
    def set(self, attr, value):
        
        if attr == "idxToolSelected":
            idxToolSelectedOld = self.get("idxToolSelected")
            if idxToolSelectedOld not in [None, 0]:
                oldAction = self.__listActions[idxToolSelectedOld]
                oldAction.setChecked(False)
            if value > 0 and value <= PyLinXHelper.ToolSelected.max:
                self.__listActions[value].setChecked(True)
                return BContainer.BContainer.set(self,"idxToolSelected", value)
            elif value == 0:
                return BContainer.BContainer.set(self,"idxToolSelected", 0)
            
        elif attr == "bSimulationMode":
            
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
                return BContainer.BContainer.set(self,"bSimulationMode", True)
            
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
                return BContainer.BContainer.set(self,"bSimulationMode", False)
                
        else:
            return BContainer.BContainer.set(self,attr, value)
