import sys, os
from PyQt4 import QtCore, QtGui

import PyLinXData.PyLinXHelper as helper
import PyLinXCtl.PyLinXMainController as ctl
import matplotlib.pyplot as pyplot

class ThumbListWidget(QtGui.QListWidget):
    def __init__(self, parent=None, listItems={}):
        super(ThumbListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(124, 124))
        self.doubleClicked.connect(self.doubleClickEvent)
        self.listItems = listItems

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
            
    def doubleClickEvent(self, modelIndex):
        print u"doubleClocked"
        #labelName = self.item(modelIndex.row()).getFullSignalName()
        #self.emit(QtCore.SIGNAL("plotSignal"), labelName )


class NamedQListWidgetItem(QtGui.QListWidgetItem):

    def __init__(self, itemString, nameFileObject = None):
        
        super(NamedQListWidgetItem, self).__init__(itemString)
            

class PX_Tab_ObjectHandlerList(QtGui.QWidget):
    
    def __init__(self, mainController):
        
        super(QtGui.QWidget,self).__init__()
        self.listItems={}
        myBoxLayout = QtGui.QVBoxLayout()
        self.setLayout(myBoxLayout)
        self.toolbar = QtGui.QToolBar()
        self.mainController = mainController
        self.__objectHandler = mainController.getb(u"ObjectHandler")        

        self.listItems = {}

        self.myListWidget = ThumbListWidget(self, self.listItems)  
        self.myListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.myListWidget.connect(self.myListWidget, QtCore.SIGNAL("customContextMenuRequested(QPoint)" ), self.listItemRightClicked)
        
        #self.connect(self.myListWidget, QtCore.SIGNAL("plotSignal"), self.plotSignal)
        
        myBoxLayout.addWidget(self.toolbar)
        myBoxLayout.addWidget(self.myListWidget)

        ## Tool-Bar

        self.toolbar.setIconSize (QtCore.QSize(16,16))
        
        # Add Action to Toolbar
        
        #self.__actionLoad = helper.loadAction(widget=self,  IconPath =u"./Recources/Icons/openSignal24.png", ToolTip=u"Load Signal File",\
        #                                ShortCut=u"Ctrl+L", Callback=self.loadSignal, ToolBar=self.toolbar)
        #self.__actionMap  = helper.loadAction(widget=self,  IconPath =u"./Recources/Icons/SignalMapping16.png", ToolTip=u"Map Signals by Name",\
        #                                ShortCut=u"Ctrl+M", Callback=self.mapSignalsByName, ToolBar=self.toolbar)

        
        self.toolbar.setStyleSheet(u".QToolBar {border: 0px;}")
        self.SignalFileName = None
        self.repaint()
        
    def repaint(self):
        listObjects = self.__objectHandler.get(u"listObjects")
        self.listItems = {}
        for _object in listObjects:
            listItem = NamedQListWidgetItem( _object)
            self.addListWidgetItem(listItem)
        super(PX_Tab_ObjectHandlerList, self).repaint()

#     def plotSignal(self, labelName):
#         signal = self.mainController.get(u"@signals." + unicode(labelName)) 
#         if (u"xlabel" in signal) and (u"time" in signal):
#             pyplot.plot(signal[u"time"], signal[u"values"])
#             pyplot.xlabel(signal[u"xlabel"])
#         else:
#             pyplot.plot(signal[u"values"])
#         pyplot.title(signal[u"title"])
#         pyplot.ylabel(signal[u"ylabel"])    
#         pyplot.grid(True)
#         pyplot.show()
        
    def addListWidgetItem(self, listItemName = None):
        if listItemName == None:
            listItemName='Item '+str(len(self.listItems.keys()))        
        self.listItems[listItemName]=None 
        self.rebuildListWidget() 
# 
#     def listItemRightClicked(self, QPos): 
#         self.listMenu= QtGui.QMenu()
#         menu_item = self.listMenu.addAction("Remove Item")
#         if len(self.listItems.keys())==0: menu_item.setDisabled(True)
#         self.connect(menu_item, QtCore.SIGNAL("triggered()"), self.menuItemClicked) 
# 
#         parentPosition = self.myListWidget.mapToGlobal(QtCore.QPoint(0, 0))        
#         self.listMenu.move(parentPosition + QPos)
#         self.listMenu.show() 
# 
#     def menuItemClicked(self):
#         if len(self.listItems.keys())==0: print 'return from menuItemClicked'; return
#         currentItemName=str(self.myListWidget.currentItem().text() )
#         self.listItems.pop(currentItemName, None)
#         self.rebuildListWidget()

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
    mainController = ctl.PyLinXMainController(bListActions = False)
    
    # Example-Data
    
    script = u"new varElement TestVar_0 150 90 15 refName=\"TestVar_0\"\n\
new varElement Variable_id4 150 140 15 refName=\"Variable_id4_1\" \n\
new varElement Variable_id4 400.0 100.0 15 refName=\"Variable_id4_2\"\n\
new basicOperator + 300.0 100.0 name=u\"Operator_1\"\n\
new connector TestVar_0 Operator_1 idxInPin=1\n\
new connector Variable_id4_1 Operator_1 idxInPin=0\n\
new connector Operator_1 Variable_id4_2 idxInPin=0"
            
    mainController.execScript(script)    
    
    dialog_1 = PX_Tab_SignalSelect(mainController)
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec_()) 