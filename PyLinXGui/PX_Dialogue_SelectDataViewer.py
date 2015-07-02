'''
Created on 11.03.2015

@author: wplaum
'''
import copy
from PyQt4 import QtGui, QtCore

from PyLinXData import * 
import PX_Templates as PX_Templ
1
class PX_Dialogue_SelectDataViewer(QtGui.QDialog):
    
    def __init__(self, parent, variable, rootContainer, drawWidget):
         
        super(PX_Dialogue_SelectDataViewer, self).__init__(parent)
        
        self.rootContainer = rootContainer
        listSelectedDispObj = variable.get(u"listSelectedDispObj")
        layout = QtGui.QVBoxLayout(self)
        listDataDispObj = rootContainer.get(u"listDataDispObj")
        listSelectionDisp = list(set(listDataDispObj).intersection(set(listSelectedDispObj)))
        if len(listSelectionDisp ) > 0:
            listSelectionDisp.sort()
            
        idxLastSelectedDataViewer = self.rootContainer.get(u"idxLastSelectedDataViewer")
        print "idxLastSelectedDataViewer: ", idxLastSelectedDataViewer
        
        init_list = []
        for item in listDataDispObj:
            print "item: ", item
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
        print u"values: ", values
        listSelectedDispObj_new = []
        #idx = None
        idx = self.rootContainer.get(u"idxLastSelectedDataViewer")
        listSelectedDispObj = self.variable.get(u"listSelectedDispObj")
        
        #print u"values: ", values
        for key in values:
            #print u"key: ", key
            if u"bDataViewer_" in key:
                if values[key]:
                    listSelectedDispObj_new.append(int(key[12:]))
        self.variable.set(u"listSelectedDispObj", listSelectedDispObj_new)
        print u"listSelectedDispObj: ", listSelectedDispObj
        
        #idx = -1
        if values[u"bNewDataViewer"]:
            newVarDispObj = PyLinXDataObjects.PX_PlottableVarDispElement(50,50, self.rootContainer)
            self.drawWidget.activeGraphics.paste(newVarDispObj, bHashById=True)
            self.variable._BContainer__Attributes[u"bNewDataViewer"] = True
            idx = newVarDispObj.get(u"idxDataDispObj")
            listSelectedDispObj_new.append(idx)
            self.variable.set(u"listSelectedDispObj", listSelectedDispObj_new)            
            
        else:
            self.variable._BContainer__Attributes[u"bNewDataViewer"] = False
            
        
        name = self.variable.get(u"Name")
        rootGraphics = self.rootContainer.getb(u"rootGraphics")
        #listSelectedDispObj
        print u"labelAdd (1)  name: ", name, u"  listSelectedDispObj: ", listSelectedDispObj
        #rootGraphics.recur(type(self), u"labelAdd", (name, listSelectedDispObj))
        rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"labelAdd", (name, listSelectedDispObj_new))
        
        # delete the elements, that are in the old list but not in the new
        list_del = list( set(listSelectedDispObj).difference(set(listSelectedDispObj_new)))
        rootGraphics.recur(PyLinXDataObjects.PX_PlottableVarDispElement, u"labelRemove", (name, list_del))
        
        self.rootContainer.set(u"idxLastSelectedDataViewer", idx )
        
        self.hide()
        
    @staticmethod
    def getParams(parent, variable, rootContainer,  drawWidget):
        dialog = PX_Dialogue_SelectDataViewer(parent, variable, rootContainer,  drawWidget)
        result = dialog.exec_()
        drawWidget.repaint() 
        return dialog.result
        #return result                        
        
        