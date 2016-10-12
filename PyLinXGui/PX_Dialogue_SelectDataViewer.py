'''
Created on 11.03.2015

@author: Waetzold Plaum
'''
import copy
from PyQt4 import QtGui, QtCore

# from PyLinXData import BContainer, PyLinXCoreDataObjects, \
#            PyLinXHelper,PX_Signals,PX_DataDictionary
import PX_Templates as PX_Templ
from PyLinXGui import BEasyWidget

class PX_Dialogue_SelectDataViewer(QtGui.QDialog):
    
    def __init__(self, parent, variable, mainController, drawWidget):
         
        super(PX_Dialogue_SelectDataViewer, self).__init__(parent)
        
        self.mainController = mainController
        listSelectedDispObj = variable.get(u"listSelectedDispObj")
        layout = QtGui.QVBoxLayout(self)
        listDataDispObj = mainController.get(u"listDataDispObj")
        listSelectionDisp = list(set(listDataDispObj).intersection(set(listSelectedDispObj)))
        if len(listSelectionDisp ) > 0:
            listSelectionDisp.sort()
            
        idxLastSelectedDataViewer = self.mainController.get(u"idxLastSelectedDataViewer")
        
        init_list = []
        for item in listDataDispObj:
            dict_cache = {}
            dict_cache[u"Name"] = u"bDataViewer_" + str(item)
            dict_cache[u"DisplayName"] = u"data viewer " + str(item)
            dict_cache[u"ValueType"] = u"bool"
            if item in listSelectionDisp or \
                            ((item == idxLastSelectedDataViewer) and len(listSelectionDisp)== 0):
                value = True
            else:
                value = False
            dict_cache[u"Value"] = value
            init_list.append(dict_cache)
      

        dict_cache = {}
        dict_cache[u"Name"] = u"bNewDataViewer"
        dict_cache[u"DisplayName"] = u"New data viewer"
        dict_cache[u"ValueType"] = u"bool"

        if len(listSelectionDisp ) == 0 and idxLastSelectedDataViewer < 0:
            dict_cache[u"Value"] = True
        else:
            dict_cache[u"Value"] = False
            
        init_list.append(dict_cache)

        
        self.setLayout(layout)
        self.drawWidget = drawWidget
        self.variable = variable
        easyWidget          = BEasyWidget.EasyWidget(init_list, True)
        self.layout().addWidget(easyWidget)
        self.formWidget     = easyWidget

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.on_accept)
        self.buttons.rejected.connect(self.on_reject)
        self.layout().addWidget(self.buttons)
        self.result = False
        
    def on_reject(self):
        self.hide()
        
    def on_accept(self):
        
        self.result = True
        values = self.formWidget.getValues()
        listSelectedDispObj_new = []
        idx = self.mainController.get(u"idxLastSelectedDataViewer")
        listSelectedDispObj = self.variable.get(u"listSelectedDispObj")
        
        for key in values:
            if u"bDataViewer_" in key:
                if values[key]:
                    listSelectedDispObj_new.append(int(key[12:]))
        
        if values[u"bNewDataViewer"]:
            execStr = u"new dataViewer 50 50"
            newVarDispObj = self.mainController.execCommand(execStr)
            idx = newVarDispObj.get(u"idxDataDispObj")
            listSelectedDispObj_new.append(idx)
      
        execStr = u"set " + self.variable.objPath[:-1] + u".listSelectedDispObj " +\
                unicode(repr(listSelectedDispObj_new).replace(u" ", u""))                  
        self.mainController.execCommand(execStr)

        self.mainController.set(u"idxLastSelectedDataViewer", idx)
        self.hide()
        
    @staticmethod
    def getParams(parent, variable, mainController,  drawWidget):
        dialog = PX_Dialogue_SelectDataViewer(parent, variable, mainController,  drawWidget)
        result = dialog.exec_()
        drawWidget.repaint() 
        return dialog.result
        