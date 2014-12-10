'''
Created on 19.05.2014

@author: Waetzold Plaum
'''
from   PyQt4 import QtGui
import inspect
import string

def error(strErrorMessage):
    msgBox = QtGui.QMessageBox()
    msgBox.setIcon(QtGui.QMessageBox.Critical)
    msgBox.setText(strErrorMessage)
    msgBox.addButton(QtGui.QPushButton('OK'), QtGui.QMessageBox.YesRole)
    msgBox.setWindowTitle("Fehler")
    msgBox.exec_()
    
def checkType(obj, _type):
    types = inspect.getmro(type(obj))
    return _type in types

def getAttributeAndValue(stri):
    listStri = string.split(stri)
    if len(listStri) == 0:
        return None
    else:
        return listStri[0], listStri[2]