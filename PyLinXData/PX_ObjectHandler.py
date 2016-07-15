'''
Created on 18.02.2016

@author: Waetzold Plaum
'''

import numpy
import math
import os
import mdfreader
import numpy as np
import inspect
from datetime import datetime

#import BContainer
import PyLinXCtl
import PyLinXCoreDataObjects
from PyLinXData import PX_CSVObject as PX_CSVObject 


# The object handler handles the problem that each variable, class pp. may occur several times in the code. But these instances correspond to single
# objects. The object handler handles the object. Each time a new instance of the variable is createt, it is registered by the object handler. The 
# object handler also manages the recording of signals. 

class PX_ObjectHandler(PyLinXCoreDataObjects.PX_Object):
    
    # Enumeration for the file extension of the recorder
    
    class FileExt:
        
        number=0
        dateNtima=1
        
    # Enumeration for the states of the recorder
    
    class recorderState:
        
        off = 0
        logSelected = 1
        logAll = 2
    
    def __init__(self, parent):
        if not (type(parent) == PyLinXCtl.PyLinXMainController.PyLinXMainController):
            raise Exception("Error PX_ObjectHandler.__init__: Invalid Type of MainController")
        super(PX_ObjectHandler, self).__init__(parent, u"ObjectHandler")
        self.set(u"bObjectInSimulationMode", False)
        self._BContainer__AttributesVirtual.extend([u"listObjects", u"mapping", u"bRecord", u"recorder_VariablesToRecordProcessed"])
        
        ################################
        # Configuration of the recorder
        ################################
        
        self.set(u"recorder_BaseFileName", u"measure")
        self.set(u"recorder_FileExtension", PX_ObjectHandler.FileExt.number)
        self.set(u"recorder_SaveFolder", os.path.join(os.getcwd(), u"Measurements"))
        self.set(u"recorder_RecordState", PX_ObjectHandler.recorderState.off)
        self.set(u"recorder_VariablesToRecord", [])
        self.set(u"recorder_fileFormat", PX_Recorder.FileFormat.mdf)
        self.__mdfObject = None
        self.__dataDict = None
        self.__runConfigDictionary = None
        self.__bRecord = False
        self.__mainController = self.getRoot(PyLinXCtl.PyLinXMainController.PyLinXMainController)
        self.recorder = PX_Recorder(self)
        self.__variables = PyLinXCoreDataObjects.PX_Object(self, "variables")
        
    
    def register(self, variable):
        
        varName = variable.get(u"DisplayName")

        #  Attributes with the prefix "var." correspond to variables of the models

        if (varName in self.__variables._BContainer__Body):
            self._BContainer__Attributes[u"Var." + varName] += 1
            objectVar = self.__variables._BContainer__Body[varName]
            objectVar.get(u"listRefInstances").append(variable) 
        else:
            objectVar = PX_ObjectVariable(self.__variables, variable)
            self._BContainer__Attributes[u"Var." + varName] = 1
        
        return objectVar
        
        
    def unregister(self, varName):
        print "HAS TO BE IMPLEMENTED! unregister()"
    
    def runInit(self):

        for variable in self.__variables.getChildKeys():
            obj = self.__variables.getb(variable)
            obj.runInit()
            # NEU
            self.recorder.init()


    def updateDataDictionary(self):
        
        for variable in self.__variables.getChildKeys():
            obj = self.__variables.getb(variable)
            obj.updateDataDictionary()

   
    #######################
    # SETTER and GETTER
    #######################
    
    def get(self, attr):
        
        if attr == u"listObjects":
            return self.__variables._BContainer__Body.keys()
        elif attr == u"mapping":
            return self.__get_mapping()
        elif attr == u"bRecord":
            recorder_VariablesToRecord = self.get(u"recorder_VariablesToRecordProcessed")
            return (len(recorder_VariablesToRecord ) > 0)
        elif attr == u"recorder_VariablesToRecordProcessed":
            recorederState = self._BContainer__Attributes[u"recorder_RecordState"]<
            if  recorederState == PX_ObjectHandler.recorderState.logAll:
                return self.__variables._BContainer__Body.keys()
            elif recorederState == PX_ObjectHandler.recorderState.logSelected:
                return self._BContainer__Attributes[u"recorder_VariablesToRecord"]
            else:
                return []
        else:
            return super(PX_ObjectHandler, self).get(attr)

    
    def __get_mapping(self):
        mapping = {}
        for key in self.__variables.getChildKeys():
            element = self.__variables.getb(key)
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
        keys = self.__variables.getChildKeys()
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
        
        self.__RunConfigDictionary = self.__mainController.getb(u"RunConfigDictionary")
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
     
        
#############################################
## Recorder Class
#############################################

