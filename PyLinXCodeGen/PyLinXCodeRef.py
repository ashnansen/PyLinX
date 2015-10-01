'''
Created on 02.09.2015

@author: Waetzold Plaum
'''

from PyLinXData import PyLinXDataObjects

################################################
# internal classes used for code-generation
# they should "know" all the global information
# of the run-engine
################################################

class PX_CodeRefObject(PyLinXDataObjects.PX_IdObject):
    '''
    classdocs
    '''

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
    
    def __init__(self,*param):
        super(PX_CodableBasicOperator, self).__init__(*param)
        
    def getCode(self,Code):
        lenBody = len(self._BContainer__Body)
        if lenBody != 2:
            print "TODO: Error-Handling (2)"
        else:
            keys = self.getChildKeys()
            keys.sort()
            operator = self.ref._BContainer__Head
            var0 = self.getb(keys[0]).getCode(Code)
            var1 = self.getb(keys[1]).getCode(Code) 
            return u"( " + var0 + u" " + operator + u" " + var1 + u" ) "


class PX_CodableVarElement(PX_CodeRefObject):
        
    def __init__(self,*param):
        super(PX_CodableVarElement, self).__init__(*param)
        
    def getCode(self, Code):

        lenBody = len(self._BContainer__Body)
        name = self.ref.get(u"Name") 
        if lenBody == 1:
            input = self.getb(self.getChildKeys()[0])
            code_to_add = name + u" = " + input.getCode(Code)
            #print "APPEND!"
            Code.appendLine(code_to_add)
        return name