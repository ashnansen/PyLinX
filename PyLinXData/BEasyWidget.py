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
            Name        = valDict["Name"]
            DisplayName = valDict["DisplayName"]
            Value       = valDict["Value"]
            ValueType   = valDict["ValueType"]
            label = QtGui.QLabel(DisplayName)
            if ValueType == "bool":
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
            
            if "Unit" in keys:
                Unit  = valDict["Unit"]
                label = QtGui.QLabel("["+Unit+"]")
                grid.addWidget(label, counter, 2)
            counter += 1
        
        self.setLayout(grid)
        
    def getValues(self):
        
        retDict = {}
        
        for valDict in self.__listInitData:
            Name        = valDict["Name"]
            ValueType   = valDict["ValueType"]
            if ValueType == "bool":
                value       = self.__dictEditElements[Name].checkState()
            else:
                value       = self.__dictEditElements[Name].text()
            ValueType   = valDict["ValueType"]
            try:
                if ValueType == "float":
                    value = float(value)
                elif ValueType == "bool":
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

        
if __name__ == "__main__":   
    
    app = QtGui.QApplication(sys.argv)
    
    init_list = [{ "Name": "constVal",        "DisplayName":  "Value",     "ValueType": "float", "Value":0},\
                 { "Name": "stim_Frequency",  "DisplayName":  "Frequency", "ValueType": "float", "Unit": "Hz", "Value":0},\
                 { "Name": "stim_Phase",      "DisplayName":  "Phase",     "ValueType": "float", "Value":0}]
    init_list2 = [{ "Name": "constVal",       "DisplayName":  "Value",     "ValueType": "bool", "Value":True},\
                 {  "Name": "stim_Frequency",  "DisplayName":  "Frequency", "ValueType": "bool", "Unit": "Hz", "Value":False},\
                 {  "Name": "stim_Phase",      "DisplayName":  "Phase",     "ValueType": "bool", "Value":False}]
    easyWidget = EasyWidget(init_list, False)
    easyWidget.show()
    app.exec_()