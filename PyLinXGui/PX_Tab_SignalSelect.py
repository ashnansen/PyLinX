import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer

import PyLinXData.PyLinXHelper as helper
import PyLinXCtl.PyLinXMainController as ctl
import matplotlib.pyplot as pyplot


class PX_Tab_SignalSelect_TreeView(QtGui.QTreeView):
    def __init__(self, parent=None, listItems={}, mainDrawingWidget = None):
        super(PX_Tab_SignalSelect_TreeView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(16, 16))
        self.listItems = listItems
        self.setIndentation(0)
        self.setHeaderHidden(True)
        self.mainDrawingWidget = mainDrawingWidget
        
        self.bTimer = False
        self.bDoubleClicked = False
        self.bDoubleClick = False
        

        
    ###################
    # Mouese Click 
    ###################
           
    def mousePressEvent(self, event):
        self.event = event
        if not self.bTimer:
            self.bTimer = True
            self.bDoubleClicked = False
            self.bDoubleClick = False
            QTimer.singleShot(QtGui.QApplication.instance().doubleClickInterval(),
                              self.performSingleClickAction)
        super(PX_Tab_SignalSelect_TreeView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.bTimer and event.button() == QtCore.Qt.LeftButton:
            if self.bDoubleClick:
                self.performDoubleClickAction()
            else:
                self.bDoubleClick = True
        #if self.bTimer and event.button() == QtCore.Qt.LeftButton:
            
        super(PX_Tab_SignalSelect_TreeView, self).mouseReleaseEvent(event)    

    def performSingleClickAction(self):

        self.bTimer = False
        if self.bDoubleClick:
            return
             
        label = self.__getLabelName()#= self.childAt(self.event.pos())
        if not label:
            return 
        mimeData = QtCore.QMimeData()
        indices = self.selectedIndexes()
        if len(indices) > 0:
            index = indices[0]
            item = self.model().item(index.row(),0)
            labelName = item.getFullSignalName()
            mimeData.setText(labelName)
            labelNameList = labelName.split("|")
            qlabel = QtGui.QLabel(labelNameList[0])
            pixmap = QtGui.QPixmap(qlabel.size())
            qlabel.render(pixmap)
    
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
    
            dropAction = drag.exec_(QtCore.Qt.CopyAction|QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)
            if dropAction == QtCore.Qt.MoveAction:
                label.close()            

    def performDoubleClickAction(self):

        self.bDoubleClicked = True
        indices = self.selectedIndexes()
        if len(indices) > 0:
            index = indices[0]            
            labelName = self.model().item(index.row(),0).getFullSignalName()
        labelName = self.__getLabelName()
        if labelName:
            self.emit(QtCore.SIGNAL("plotSignal"), labelName )
                        

    def __getLabelName(self): 

        indices = self.selectedIndexes()
        if len(indices) > 0:
            index = indices[0]            
            return self.model().item(index.row(),0).getFullSignalName()
        else:
            return None
            
            
    #########################
    # DRAG N DROP
    #########################

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
 
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.emit(QtCore.SIGNAL("dropped"), links)
        else:
             
            event.ignore()
 
    def getSignal(self):
        indices = self.selectedIndexes()
        row = indices[0].row()
        item = self.model().item(row,0)
        return item.getFullSignalName()
    
    ############
    # MISC
    ############

class NamedQStandardItem(QtGui.QStandardItem):

    def __init__(self, itemString, nameFileObject):
        
        super(NamedQStandardItem, self).__init__(itemString)
        self.nameFileObject = nameFileObject
        self.setEditable(False)
    
    def getFullSignalName(self):
        
        return unicode( self.text()  + u"|" + self.nameFileObject)

        
class treeModel_Signals(QtGui.QStandardItemModel):
    
    def __init__(self, parent = None, treeView = None, tabWidget = None):
        super(treeModel_Signals, self).__init__(parent)
        self.appendColumn([])
        self.appendColumn([])
        self.__treeView = treeView
        self.__tabWidget = tabWidget
       
        
    def loadSignals(self, signals, signalFileName, masterSignals):
                
        for signal in signals:
            if signal not in masterSignals:
                modelItem =  NamedQStandardItem( signal, signalFileName)
                self.appendRow(modelItem)
                rowIndex = self.rowCount()
                iconItem = QtGui.QStandardItem(u"")
                self.setItem(rowIndex - 1, 1, iconItem)
                varItem = QtGui.QStandardItem(u"")
                self.setItem(rowIndex - 1, 2, varItem)
        if len(signals) > 0:
            self.connect(self.__tabWidget.myListWidget, \
                    QtCore.SIGNAL("customContextMenuRequested(QPoint)" ),self.__tabWidget.listItemRightClicked)        


        
        self.__treeView.setColumnWidth(1,20)
        self.__treeView.setColumnWidth(0,90)
        self.__treeView.setColumnWidth(2,90)
        
        item = QtGui.QStandardItem()
        item.setIcon(QtGui.QIcon(u"./Recources/Icons/mappedTo16.png"))
        self.setHorizontalHeaderItem(1,item)
        self.setHorizontalHeaderLabels([u"Signal", u"", "Variable"])
    
        
    def setMapping(self, mapping):
        
        rowCount = self.rowCount()
        items = mapping.items()
        for i in range(rowCount):
            signalName = self.item(i,0).getFullSignalName()
            listMappedVars = []
            for j in range(len(items)):
                if signalName == items[j][1]:
                    listMappedVars.append(items[j][0])
            if len(listMappedVars) > 0:
                self.setItem(i,1,QtGui.QStandardItem(QtGui.QIcon( u"./Recources/Icons/mappedTo16.png"),u""))
                self.setItem(i,2,QtGui.QStandardItem(u" ".join(listMappedVars)))
            else:
                self.setItem(i,1,QtGui.QStandardItem(u""))
                self.setItem(i,2,QtGui.QStandardItem(u""))

        self.__treeView.repaint()


class PX_Tab_SignalSelect(QtGui.QWidget):
    
    def __init__(self, mainController,   drawWidget = None  ):
        
        super(QtGui.QWidget,self).__init__()
        self.listItems={}
        myBoxLayout = QtGui.QVBoxLayout()
        self.setLayout(myBoxLayout)
        self.toolbar = QtGui.QToolBar()
        self.mainController = mainController
        self.__signalsFolder = mainController.getb(u"signalFiles")
        self.__objectHandler = mainController.getb(u"ObjectHandler")       

        self.myListWidget = PX_Tab_SignalSelect_TreeView(self, self.listItems, mainDrawingWidget = drawWidget )  
        self.myListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.model = treeModel_Signals(self, self.myListWidget, self)
        self.myListWidget.setModel(self.model)
        
        self.connect(self.myListWidget, QtCore.SIGNAL("plotSignal"), self.plotSignal)
        
        myBoxLayout.addWidget(self.toolbar)
        myBoxLayout.addWidget(self.myListWidget)

        ## Tool-Bar

        self.toolbar.setIconSize (QtCore.QSize(16,16))
        
        # Add Action to Toolbar
        
        self.__actionLoad = helper.loadAction(widget=self,  IconPath =u"./Recources/Icons/openSignal24.png", ToolTip=u"Load Signal File",\
                                        ShortCut=u"Ctrl+L", Callback=self.loadSignalFile, ToolBar=self.toolbar)
        self.__actionMap  = helper.loadAction(widget=self,  IconPath =u"./Recources/Icons/SignalMapping16.png", ToolTip=u"Map Signals by Name",\
                                        ShortCut=u"Ctrl+M", Callback=self.mapSignalsByName, ToolBar=self.toolbar)
        self.__actionDelMap= helper.loadAction(widget=self,  IconPath =u"./Recources/Icons/deleteMap16.png", ToolTip=u"Delete Mapping",\
                                                            Callback=self.delMap, ToolBar=self.toolbar)

        
        self.toolbar.setStyleSheet(u".QToolBar {border: 0px;}")
        self.SignalFileName = None
       
        
        
        # Turns interacive mode of matplotlib.pyplot on
        pyplot.ion()
        self.repaint()
        
    def delMap(self):
        mapping = self.__objectHandler.get(u"mapping") 
        for key in mapping:
            command = u"set @objects/" + key + u".signalMapped 0"
            self.mainController.execCommand(command)  
        self.repaint()  
        
    def repaint(self):
        bSignalLoaded = self.__signalsFolder.get(u"bSignalLoaded")
        self.__actionMap.setEnabled(bSignalLoaded)
        self.__actionDelMap.setEnabled(bSignalLoaded)
        self.__actionLoad.setEnabled(not bSignalLoaded)
        mappingFromData = self.__objectHandler.get(u"mapping") 
        self.model.setMapping(mappingFromData)        
        super(PX_Tab_SignalSelect, self).repaint()

    def plotSignal(self, labelName):
        
        signal = self.mainController.get(u"@signals." + unicode(labelName)) 
        if (u"xlabel" in signal) and (u"time" in signal):
            pyplot.plot(signal[u"time"], signal[u"values"])
            pyplot.xlabel(signal[u"xlabel"])
        else:
            pyplot.plot(signal[u"values"])
        pyplot.title(signal[u"title"])
        pyplot.ylabel(signal[u"ylabel"])    
        pyplot.grid(True)
        pyplot.show()    
        
    def loadSignalFile(self):
        
        strPath = helper.showFileSelectionDialog(self,strPath = None, bDir = False, \
                                       strExt = u"All files (*.*);;MDF3 (*.dat *.mdf);;MDF4 (*.mf4)", \
                                       strHeader = u"Load Singal File",\
                                       dialogType = u"load",\
                                       bFileObject = False )
        if not strPath:
            return
        command = u"new signalFile " + strPath 
        newSignalFile = self.mainController.execCommand(command)
        signals = newSignalFile.get(u"signals")
        masterSignals = newSignalFile.get(u"masterSignals")
        self.SignalFileName= newSignalFile.get(u"Name")
        
        self.model.loadSignals(signals, self.SignalFileName, masterSignals)
        self.myListWidget.setHeaderHidden(False)
        self.repaint()
    
    def mapSignalsByName(self):
        signals = self.__signalsFolder.get(u"signals")
        varObjects = self.__objectHandler.get(u"listObjects")
        mapping = {}
        for varObject in varObjects:
            for signal in signals:
                signal_0 = signal[0] 
                if signal_0 == varObject:
                    if not varObject in mapping:
                        mapping[varObject] = signal_0 + u"|" + signal[1]
        
        for key in mapping:
            signal = mapping[key]
            command = u"set @objects/" + key + u".signalMapped " + signal
            self.mainController.execCommand(command)  

        self.repaint()             
    
    def addListWidgetItem(self, listItemName = None):
        if listItemName == None:
            listItemName='Item '+str(len(self.listItems.keys()))        
        self.listItems[listItemName]=None 
        self.rebuildListWidget() 

    def listItemRightClicked(self, QPos): 
        
        listObjects = self.__objectHandler.get(u"listObjects")
        mapping = self.__objectHandler.get(u"mapping")
        signal = self.myListWidget.getSignal()
        menu = QtGui.QMenu()
        listActions = []
        # listObjects.sort()
        for obj in listObjects:
            action = QtGui.QAction(QtCore.QString(obj), menu)
            action.setCheckable(True)
            if obj in mapping:
                mappedSignal = mapping[obj]
                bSignalMapped = (signal in mappedSignal) or (signal == mappedSignal)
                if bSignalMapped:
                    action.setChecked(True)
            menu.addAction(action)
            listActions.append(action)                                
        action = menu.exec_(self.myListWidget.viewport().mapToGlobal(QPos))
        if action != None:
            idxAction = listActions.index(action)        
            obj2 =  listObjects[idxAction]
            if action.isChecked():
                command = u"set @objects/" + obj2 + u".signalMapped " + signal
            else:
                command = u"set @objects/" + obj2 + u".signalMapped 0"
            self.mainController.execCommand(command)  
        self.repaint()
        self.myListWidget.mainDrawingWidget.repaint()      
        

    def rebuildListWidget(self):
        self.myListWidget.clear()
        items=self.listItems.keys()
        if len(items)>1: items.sort()
        for listItemName in items:
            listItem = NamedQListWidgetItem( listItemName, self.SignalFileName)
            self.listItems[listItemName]=listItem
            self.myListWidget.addItem(listItem)
           

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainController = ctl.PyLinXMainController( bListActions = False)
    dialog_1 = PX_Tab_SignalSelect(mainController)
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec_())     