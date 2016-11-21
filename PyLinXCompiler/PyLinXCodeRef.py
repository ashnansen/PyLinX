'''
Created on 02.09.2015

@author: Waetzold Plaum
'''
import copy

from PyLinXData import PyLinXCoreDataObjects
import PyLinXRunEngine 

################################################
# internal classes used for code-generation
# they should "know" all the global information
# of the run-engine
################################################

class PX_CodeRefObject(PyLinXCoreDataObjects.PX_IdObject):
    
    '''
    classdocs
    '''
    _dictSetCallbacks = copy.copy(PyLinXCoreDataObjects.PX_IdObject._dictSetCallbacks)
    _dictGetCallbacks = copy.copy(PyLinXCoreDataObjects.PX_IdObject._dictGetCallbacks)

    def __init__(self, parent, refObj):
        '''
        Constructor
        '''
        name = refObj.get(u"Name") + u"_REF"
        super(PX_CodeRefObject, self).__init__(parent, name)
        self._BContainer__Head = refObj
        
        
    def get_ref(self):
        return self._BContainer__Head
    
    ref = property(get_ref)
        

class PX_CodableBasicOperator(PX_CodeRefObject):
    
    _dictSetCallbacks = copy.copy(PX_CodeRefObject._dictSetCallbacks)
    _dictGetCallbacks = copy.copy(PX_CodeRefObject._dictGetCallbacks)
    
    def __init__(self,parent, knot, CodingVariant, orderConnection):
        super(PX_CodableBasicOperator, self).__init__(parent, knot)
        self.__orderConnection = orderConnection
        
    def getCode(self,Code):
        lenBody = len(self._BContainer__Body)
        if lenBody != 2:
            print "TODO: Error-Handling (2)"
        else:
            keys = self.getChildKeys()
            objs = [self.getb(key).get_ref() for key in keys]
            variables = {}
            variables[self.__orderConnection[objs[0].ID]] = self.getb(keys[0]).getCode(Code)
            variables[self.__orderConnection[objs[1].ID]] = self.getb(keys[1]).getCode(Code)
            operator = self.ref._BContainer__Head
            return u"( " + variables[-1] + u" " + operator + u" " + variables[-2] + u" ) "


class PX_CodableVarElement(PX_CodeRefObject):
            
    _dictSetCallbacks = copy.copy(PX_CodeRefObject._dictSetCallbacks)
    _dictGetCallbacks = copy.copy(PX_CodeRefObject._dictGetCallbacks)
    
    def __init__(self,parent, knot, CodingVariant):
        super(PX_CodableVarElement, self).__init__(parent, knot)
        self.CodingVariant = CodingVariant
        
    def getCode(self, Code):

        lenBody = len(self._BContainer__Body)
        name = self.ref.get(u"DisplayName") 
        if lenBody == 1:
            _input = self.getb(self.getChildKeys()[0])
            if self.CodingVariant == PyLinXRunEngine.PX_CodeAnalyser.CodingVariant.ReadSingleVars: 
                code_to_add = name + u" = " + _input.getCode(Code)
            elif self.CodingVariant == PyLinXRunEngine.PX_CodeAnalyser.CodingVariant.ReadVarsFromDataDict:
                code_to_add = u"DataDictionary[u\"" + name + u"\"]" + u" = " + _input.getCode(Code)
            Code.appendLine(code_to_add)
        if self.CodingVariant == PyLinXRunEngine.PX_CodeAnalyser.CodingVariant.ReadSingleVars: 
            return name
        elif self.CodingVariant == PyLinXRunEngine.PX_CodeAnalyser.CodingVariant.ReadVarsFromDataDict:
            return u"DataDictionary[u\"" + name + u"\"]"
        