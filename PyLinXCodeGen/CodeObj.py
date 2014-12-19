'''
Created on 19.12.2014

@author: Waetzold Plaum
'''

from PyLinXData import *


# class PX_CodeRefObject(PyLinXDataObjects.PX_IdObject):
#     '''
#     classdocs
#     '''
# 
# 
#     def __init__(self, refObj):
#         '''
#         Constructor
#         '''
#         name = refObj.get("Name") + "_REF"
#         super(PX_CodeRefObject, self).__init__(name)
#         self._BContainer__Head = refObj
#         
#         
#     def get_ref(self):
#         return self._BContainer__Head
#     
#     ref = property(get_ref)
# 
# 
# 
# class PX_CodableObject(PX_CodeRefObject):
#     
#     def __init__(self,*param):
#         super(PX_CodableObject, self).__init__(*param)
#         
# 
# class PX_CodableBasicOperator(PX_CodableObject):
#     
#     def __init__(self,*param):
#         super(PX_CodableBasicOperator, self).__init__(*param)
#         
#     def isSaturated(self):
#         pass
#           
# class PX_CodableVarElement(PX_CodableObject):
#         
#     def __init__(self,*param):
#         super(PX_CodableVarElement, self).__init__(*param)
#         
#     def isSaturated(self):
#         pass