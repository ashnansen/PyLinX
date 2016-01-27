'''
Test Properties editor
'''
import sys
import inspect 
from PyQt4 import QtGui, QtCore
import copy
 
from PyLinXData import BContainer
from PyLinXGui import BEasyWidget
 
class PropertyEditor(QtGui.QMainWindow):
     
    def __init__(self, initObject = None):
        
        super(PropertyEditor, self).__init__()
        
        # Build GUI
        
        self.setWindowTitle('Example')
        self.mainWidget = QtGui.QWidget()
        self.treeView = QtGui.QTreeView()
        self.splitter = QtGui.QSplitter()
        self.model = QtGui.QStandardItemModel()
        self.__activeWidget = None
        
        
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAnimated(True)
        self.treeView.header().hide() 
        
        self.mainHLayout = QtGui.QHBoxLayout()
        self.mainWidget.setLayout(self.mainHLayout)
        self.stackedWidget = QtGui.QStackedWidget()
        self.stackedWidget.resize(300,300)
        self.setCentralWidget(self.mainWidget)
        self.splitter.addWidget(self.treeView)
        self.rightMainWidget = QtGui.QWidget()
        self.vboxlayout = QtGui.QVBoxLayout()
        self.rightMainWidget.setLayout(self.vboxlayout)
        self.vboxlayout.addWidget(self.stackedWidget)
        self.spacer = QtGui.QSpacerItem(300,300,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Maximum)
        self.vboxlayout.addItem(self.spacer)
        self.splitter.addWidget(self.rightMainWidget)
        self.mainHLayout.addWidget(self.splitter)
        
        # Connect Signals
        
        QtCore.QObject.connect(self.treeView, QtCore.SIGNAL("clicked (QModelIndex)"),self.row_clicked)
        
        # Setup Data Structures
        
        self.__rootConfigTable = ConfigTable([], "ROOT")
        
        types = inspect.getmro(type(initObject))
        if ConfigTable in types:
            self.__rootConfigTable = initObject
        elif BContainer.BContainer in types:
            self.__init_ConfigTree(self.__rootConfigTable, initObject)
        
        self.__rootConfigTable.write(self.model)
        self.treeView.setModel(self.model)        
        self.treeView.expandAll()
        
        self.resize(600, 300)
        self.show()
        
    def __init_ConfigTree(self, confTable, initObject):
        
        #print initObject
        copyElem = BContainer.BList([])
        for elem in  initObject.getChilds():
            types = inspect.getmro(type(elem))
            if ConfigTable in types:
                copyElem = copy.copy(elem)
                confTable.paste(copyElem)
            self.__init_ConfigTree(copyElem, elem)
            
    def row_clicked(self, index):
        if self.__activeWidget != None:
            data = self.__activeWidget.getValues()
        else:
            data = None
        count = self.stackedWidget.count()
        for i in range(count):
            _widget = self.stackedWidget.widget(i)
            self.stackedWidget.removeWidget(_widget)

        newWidget = self.model.itemFromIndex(index).getReference().getWidget()
        self.stackedWidget.addWidget(newWidget)
        self.stackedWidget.setCurrentIndex(0)
        self.__activeWidget = newWidget 
        
        self.onLeaveRow(data)
        
    def onLeaveRow(self, data):
        if data != None:
            print data

class ConfigTable(BContainer.BList):
    
    def __init__(self, _list, DisplayName):
        
        super(ConfigTable, self).__init__(_list)
        self.set(u"DisplayName", DisplayName)
        self.set(u"Name", DisplayName)
        self.__qModelItem = QStandardItemRef( self, DisplayName )
        self.__widget = None
     
    def getWidget(self):
        if self.__widget == None:
            self.__widget = BEasyWidget.EasyWidget(self)
            return self.__widget
        else:
            return self.__widget
        
    def write(self, arg):
        types = inspect.getmro(type(arg))
        if QtGui.QStandardItemModel in types:
            return self.__writeTreeModel(arg, bNotRoot = False) 
        else:
            return super(ConfigTable, self).write(arg)
        
    def __writeTreeModel(self, model, bNotRoot = True):
        if bNotRoot:
            name = self.get(u"DisplayName")
            item = QStandardItemRef(self,name)
            model.appendRow(item)
        else:
            item = model
        for elem in  self.getChilds():
            elem.__writeTreeModel(item)

class QStandardItemRef(QtGui.QStandardItem):
    
    def __init__(self, reference, text, icon = None):
        if icon == None:
            super(QStandardItemRef, self).__init__(text)
        else:
            super(QStandardItemRef, self).__init__(icon, text)
        self.__reference = reference
        
    def getReference(self):
        return self.__reference

