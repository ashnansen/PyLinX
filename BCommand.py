'''
Created on 26.05.2014

@author: Waetzold Plaum
'''
import string

class BCommand:
    
    com_set         =  1
    com_get         =  2
    com_getCond     =  3
    com_getRoot     =  4
    com_paste       =  5
    com_write       =  6
    com_getb        =  7
    com_move        =  8
    com_del         =  9
    com_is          = 10
    com_add         = 11
    com_cut         = 12
    com_copy        = 13
    com_deepcopy    = 14
    com_print       = 15
    
    
    __idxCountIdGlobal = 0
    __instanceGlobal = None
    #__listInstances = ["view", "mon", "log", "ctl", "sync", "relDB", "objDB"]
    __dictProtocol  = { "set"        :  com_set,
                        "get"        :  com_get,
                        "getCond"    :  com_getCond,
                        "getRoot"    :  com_getRoot,
                        "paste"      :  com_paste,
                        "write"      :  com_write,
                        "getb"       :  com_getb,
                        "move"       :  com_move,
                        "del"        :  com_del,
                        "is"         :  com_is,
                        "add"        :  com_add,
                        "cut"        :  com_cut,
                        "copy"       :  com_copy,
                        "deepcopy"   :  com_deepcopy,
                        "print"      :  com_print }

    def __init__(self, initObject=None, idCom = None,  instance = None):

#         if instance != None:
#             if instance in BCommand.__listInstances:
#                 BCommand.__instanceGlobal = instance
             
        
        if idCom == None:
            self.__idxCountId   = BCommand.__idxCountIdGlobal
        else:
            if isinstance(idCom, int):
                if idCom > 0:
                    self.__idxCountId = idCom
        
        self.__constrInitObject = initObject
        self.__constrInstance   = instance
        self.__constrIdCom      = idCom 
        self.__instance         = BCommand.__instanceGlobal
        self.__com              = None
        self.__listStr          = []
        self.__destination      = ""
        
        # TODO: Some mechanism to prevent overflow
        if idCom == None:
            BCommand.__idxCountIdGlobal += 1
        
        if isinstance(initObject, str) or isinstance(initObject, unicode):
            initObject          = string.strip(initObject)
            self.__listStr      = string.split(initObject)
            len_listStr = len(self.__listStr)
            if len_listStr > 0:
                listStr_0 = self.__listStr[0]
                if len(listStr_0) > 0:
                    # first Argument with peficed "@" describes a specific destination of the command
                    if listStr_0[0] == "@":
                        self.__destination = listStr_0[1:]
                        if len_listStr > 1:
                            listStr_0 = self.__listStr[1]
                    if listStr_0 in BCommand.__dictProtocol.keys():
                        self.__com = BCommand.__dictProtocol[listStr_0]    
                    else:
                        self.__com = 0
        #print "self.__com: ", self.__com

    def getArgV(self):
        # If the command is identified by the corresponding enumeration then the command string is redundant otherwise it should be 
        # transbitted
        if self.__com > 0:
            return self.__listStr[1:]
        else:
            return self.__listStr
        
    argv = property(getArgV)

    def getCom(self):
        return self.__com
    
    com = property(getCom)
                
    def getId(self):
        return self.__idxCountId 
    
    id = property(getId)
    
    def getInstance(self):
        return self.__instance
     
    instance = property(getInstance)

    def __repr__(self):
        if self.__constrIdCom == None:
            retStr = "BCommand(initObject="+ repr(self.__constrInitObject)+",instance="\
                            + repr(self.__instance)+",idCom="+ repr(self.__idxCountId) +")"
        else:
            retStr = "BCommand(initObject="+ repr(self.__constrInitObject)+",instance="\
                            + repr(self.__instance)+",idCom="+ repr(self.__constrIdCom)+")" 
        return retStr 

if __name__ == "__main__":    
    com1 = BCommand(instance="view")
    for i in range(10):
        print "------------------"
        com = BCommand("get attr")
        print com.id
        print com.argv
        print com.com
        execStr = "com2 = " + repr(com)
        exec(execStr)
        print com2.id
        print com2.argv
        print com2.com
        