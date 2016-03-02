'''
Created on 30.10.2014

@author: Waetzold Plaum
'''
# General Libraries - alphabedic order
import copy
import cProfile
import ctypes
import inspect
import jsonpickle
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys
import threading
import Queue
import codecs

# Project specific Libraries - alphabedic order
from PyLinXData import BContainer, PyLinXCoreDataObjects, PyLinXHelper, \
    PX_Signals, PX_DataDictionary
from PyLinXGui import *
from PyLinXCodeGen import *
import PyLinXGui.PX_Templates as PX_Templ
import PyLinXGui.PX_TabWidget_main as PX_TabWidget_main
import PyLinXGui.PX_Tab_SignalSelect as PX_Tab_SignalSelect
import PyLinXGui.PX_ScrollArea_Main as PX_ScrollArea_Main 
#import PylinXGui.PX_ScrollArea_Main as PX_ScrollArea_Main
import PyLinXData.PyLinXHelper as helper
from PyLinXCtl import PyLinXMainController

class PyLinXMain(QtGui.QMainWindow):

    def __init__(self):
 
        super(PyLinXMain, self).__init__()
        
        reload(sys) 
        sys.setdefaultencoding('utf8')

        uiString = u".//Recources//Ui//PyLinX_v0_5.ui"
        self.ui = uic.loadUi(uiString)
        self.ui.setWindowIcon(QtGui.QIcon(r"icons/pylinx_16.png"))
        self.ui.setWindowTitle('PyLinX')
        self.runThreadMessageQueue = Queue.Queue()
        #QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('cleanlooks') )
        #QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('plastique') )
        
        
        # Main Data Structures

        self.mainController = PyLinXMainController.PyLinXMainController(mainWindow = self )

        _rootGraphics = self.mainController.getb(u"rootGraphics")
        
        # ExampleData

        script = u"new varElement TestVar_0 150 90 15 refName=\"TestVar_0\"\n\
new varElement Variable_id4 150 140 15 refName=\"Variable_id4_1\" \n\
new varElement Variable_id4 400.0 100.0 15 refName=\"Variable_id4_2\"\n\
new basicOperator + 300.0 100.0 name=u\"Operator_1\"\n\
new connector TestVar_0 Operator_1 idxInPin=1\n\
new connector Variable_id4_1 Operator_1 idxInPin=0\n\
new connector Operator_1 Variable_id4_2 idxInPin=0"
            
        self.mainController.execScript(script)
        
                
        # run Engine
        
        self.runEngine = None
        
        # Drawing GUI
        
        # Events
        
        self.stopRunEvent = threading.Event()
        self.repaintEvent = threading.Event()
        
        # DrawWidget and ScrollArea
        #scrollingArea = QtGui.QScrollArea()
        scrollingArea = PX_ScrollArea_Main.PX_ScrollArea_Main()
        horizongalLayout2 = QtGui.QHBoxLayout()
        drawWidget = PX_Widget_MainDrawArea.DrawWidget(self.mainController, self, self.repaintEvent )        
        self.drawWidget = drawWidget
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
        drawWidget.setAutoFillBackground(True)
        drawWidget.setPalette(pal)
        horizongalLayout2.addWidget(drawWidget)
        scrollingArea.setLayout(horizongalLayout2)
        scrollingArea.setContentsMargins(-30,-30,-30,-30)
        scrollingArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollingArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)        
        
        # TabWidget
        self.ui.TabWidget = PX_TabWidget_main.PX_TabWidget_main(mainController = self.mainController)
        widget0 = QtGui.QWidget()
        self.ui.TabWidget.setMinimumWidth(260)
        self.ui.TabInfo = QtGui.QWidget() 
        self.ui.TabWidget.adjoinTab(self.ui.TabInfo, u"Info", PX_TabWidget_main.PX_TabWidget_main.DisplayRole.inEditAndSimulationMode,1)
        self.ui.TabSignals = PX_Tab_SignalSelect.PX_Tab_SignalSelect(self.mainController, drawWidget = self.drawWidget  )
        self.ui.TabWidget.adjoinTab(self.ui.TabSignals, u"Signals", PX_TabWidget_main.PX_TabWidget_main.DisplayRole.onlyInSimulationMode,2)
        self.ui.TabElements = PX_Tab_ObjectHandlerList.PX_Tab_ObjectHandlerList(self.mainController)
        self.ui.TabWidget.adjoinTab(self.ui.TabElements, u"Elements", PX_TabWidget_main.PX_TabWidget_main.DisplayRole.onlyInEditMode,3)
        self.connect(self, QtCore.SIGNAL("updateTabs"), self.ui.TabWidget.updateTabs)
        
        #Connecting Signal
        self.connect(drawWidget, QtCore.SIGNAL(u"signal_repaint_Tab_SignalSelect"),self.ui.TabSignals.repaint)

        
        # Splitter
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.ui.TabWidget)
        splitter1.addWidget(scrollingArea)
        splitter1.setStretchFactor(1,4)
        splitter1.setStretchFactor(0,1)
        splitter1.setStyleSheet("""
        .QSplitter {
            padding-left: 8px;
            padding-top: 8px;
            padding-right: 8px;
            }
        """)

        
        self.ui.setCentralWidget(splitter1)

        scrollingArea.setWidget(drawWidget)
        scrollingArea.setWidgetResizable(True)
        scrollingArea.setAutoFillBackground(False)

        self.ui.show()
        
        # Connecting Actions
        ####################
        
        # Menu-Bar
            
            # Programm
        
        self.ui.actionClose.triggered.connect(self.closeApplication)
        
            # Project
        
        self.ui.actionNewProject.triggered.connect(self.on_actionNewProject)
        self.ui.actionLoadProject.triggered.connect(self.on_actionLoadProject)
        self.ui.actionSave.triggered.connect(self.on_actionSave)
        self.ui.actionSave_As.triggered.connect(self.on_actionSave_As)
        
        # Tool-Bar
        
        self.ui.actionNewElement.triggered.connect(self.on_actionNewElement)
        self.ui.actionNewElement.setCheckable(True)
        self.ui.actionNewPlus.triggered.connect(self.on_actionNewPlus)
        self.ui.actionNewMinus.triggered.connect(self.on_actionNewMinus)
        self.ui.actionNewMultiplication.triggered.connect(self.on_actionNewMultiplication)
        self.ui.actionNewDivision.triggered.connect(self.on_actionNewDivision)
        
        self.ui.actionNewPlus.setCheckable(True)
        self.ui.actionNewMinus.setCheckable(True)
        self.ui.actionNewMultiplication.setCheckable(True)
        self.ui.actionNewDivision.setCheckable(True)
        self.ui.actionRun.setEnabled(False)
        self.ui.actionActivate_Simulation_Mode.triggered.connect(self.on_Activate_Simulation_Mode)
        self.ui.actionRun.triggered.connect(self.on_run)
        self.ui.actionStop.triggered.connect(self.on_stop)
        

        self.ui.resize(800,600)
        
        
        # Configurations that require the GUI to exist
        self.mainController.set(u"bSimulationMode", False)
        
