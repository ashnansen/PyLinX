'''
Created on 18.02.2016

@author: Waetzold Plaum
'''

import numpy
import math

import BContainer
import PyLinXCtl
import PyLinXCoreDataObjects


# The object handler handles the problem that each variable, class pp. may occur several times in the code. 

class PX_ObjectHandler(PyLinXCoreDataObjects.PX_Object):
    
    def __init__(self, parent):
        if not (type(parent) == PyLinXCtl.PyLinXMainController.PyLinXMainController):
            raise Exception("Error PX_ObjectHandler.__init__: Invalid Type of MainController")
        super(PX_ObjectHandler, self).__init__(parent, u"ObjectHandler")
        self.set(u"bObjectInSimulationMode", False)
        self._BContainer__AttributesVirtual.extend([u"listObjects", u"mapping"])
    
    def register(self, variable):
        
        varName = variable.get(u"DisplayName")

        #  Attributes with the prefix "var." correspond to variables of the models

        if (varName in self._BContainer__Body):
            self._BContainer__Attributes[u"Var." + varName] += 1
            objectVar = self._BContainer__Body[varName]
            objectVar.get(u"listRefInstances").append(variable) 
        else:
            objectVar = PX_ObjectVariable(self, variable)
            self._BContainer__Attributes[u"Var." + varName] = 1
        
        return objectVar
        
        
    def unregister(self, varName):
        print "HAS TO BE IMPLEMENTED! unregister()"
    
    def runInit(self):
        for variable in self.getChildKeys():
            obj = self.getb(variable)
            obj.runInit()
    
    def updateDataDictionary(self):
        for variable in self.getChildKeys():
            obj = self.getb(variable)
            obj.updateDataDictionary()        
    
    def get(self, attr):
        
        if attr == u"listObjects":
            return self._BContainer__Body.keys()
        if attr == u"mapping":
            return self.__get_mapping()
        else:
            return super(PX_ObjectHandler, self).get(attr)
    
    def __get_mapping(self):
        mapping = {}
        for key in self.getChildKeys():
            element = self.getb(key) 
            nameSignal= element.get(u"signalMapped")
            if nameSignal!= None:
                nameVariable = element.get(u"Name")
                mapping[nameVariable] = nameSignal
        return mapping
    
    def set(self, attr, obj, options = None):
        
        if attr == u"mapping":
            return self.set_mapping(obj)
        else:
            return super (PX_ObjectHandler, self).set(attr, obj, options = None)
        
    def set_mapping(self, mapping):
        keys = self.getChildKeys()
        for variable in mapping:
            if variable in keys:
                varObject = self.getb(variable)
                varObject.set(u"signalMapped", mapping[variable])
        return
    
class PX_ObjectVariable(PyLinXCoreDataObjects.PX_Object):

    def __init__(self, parent, variable):
        
        name = variable.get(u"DisplayName")
        super(PX_ObjectVariable, self).__init__(parent, name)
        self._BContainer__Attributes[u"listRefInstances"] = [variable]
        self.__refVariable = variable
        self.__mainController = self.getRoot()
        self.__signalhandler = self.__mainController.getb(u"signalFiles")
        self.__DataDictionary = self.__mainController.getb(u"DataDictionary")
        
        self.set(u"StimulationFunction", None)
        self.set(u"listSelectedDispObj", [])
        self.set(u"stim_const_val", 0.)
        self.__time = None
        self.__signal = None
        self.__iteratorSignal = None
        self.__RunConfigDictionary = None
        self.__stimulateBySignal = False
        self.__lenSignal = None 
        
        self.__stimFuntion = self.updateDataDictionary_const_val
        
        
        # Initializing the special parameters for the stimulation
        #########################################################
        
        self.__stim_const_val = 0.
        self.__stim_sine_frequency = 0.
        self.__stim_sine_offset = 0.
        self.__stim_sine_amplitude = 0.
        self.__stim_ramp_frequency = 0.
        self.__stim_ramp_phase = 0.
        self.__stim_ramp_offset = 0.
        self.__stim_ramp_amplitude = 0.
        self.__stim_pulse_frequency = 0.
        self.__stim_pulse_phase = 0.
        self.__stim_pulse_amplitude = 0.
        self.__stim_pulse_offset = 0.
        self.__stim_step_phase = 0.
        self.__stim_step_offset = 0.
        self.__stim_step_amplitude = 0.
        self.__stim_random_offset = 0.
        self.__stim_random_amplitude = 0.
        

    #########################
    # GET and SET-Funcitons
    #########################    
    
    def get(self, attr):
     
        if attr == u"bMeasure":
            listSelectedDispObj = self.get(u"listSelectedDispObj")
            if len(listSelectedDispObj) > 0:
                return True
            return False
        elif attr == u"objPath":
            objPath = super(PX_ObjectVariable, self).get(u"path")
            return objPath
        elif attr == u"bStimulate":
