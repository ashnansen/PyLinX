'''
Created on 11.03.2015

@author: wplaum
'''
import copy
from PyQt4 import QtGui, QtCore

from PyLinXData import * 
import PX_Templates as PX_Templ

class PX_Dialogue_SelectDataViewer(QtGui.QDialog):
    
    def __init__(self, parent, variable, rootContainer, drawWidget):
         
        super(PX_Dialogue_SelectDataViewer, self).__init__(parent)
        
        listSelectedDispObj = variable.get("listSelectedDispObj")
        layout = QtGui.QVBoxLayout(self)
        listDataDispObj = rootContainer.get("listDataDispObj")
        listSelectionDisp = list(set(listDataDispObj).intersection(set(listSelectedDispObj)))
        if len(listSelectionDisp ) > 0:
            listSelectionDisp.sort()
        
        init_list = []
        for item in listDataDispObj:
            dict_cache = {}
            dict_cache["Name"] = "bDataViewer_" + str(item)
            dict_cache["DisplayName"] = "data viewer " + str(item)
            dict_cache["ValueType"] = "bool"
            if item in listSelectionDisp:
                value = True
            else:
                value = False
            dict_cache["Value"] = value
            init_list.append(dict_cache)
      

        dict_cache = {}
        dict_cache["Name"] = "bNewDataViewer"
        dict_cache["DisplayName"] = "New data viewer"
        dict_cache["ValueType"] = "bool"

        if len(listSelectionDisp ) == 0:
            dict_cache["Value"] = True
        else:
            dict_cache["Value"] = False
            
        init_list.append(dict_cache)

        
        self.setLayout(layout)
        self.drawWidget = drawWidget
        self.variable = variable
        self.rootContainer = rootContainer
        
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
        for key in values:
            if "bDataViewer_" in key:
                if values[key]:
                    listSelectedDispObj_new.append(int(key[12:]))
        self.variable.set("listSelectedDispObj", listSelectedDispObj_new)
        if values["bNewDataViewer"]:
            newVarDispObj = PyLinXDataObjects.PX_PlottableVarDispElement(50,50, self.rootContainer)
            self.drawWidget.activeGraphics.paste(newVarDispObj, bHashById=True)
            self.variable._BContainer__Attributes["bNewDataViewer"] = True
            idx = newVarDispObj.get("idxDataDispObj")
            listSelectedDispObj = self.variable.get("listSelectedDispObj")
            listSelectedDispObj.append(idx)
            
#                             #newVarDispObj = PyLinXDataObjects.PX_PlottableVarDispElement(50,50, self.rootContainer)
#                             idx = newVarDispObj.get("idxDataDispObj")
#                             listSelectedDispObj = var.get("listSelectedDispObj")
#                             print "listSelectedDispObj (0): ", listSelectedDispObj
#                             listSelectedDispObj.append(idx)
#                             print "listSelectedDispObj (1): ", listSelectedDispObj
#                             var.set("listSelectedDispObj", listSelectedDispObj)
#                             self.activeGraphics.paste(newVarDispObj, bHashById=True)

            
            
            
        else:
            self.variable._BContainer__Attributes["bNewDataViewer"] = False
        #self.variable._BContainer__Attributes.update(values)
        self.hide()
        
    @staticmethod
    def getParams(parent, variable, rootContainer,  drawWidget):
        dialog = PX_Dialogue_SelectDataViewer(parent, variable, rootContainer,  drawWidget)
        result = dialog.exec_()
        drawWidget.repaint() 
        return dialog.result                        
        
        