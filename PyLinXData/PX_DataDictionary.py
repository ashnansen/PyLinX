'''
Created on 16.02.2016

@author: Waetzold Plaum
'''

from PyLinXData.BContainer import BDict

class PX_DataDictionary(BDict):

    def __init__(self, parent):
        
        super(PX_DataDictionary, self).__init__({})
        self.set(u"Name", u"DataDictionary")
        self.set(u"DisplayName", u"DataDictionary")
        parent.paste(self)