#             bStimulate = (self.get(u"StimulationFunction") != None)
#             print "StimulationFunction", self.get(u"StimulationFunction")
#             print bStimulate
#             return bStimulate
            return (self.get(u"StimulationFunction") != None)
        elif attr == u"signalMapped":
            StimulationFunction = self.get(u"StimulationFunction")
            if StimulationFunction != None:
                if "Signal_" in StimulationFunction:
                    return StimulationFunction
            return None
        else:
            return super(PX_ObjectVariable, self).get(attr)     
         
    def set(self, attr, value, options = None):
        
        if attr == u"bMeasure":
            raise Exception(u"Error PX_ObjectVariable.set - Attribute \"bMeasure\" is read only")
        elif attr == u"listSelectedDispObj":    
            if not u"listSelectedDispObj" in self._BContainer__Attributes:
                self._BContainer__Attributes[u"listSelectedDispObj"] = []
            name = self.get(u"Name")
            rootGraphics = self.mainController.getb(u"rootGraphics")
            rootGraphics.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, \
                               u"labelAdd", (name, value))
            # delete the elements, that are in the old list but not in the new
            listSelectedDispObj = self.get(u"listSelectedDispObj")
            list_del = list( set(listSelectedDispObj).difference(set(value)))            
            rootGraphics.recur(PyLinXCoreDataObjects.PX_PlottableVarDispElement, \
                               u"labelRemove", (name, list_del))
        elif attr == u"signalMapped":
            if value == 0:
                return super(PX_ObjectVariable, self).set(u"StimulationFunction", None)
            else:
                return super(PX_ObjectVariable, self).set(u"StimulationFunction", value)
            
                 
        super(PX_ObjectVariable, self).set(attr, value, options)        


    ###################################
    # METHODS USED DURING SIMULATION       
    ###################################
        
    def runInit(self):
        
        self.__RunConfigDictionary = self.__mainController .getb(u"RunConfigDictionary")
        self.__StimulationFunction = self.get(u"StimulationFunction")
        signalMapped = self.get(u"signalMapped") 


        StimulationFunction = self.get(u"StimulationFunction")
        if StimulationFunction == u"Constant":
            self.__stimFuntion = self.updateDataDictionary_const_val
        elif StimulationFunction == u"Sine":
            self.__stim_sine_frequency = self.get(u"stim_sine_frequency")  
            self.__stim_sine_offset = self.get(u"stim_sine_offset")     
            self.__stim_sine_amplitude = self.get(u"stim_sine_amplitude")            
            self.__stimFuntion = self.updateDataDictionary_stim_sine
        elif StimulationFunction == u"Ramp":
            self.__stim_ramp_frequency = self.get(u"stim_ramp_frequency")
            self.__stim_ramp_phase = self.get(u"stim_ramp_phase")
            self.__stim_ramp_offset = self.get(u"stim_ramp_offset")
            self.__stim_ramp_amplitude = self.get(u"stim_ramp_amplitude")                
            self.__stimFuntion = self.updateDataDictionary_stim_ramp
        elif StimulationFunction == u"Pulse":
            self.__stim_pulse_frequency = self.get(u"stim_pulse_frequency")
            self.__stim_pulse_phase = self.get(u"stim_pulse_phase")
            self.__stim_pulse_amplitude = self.get(u"stim_pulse_amplitude")
            self.__stim_pulse_offset = self.get(u"stim_pulse_offset")            
            self.__stimFuntion = self.updateDataDictionary_stim_pulse
        elif StimulationFunction ==  u"Step":
            self.__stim_step_phase = self.get(u"stim_step_phase")
            self.__stim_step_offset = self.get(u"stim_step_offset")
            self.__stim_step_amplitude = self.get(u"stim_step_amplitude")            
            self.__stimFuntion = self.updateDataDictionary_stim_step
        elif StimulationFunction ==  u"Random":
            self.__stim_random_offset = self.get(u"stim_random_offset")
            self.__stim_random_amplitude = self.get(u"stim_random_amplitude")                   
            self.__stimFuntion = self.updateDataDictionary_stim_random

        if  signalMapped  == None:
            self.__time = None
            self.__signal = None
            self.__iteratorSignal = None
            self.__stimulateBySignal = False
            self.__lenSignal = None
            return 
     
        # Stimulation by Signal
        self.__stimulateBySignal = True
        self.__stimFuntion = self.updateDataDictionary_stim_signal
        signalObject = self.__signalhandler.get(signalMapped) 
        signal = signalObject[u"values"]
        time = signalObject[u"time"]
        self.__time = time
        self.__signal = signal
        self.__iteratorSignal = 0
        self.__lenSignal_minus_1 = len(signal) - 1

    
    def updateDataDictionary(self):
        
        if self.get(u"bStimulate"):
            self.__stimFuntion()

    def updateDataDictionary_const_val(self):
        self.__DataDictionary[ self.get(u"DisplayName") ] = self.__stim_const_val

    def updateDataDictionary_stim_sine(self):
        t = self.__RunConfigDictionary[u"t"]
        value = self.__stim_sine_offset + self.__stim_sine_amplitude * math.sin(2 * math.pi * self.__stim_sine_frequency * t )
        self.__DataDictionary[ self.get(u"DisplayName") ] = value

        
    def updateDataDictionary_stim_ramp(self):
        t = self.__RunConfigDictionary[u"t"]
        ratio = (t +  self.__stim_ramp_phase) / self.__stim_ramp_frequency
        value = self.__stim_ramp_offset + self.__stim_ramp_amplitude * (ratio - math.ceil(ratio) )
        self.__DataDictionary[ self.get(u"DisplayName") ] = value
    
    def updateDataDictionary_stim_pulse(self):
        t = self.__RunConfigDictionary[u"t"]
        ratio = (t +  self.__stim_pulse_phase) / self.__stim_pulse_frequency
        if ratio < 0.5:
            value = self.__stim_pulse_offset
        else:
            value = self.__stim_pulse_offset + self.__stim_pulse_amplitude
        self.__DataDictionary[ self.get(u"DisplayName") ] = value            
    
    def updateDataDictionary_stim_step(self):
        t = self.__RunConfigDictionary[u"t"]
        if self.__stim_step_phase > t:
            value = self.__stim_step_offset
        else:
            value = self.__stim_step_offset + self.__stim_step_amplitude
        self.__DataDictionary[ self.get(u"DisplayName") ] = value     
    
    def updateDataDictionary_stim_random(self):
        value = self.__stim_random_offset + self.__stim_random_amplitude * numpy.random.rand() 
        self.__DataDictionary[ self.get(u"DisplayName") ] = value  
    
    def updateDataDictionary_stim_signal(self):

        t = self.__RunConfigDictionary[u"t"]
        
        # find highest iterator for which tSignal < signal and

        while (self.__iteratorSignal < self.__lenSignal_minus_1):
            if self.__time[self.__iteratorSignal] < t: 
                if self.__time[self.__iteratorSignal + 1] >= t:
                    break
                else:
                    self.__iteratorSignal += 1
            else:
                break
            
        self.__DataDictionary[ self.get(u"DisplayName") ] =  self.__signal[self.__iteratorSignal]