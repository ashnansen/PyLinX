'''
Created on 09.08.2016

@author: Waetzold Plaum
'''
from PyQt4 import QtCore
import inspect
import copy

import PyLinXData
import PyLinXData.BContainer as BContainer 
import PyLinXData.PyLinXCoreDataObjects as PyLinXCoreDataObjects
import PyLinXData.PyLinXHelper as helper

class PyLinXController(PyLinXData.PyLinXCoreDataObjects.PX_IdObject):
    
    _dictSetCallbacks = copy.copy(PyLinXData.PyLinXCoreDataObjects.PX_IdObject._dictSetCallbacks)
    _dictGetCallbacks = copy.copy(PyLinXData.PyLinXCoreDataObjects.PX_IdObject._dictGetCallbacks)
    
    def __init__(self, root = None, mainWindow = None, bListActions = True, name = u"controller"):
        
        super(PyLinXController, self).__init__(None, name)
 
        self.__listCommands = []
        self.__mainWindow  = mainWindow
        self.__root = root
        self.__activeFolder = None
        self.__dictAlias = BContainer.BDict({}, name = u"dictAlias")
        self.paste(self.__dictAlias)
        self.set(u"LogLevel", 0)
        self.paste(BContainer.BDict({}, name="dictConstructors"))
        self._selection         = []
        
                
    ############
    # Properties
    ############

    def get_dictAlias(self):
        return self.__dictAlias
    
    dictAlias = property(get_dictAlias)


    def get_root(self):
        return self.__root 
        
    root = property(get_root)


    def get_activeFolder(self):
        return self.__activeFolder
    
    def set_activeFolder(self, activeFolder, options = None):
        self.__activeFolder = activeFolder
    
    activeFolder = property(get_activeFolder, set_activeFolder)
    
    def get_selection(self):
        return self._selection

    def set_selection(self, selection):
        self._selection = selection
        
    selection = property(get_selection, set_selection)    


    ###################
    # EXECUTE COMMANDS
    ###################
    
    def execScript(self, script, bResetID = True):
        if bResetID:
            PyLinXCoreDataObjects.PX_IdObject._PX_IdObject__ID = 0
        listScript = script.split("\n")
        for line in listScript:
            self.execCommand(line)



    ####################
    # Execute  commands
    ####################            
            
    def execCommand(self, command):
        
        if self.get(u"LogLevel") > 0:
            print  self.activeFolder.get__path() + "> " +  command
        
        # Tracking of the commands
        self._PyLinXController__listCommands.append(command)

        if (type(command) in [str,  unicode, QtCore.QString]):
            command = unicode(command)
            command = command.strip()
            command = command.split(" ")
        
        strCommand = command[0].strip()
        
        # Comments or white space lines
        if strCommand == u"":
            return
        if strCommand[0] == u'#':
            return
        
        # Determine target object if alias context is used
        context = self.activeFolder
        if strCommand == u"@selection":
            context = u"@selection"
            command = command[1:]
            strCommand = command[0].strip()            
        elif strCommand[0] == u"@":
            if strCommand in self.dictAlias:
                context = self.dictAlias[strCommand]
                command = command[1:]
                strCommand = command[0].strip()
            else:
                raise Exception("Error PyLiNXController.execCommand: \"" + strCommand  + "\" unknown Alias!")

        
        strExec = ""
        for i in range(1, len(command)):
            command_i = command[i]
            command_i_0 = command_i[0]
            
            # lists, sets, dicts, numeric
            if      (command_i_0 in (u"[", u"(", u"{")) or command_i.isnumeric()\
                    or (command_i   in (u"True", u"False")): 
                strExec += (u"command[" + unicode(i) + u"] = " + command[i] + u"\n")
            
            # other cases
            else:
                if u"\"" in command_i:
                    command[i] = command_i.replace(u"\"", u"\\\"")
                strExec += (u"command[" + unicode(i) + u"] = u\"" + command[i] + u"\"\n")

        exec(strExec)
        
        
        if strCommand == u"set":
            return self.__execCommand_set(context, command[1:])
        elif strCommand == u"del":
            return self.activeFolder.delete(command[1:])
        elif strCommand == u"new":
            return self.__execCommand_new(context, command[1:])
        elif strCommand == u"select":
            return self.__execCommand_select(command[1:])
        elif strCommand == u"cd":
            return self.__execCommand_cd(command[1:])


    ####################
    # GETTER and SETTER
    ####################
    
    # mainWindow
    ############
    def get__mainWindow(self):    
        return self.__mainWindow
    _dictGetCallbacks.addCallback(u"mainWindow", get__mainWindow)
    mainWindow = property(get__mainWindow)
   
    # listCommands
    ##############
    def get__listCommands(self):
        return self.__listCommands
    _dictGetCallbacks.addCallback(u"listCommands", get__listCommands)
    listCommands = property(get__listCommands)

    # listKeys
    ##########
    def get__Selection_listKeys(self):
        return [ val.get(u"Name") for val in self._selection ]
    _dictGetCallbacks.addCallback(u"Selection_listKeys", get__Selection_listKeys)
    
    def set_Selction_listKeys(self,attr, value):
        self.selection = value
    _dictSetCallbacks.addCallback(u"Selection_listKeys", set_Selction_listKeys)
    Selection_listKeys = property(get__Selection_listKeys, set_Selction_listKeys)

    # Selection_types
    #################
    def get__Selection_types(self):
        setTypes = set([])
        for element in self.selection:
            types = inspect.getmro(type(element))
            setTypes = setTypes.union(set(types))
        return setTypes
    _dictGetCallbacks.addCallback(u"Selection_types", get__Selection_types)
    Selection_types = property(get__Selection_types)
    
    ####################
    # SPECIFIC COMMANDS
    ####################              

    ##############
    # Command NEW
    ##############


    def __execCommand_new(self, context, listCommands):
               
        strType = listCommands[0]
        dictConstructors = self.getb("dictConstructors")
        _type = dictConstructors[strType]
        dictKWArgs = {}
        listArgs = [context]
        for command in listCommands[1:]:
            if type(command) in (unicode, str):
                if u"=" in command:
                    command = command.split(u"=")
                    exec(u"val = " + command[1]) in globals()
                    dictKWArgs[command[0]] = val
                else:
                    listArgs.append(command)
            else:
                listArgs.append(command)
        new_object =  context.new(_type, * tuple(listArgs), **dictKWArgs)
        return new_object
    
    
    #################
    # Command SELECT
    ################# 
    
    def __execCommand_select(self, command):
        
        self.selection = [self.activeFolder.getb(key) for key in command]
    
    
    ###############
    # Commande SET
    ###############
    
    def __execCommand_set(self, context, command):

        if context == u"@selection":
            return self.__execCommand_set_Selection(command)
        
        path = command[0]
        len_command = len(command)
        listPath = path.split(u".")
        len_listPath = len(listPath)
        bSubElement = (len_listPath > 1)    
        if bSubElement:
            if len_listPath >1:
                attr = listPath[-1]
                pathWithoutAttribute = path[0:len(path) - len(listPath[-1]) -1]
                element = context.getObjFromPath(pathWithoutAttribute)
                retObj =  element.set(attr, command[-1])
                return retObj 
        elif len_command ==2:
            return context.set(command[0], command[1])
        else:
            element = self.getObjFromPath(path)
            return  element.set(u"", command[1])
    
    # set selection
    ###############
       
    def __execCommand_set_Selection(self, command):
        for element in self.selection:
            if element.isAttr(command[0]):
                element.set(*tuple(command))
                
    
    #############
    # Command CD
    #############

    # Method to change the active folder
    def __execCommand_cd(self, path):
        try:
            obj = self.getObjFromPath(path)
        except Exception as exp:
            errorString = u"Error PyLinXProjectController,PyLinXProjectController.cd: Failed to open " + path + \
                     " - " + unicode(Exception) 
            helper.error(errorString)
            return 
        if obj == None:
            errorString = u"Error PyLinXProjectController,PyLinXProjectController.cd - " + unicode(Exception) 
            helper.error(errorString)
            return
        self.activeFolder = obj
        return    
    