if __name__ == '__main__':
    
    class PropertyEditorExample(PropertyEditor):
        
        def __init__(self, bcontainer):
            super(PropertyEditorExample, self).__init__(bcontainer)
            
#         def onLeaveRow(self, data):
#             print "inherited!"
#             print data
            
     
    init_list =  [{ u"Name": u"stim_Frequency",u"DisplayName":  u"Frequency", u"ValueType": u"float", u"Unit": u"Hz", u"Value":0.},\
                 { u"Name": u"constVal",      u"DisplayName":  u"Value",     u"ValueType": u"int", u"Value":5},\
                 { u"Name": u"stim_Phrase",    u"DisplayName":  u"Phrase",     u"ValueType": u"unicode", u"Value":0.},\
                 { u"Name": u"constVal2",      u"DisplayName":  u"Value",     u"ValueType": u"bool", u"Value":True},\
                 { u"Name": u"stim_Frequency2",u"DisplayName":  u"Frequency", u"ValueType": u"bool", u"Value":False},\
                 { u"Name": u"stim_Phase2",    u"DisplayName":  u"Phase",     u"ValueType": u"bool", u"Value":False},\
                 { u"Name": u"colTest2",       u"DisplayName":  u"Farbe der Welt",     u"ValueType": u"color", u"Value":QtGui.QColor(u"white")},\
                 { u"Name": u"stim_Frequency3",u"DisplayName":  u"Frequency", u"ValueType": u"bool",  u"Value":False},\
                 { u"Name": u"stim_Phase3",    u"DisplayName":  u"Phase",     u"ValueType": u"float", u"Value":0.,u"Unit": u"Hz"},\
                 { u"Name": u"valSpin",       u"DisplayName":  u"Value from ComboBox", u"ValueType": u"comboBoxItem", \
                        u"Value": u"One", u"ValueList": [u"one", u"two", u"three"], u"Value": "two", u"Unit": "Wz"}
                 ]
    
    init_list2 = [{ u"Name": u"constVal",       u"DisplayName":  u"Value",     u"ValueType": u"bool", u"Value":True},\
                  { u"Name": u"stim_Frequency", u"DisplayName":  u"Frequency", u"ValueType": u"bool", u"Unit": u"Hz", u"Value":False},\
                  { u"Name": u"stim_Phase",     u"DisplayName":  u"Phase",     u"ValueType": u"bool", u"Value":False}]

    init_list3 = [{ u"Name": u"stim_Phase2",    u"DisplayName":  u"Phase",              u"ValueType": u"bool", u"Value":False},\
                  { u"Name": u"colTest2",       u"DisplayName":  u"Farbe der Welt",     u"ValueType": u"color", u"Value":QtGui.QColor(u"white")},\
                  { u"Name": u"stim_Frequency3",u"DisplayName":  u"Frequency",          u"ValueType": u"bool",  u"Value":False},\
                  { u"Name": u"stim_Phase3",    u"DisplayName":  u"Phase",              u"ValueType": u"float", u"Value":0.,u"Unit": u"Hz"},\
                  { u"Name": u"valSpin",        u"DisplayName":  u"Value from ComboBox",u"ValueType": u"comboBoxItem", \
                    u"Value": u"One",           u"ValueList": [u"one", u"two", u"three"],     u"Value": "two", u"Unit": "Wz"}]
    
    DataContainer1 = BContainer.BContainer("DataContainer1")
    DataContainer2 = BContainer.BContainer("DataContainer2")
    DataContainer3 = BContainer.BContainer("DataContainer3")
    DataContainer1.paste(DataContainer2)
    DataContainer1.paste(DataContainer3)
    
    configTable_root = ConfigTable(init_list3, u"Config root")
    configTable = ConfigTable(init_list, u"Config 1")
    configTable2 = ConfigTable(init_list2, u"Config 2")
    
    DataContainers = [DataContainer1, DataContainer2, DataContainer3]
    configTables   = [configTable_root, configTable, configTable2]
    for i in range(len(DataContainers)):
        DataContainers[i].paste(configTables[i])
        for _dict in configTables[i]:
            DataContainers[i].set(_dict[u"Name"], _dict[u"Value"])
        print DataContainers[i]
 
    app = QtGui.QApplication(sys.argv)
    mainWindow = PropertyEditorExample(DataContainer1)
    sys.exit(app.exec_())