######################
# Methods
#####################


# Callbacks
####################

    def closeApplication(self):
        
        print "CLOSE!"
        if QtGui.QMessageBox.question(None, u"", u"Soll PyLinX wirklich beendet werden?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)\
                 == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
            
    def on_actionNewElement(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newVarElement) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewPlus(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newPlus) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)

    def on_actionNewMinus(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newMinus) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewMultiplication(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newMultiplication) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewDivision(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newDivision) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)

            
    def on_actionSave(self):
        rootGraphics = self.mainController.getb(u"rootGraphics")
        if rootGraphics.isAttr(u"strSavePath"):
            strSavePath = rootGraphics.get(u"strSavePath")
            self.__saveProject(strSavePath)
        else:
            self.on_actionSave_As()

    
    def on_actionSave_As(self):
        if self.mainController.isAttr(u"strSavePath"):
            strSavePath_old = self.mainController.get(u"strSavePath")
            (strPath, strSavePath_old_file) = os.path.split(strSavePath_old)
        else:
            strPath = os.getcwd()
        strSavePath= helper.showFileSelectionDialog(self.ui,strPath, bDir = False, strExt = u"*.pyp", \
                                                    strHeader =u"Select File to save Project...",\
                                                    dialogType = u"save",\
                                                    bFileObject = False)
        (strSavePath_base,strSavePath_ext) = os.path.splitext(strSavePath)
        if not  strSavePath_ext == u"pyp":
            strSavePath = strSavePath_base + u".pyp"
        self.__saveProject(strSavePath)

     
    def __saveProject(self, strSavePath):    
        
        _file = codecs.open(strSavePath, encoding='utf-8', mode='w')
        
        listCommands = self.mainController.get(u"listCommands")
        strCommands = u""
        for command in listCommands:
            strCommands += command
            strCommands += u"\n"
        _file.write(strCommands)
        _file.close()
        rootGraphics = self.mainController.getb(u"rootGraphics")
        rootGraphics.set(u"strSavePath", strSavePath)  

  
    def on_actionLoadProject(self):
         
        strPath = os.getcwd()
        _file, strSavePath = helper.showFileSelectionDialog(self.ui,strPath, bDir = False,strHeader ="Select File to load Project...",\
                                                     strExt = u"*.pyp",\
                                                     dialogType = u"load")  
 
        if _file == None:
            return
         
        old_Controller = self.mainController
 
        self.mainController = PyLinXMainController.PyLinXMainController(mainWindow = self )
        _file_read = _file.read()
 
        self.mainController.execScript(_file_read)
         
        old_Controller.delete()
        newProject = self.mainController.getb(u"rootGraphics")
        self.drawWidget.newProject(self.mainController)
         
        rootGraphics = self.mainController.getb(u"rootGraphics")
        rootGraphics.set(u"strSavePath", strSavePath)          
 
        self.drawWidget.repaint()

    
    def on_actionNewProject(self):
        rootGraphicsNew = PyLinXCoreDataObjects.PX_PlottableObject(u"rootGraphics")
        self.mainController.delete(u"rootGraphics")
        self.mainController.set(u"bSimulationMode", False)
        self.mainController.paste(rootGraphicsNew)
        self.drawWidget.activeGraphics = rootGraphicsNew
        self.drawWidget.repaint()
        

        
    def on_Activate_Simulation_Mode(self):
        
        bSimulationMode = self.mainController.get(u"bSimulationMode")
        if bSimulationMode:
            self.mainController.execCommand(u"set @mainController.bSimulationMode False")
        else:
            self.mainController.execCommand(u"set @mainController.bSimulationMode True")
        self.drawWidget.repaint()
        
    def on_run(self):
        
        self.runEngine = self.mainController.getb(u"PX_CodeGeerator")
        self.runEngine.startRun(self.drawWidget, self.stopRunEvent, self.repaintEvent)
        self.mainController.set(u"bSimulationRunning", True)
        
    def on_actionOsci(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newVarDispObj) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_stop(self):
        self.runThreadMessageQueue.put(u"stopRun")
        

def run():
    app = QtGui.QApplication(sys.argv)
    obj = PyLinXMain()   
    app.exec_()
    
    
if __name__ == '__main__':
    
    PROFILE = False
    
    if PROFILE:
        cProfile.run('run()')
    else:
        run()
