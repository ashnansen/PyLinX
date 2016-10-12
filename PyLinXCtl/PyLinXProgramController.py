'''
Created on 29.08.2016

@author: Waetzold Plaum
'''
import copy

import PyLinXController

class PyLinXProgramController(PyLinXController.PyLinXController):
    
    _dictSetCallbacks = copy.copy(PyLinXController.PyLinXController._dictSetCallbacks)
    
    def __init__(self, mainWindow = None, bListActions = False):
        
        # Programm Controller should be known to all objects.This mnechanism has to be changed if the 
        # PyLinX should get capable of multisession. Then the "paste" method should set the correponding Programm 
        # Controller.

        super(PyLinXProgramController, self).__init__(None, mainWindow, bListActions, u"ProgramController")
        
        self.__project = None
        
    def get_project(self):
        return self.__project
    
    def set_project (self,project):
        oldProject = self.__project
        self.__project = project
        del oldProject
        
    project = property(get_project, set_project)
        
    