'''
Created on 10.03.2016

@author: Waetzoold Plaum
'''

# This module implements the standard backend for the PyLinX Compiler. Frontend and Backend
# are seprarated since one can choose different backends for different purposes. The standard
# Backend implements code generation of PyLinX models with code output in Pyhton 2.7

import copy

from PyLinXData import BContainer

class PX_CG_PythonStd(BContainer.BContainer):

    _dictSetCallbacks = copy.copy(BContainer.BContainer._dictSetCallbacks)
    _dictGetCallbacks = copy.copy(BContainer.BContainer._dictGetCallbacks)

    
    def __init__(self, parent = None):
        super(PX_CG_PythonStd, self).__init__(parent, u"PX_CG_PythonStd")