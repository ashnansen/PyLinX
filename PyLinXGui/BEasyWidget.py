'''
Created on 07.01.2015

@author: Waetzold Plaum
'''
import sys
from PyQt4 import QtGui, QtCore

class EasyWidget(QtGui.QWidget):
    
    class DispOrder():
        NameValue = 0
        ValueName = 1

    def __init__(self, init_list, bValuesFirst = False):
        
        super(EasyWidget,self).__init__()
        grid = QtGui.QGridLayout()
        counter = 0
        self.__dictEditElements = {}
        self.__listInitData = init_list
        
        if bValuesFirst:
            idxEdit  = 0
            idxLabel = 1
        else:
            idxEdit  = 1
            idxLabel = 0

        for valDict in init_list:
            
            keys        = valDict.keys()
            Name        = valDict[u"Name"]
            DisplayName = valDict[u"DisplayName"]
            Value       = valDict[u"Value"]
            ValueType   = valDict[u"ValueType"]
            label = QtGui.QLabel(DisplayName)
            if ValueType == u"bool":
                editElement = QtGui.QCheckBox()
                if Value == True:
                    checkState = QtCore.Qt.Checked
                elif Value == False:
                    checkState = QtCore.Qt.Unchecked
                else:
                    checkState = QtCore.Qt.PartiallyChecked
                editElement.setCheckState(checkState)
            else:
                editElement = QtGui.QLineEdit()
                editElement.setText(str(Value))

            grid.addWidget(editElement, counter, idxEdit)
            grid.addWidget(label, counter, idxLabel)
            grid.setColumnStretch(idxLabel,1)
            
            self.__dictEditElements[Name] = editElement 
            
            if u"Unit" in keys:
                Unit  = valDict[u"Unit"]
                label = QtGui.QLabel(u"["+Unit+u"]")
                grid.addWidget(label, counter, 2)
            counter += 1
        
        self.setLayout(grid)
        
    def getValues(self):
        
        retDict = {}
        
        for valDict in self.__listInitData:
            Name        = valDict[u"Name"]
            ValueType   = valDict[u"ValueType"]
            if ValueType == u"bool":
                value       = self.__dictEditElements[Name].checkState()
            else:
                value       = self.__dictEditElements[Name].text()
            ValueType   = valDict[u"ValueType"]
            try:
                if ValueType == u"float":
                    value = float(value)
                elif ValueType == u"bool":
                    if value == QtCore.Qt.Checked:
                        value = True
                    elif value == QtCore.Qt.Unchecked:
                        value = False
                    else:
                        value = None
            except:
                pass
            retDict[Name] = value
        return retDict

        
if __name__ == u"__main__":
        
    app = QtGui.QApplication(sys.argv)
    
    init_list = [{ u"Name": u"constVal",        u"DisplayName":  u"Value",     u"ValueType": u"float", u"Value":0},\
                 { u"Name": u"stim_Frequency",  u"DisplayName":  u"Frequency", u"ValueType": u"float", u"Unit": u"Hz", u"Value":0},\
                 { u"Name": u"stim_Phase",      u"DisplayName":  u"Phase",     u"ValueType": u"float", u"Value":0}]
    init_list2 = [{ u"Name": u"constVal",       u"DisplayName":  u"Value",     u"ValueType": u"bool", u"Value":True},\
                 {  u"Name": u"stim_Frequency",  u"DisplayName":  u"Frequency", u"ValueType": u"bool", u"Unit": u"Hz", u"Value":False},\
                 {  u"Name": u"stim_Phase",      u"DisplayName":  u"Phase",     u"ValueType": u"bool", u"Value":False}]
    easyWidget = EasyWidget(init_list, False)
    easyWidget.show()
    app.exec_()