'''
Created on 07.01.2015

@author: Waetzold Plaum
'''
import sys
from PyQt4 import QtGui

class EasyWidget(QtGui.QWidget):

    def __init__(self, init_list):
        
        super(EasyWidget,self).__init__()
        grid = QtGui.QGridLayout()
        counter = 0
        self.__dictLineEdit = {}
        self.__listInitData = init_list
        
        for valDict in init_list:
            
            keys        = valDict.keys()
            Name        = valDict["Name"]
            DisplayName = valDict["DisplayName"]
            Value       = valDict["Value"]
            label = QtGui.QLabel(DisplayName)
            grid.addWidget(label, counter, 0)
            lineEdit = QtGui.QLineEdit()
            lineEdit.setText(str(Value))
            grid.addWidget(lineEdit, counter, 1)
            self.__dictLineEdit[Name] = lineEdit 
            
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
            value       = self.__dictLineEdit[Name].text()
            try:
                if ValueType == "float":
                    value = float(value)
            except:
                pass
            retDict[Name] = value
        return retDict

        
if __name__ == "__main__":   
    
    app = QtGui.QApplication(sys.argv)
    
    init_list = [{ "Name": "constVal",        "DisplayName":  "Value",     "ValueType": "float"},\
                 { "Name": "stim_Frequency",  "DisplayName":  "Frequency", "ValueType": "float", "Unit": "Hz"},\
                 { "Name": "stim_Phase",      "DisplayName":  "Phase",     "ValueType": "float"}]
    easyWidget = EasyWidget(init_list)
    easyWidget.show()
    app.exec_()