class PX_Recorder(PyLinXCoreDataObjects.PX_Object): 
    
    class FileFormat:
        mdf = "mdf"
        csv = "csv"
    
    def __init__(self, parent, name = "recorder"): 
        super(PX_Recorder, self).__init__(parent, name)
        self.__DataDictionary = None
        self.__RunConfigDictionary = None
        self.__bRecord = False
        
    def init(self):

        self.__DataDictionary = self.mainController.getb(u"DataDictionary")
        self.__RunConfigDictionary = self.mainController.getb(u"RunConfigDictionary")
        self.__objectHandler = self.getRoot(PX_ObjectHandler)
        
        # The data would be accessible in self.__parent, but they should be copied before the run is started due to 
        # data consistency
        self.__recorder_BaseFileName                = self.__objectHandler.get(u"recorder_BaseFileName")
        self.__recorder_FileExtension               = self.__objectHandler.get(u"recorder_FileExtension")
        self.__recorder_fileFormat                  = self.__objectHandler.get(u"recorder_fileFormat")
        self.__recorder_SaveFolder                  = self.__objectHandler.get(u"recorder_SaveFolder")
        self.__recorder_RecordState                 = self.__objectHandler.get(u"recorder_RecordState")
        self.__bRecord                              = self.__objectHandler.get(u"bRecord")
        self.__recorder_VariablesToRecordProcessed  = self.__objectHandler.get(u"recorder_VariablesToRecordProcessed")
        
        self.__dataDict = {}
        
        # Preparomg time signal
        self.__dataDict[u"time_1"] = {}
        self.__dataDict["time_1"]["data"] = np.array([], np.float64)
        self.__dataDict["time_1"]["description"] = "Time"
        self.__dataDict["time_1"]["master"] = u"time_1"
        self.__dataDict["time_1"]["masterType"] = 1 
        self.__dataDict["time_1"]["unit"] = u"s"
        
        # Preparing each variable to record
        for var in self.__recorder_VariablesToRecordProcessed:
            self.__dataDict[var] = {}
            self.__dataDict[var]["data"] = np.array([], np.float64)
            self.__dataDict[var]["description"] = u""
            self.__dataDict[var]["master"] = u"time_1"
            self.__dataDict[var]["masterType"] = 1 
            self.__dataDict[var]["unit"] = u""

    def record(self):
        
        if self.__bRecord: 
            time = self.__RunConfigDictionary[u"t"]
            self.__dataDict[u"time_1"][u"data"] = np.append(self.__dataDict[u"time_1"][u"data"], time)
            for var in self.__recorder_VariablesToRecordProcessed:
                val = self.__DataDictionary[var]
                self.__dataDict[var][u"data"] = np.append(self.__dataDict[var]["data"], val)
            
    def exit(self):
        
        if self.__bRecord:
            if self.__recorder_fileFormat == self.FileFormat.mdf:
                self.__exit_mdf()
            elif self.__recorder_fileFormat == self.FileFormat.csv:
                self.__exit_csv()
        
        
    def __exit_csv(self):
        
        csvObject = PX_CSVObject.CSVObject()
        
        listVarsToSave = [u"time_1"]
        listVarsToSave.extend(self.__recorder_VariablesToRecordProcessed)
        for var in listVarsToSave:
            csvObject.addChannel({u"values": self.__dataDict[var][u"data"], \
                                  u"label": str(var), \
                                  u"unit": str(self.__dataDict[var][u"unit"]), \
                                  u"type": "f16"})
            
        dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = str(os.path.join(self.__recorder_SaveFolder,self.__recorder_BaseFileName + u"_" + dt + u".csv"))
        csvObject.write(filename, ["PyLinXItemFile", "record", "CrLf", "Tab"])
    
    
    def __exit_mdf(self):        
        mdfObject = mdfreader.mdf()
        
        listVarsToSave = [u"time_1"]
        listVarsToSave.extend(self.__recorder_VariablesToRecordProcessed)
        for var in listVarsToSave :          
            mdfObject.add_channel(0, str(var),\
                       self.__dataDict[var][u"data"],\
                       master_channel   = str("time_1"), \
                       master_type      = self.__dataDict[var][u"masterType"],\
                       unit             = str(self.__dataDict[var][u"unit"]),\
                       description      = str(self.__dataDict[var][u"description"]),\
                       conversion       = None)
    
        dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = str(os.path.join(self.__recorder_SaveFolder,self.__recorder_BaseFileName + u"_" + dt + u".dat"))
        mdfObject.write(filename)        
        