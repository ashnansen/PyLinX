'''
Created on 30.10.2014

@author: Waetzold Plaum
'''

from PyQt4 import QtCore
from PyQt4.QtGui import *


class color():
    white           = QColor(255,255,255)
    background      = QColor(255,255,224)
    backgroundSim   = QColor(236,255,236)
    black           = QColor(0,0,0)
    transparent     = QColor(0,0,0,0)
    red             = QColor(206,0,0)
    blue            = QColor(0,0,100)
    blueTransp      = QColor(0,0,100, 150)
    yellow          = QColor(255,255,0)
    orange          = QColor(255,127,0)
    green           = QColor(0,128,0)
    blueLocalVar    = QColor(18,176,240)
    grayLight       = QColor(196,196,196)
    Highlight       = QColor(200,200,255)
    HighlightTransp = QColor(200,200,255, 60)
    tupleOsciColors = (QColor(128,0  ,0  ),\
                       QColor(0  ,128,0  ),\
                       QColor(0  ,0  ,128),\
                       QColor(64 ,64 ,0  ),\
                       QColor(64 ,0  ,64 ),\
                       QColor(0  ,64 ,64 ),\
                       QColor(96 ,0  ,32 ),\
                       QColor(33 ,0  ,96 ),\
                       QColor(0  ,32 ,96 ),\
                       QColor(0  ,96 ,32 ),\
                       QColor(96 ,0  ,32 ),\
                       QColor(32 ,0  ,96 ),\
                       QColor(16 ,32 ,18 ),\
                       QColor(32 ,16 ,80 ),\
                       QColor(16 ,80 ,32 ),\
                       QColor(32 ,80 ,16 ),\
                       QColor(80 ,16 ,32 ),\
                       QColor(80 ,32 ,16 ),\
                       QColor(64 ,32 ,32 ),\
                       QColor(32 ,64 ,32 ),\
                       QColor(32 ,32 ,64 ))


class brush():
    white           = QBrush(QtCore.Qt.white)
    black           = QBrush(QtCore.Qt.black)
    gray            = QBrush(QtCore.Qt.gray)
    grayLight       = QBrush(color.grayLight) 
    transparent     = QBrush(color.transparent) 
    blue            = QBrush(color.blue)
    green           = QBrush(color.green)
    blueLocalVar    = QBrush(color.blueLocalVar)
    Highlight       = QBrush(color.Highlight)
    HighlightTransp = QBrush(color.HighlightTransp)

class Plot_Target(): 
    Gui             = 1

class PX_DiagData():
    StimForm = {}
    StimForm["Constant"]  = [{ "Name": "stim_const_val",        "DisplayName":  "Value",     "ValueType": "float", "Value": 0.}]
    StimForm["Sine"]      = [{ "Name": "stim_sine_frequency",   "DisplayName":  "Frequency", "ValueType": "float", "Value": 0., "Unit" : "Hz"},\
                             { "Name": "stim_sine_phase",       "DisplayName":  "Phase",     "ValueType": "float", "Value": 0., "Unit": "s"},\
                             { "Name": "stim_sine_offset",      "DisplayName":  "Offset",    "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_sine_amplitude",   "DisplayName":  "Amplitude", "ValueType": "float", "Value": 0.}]
    StimForm["Ramp"]      = [{ "Name": "stim_ramp_frequency",   "DisplayName":  "Frequency", "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_ramp_phase",       "DisplayName":  "Phase",     "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_ramp_offset",      "DisplayName":  "Offset",    "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_ramp_amplitude",   "DisplayName":  "Amplitude", "ValueType": "float", "Value": 0.}] 
    StimForm["Pulse"]     = [{ "Name": "stim_pulse_frequency",  "DisplayName":  "Frequency", "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_pulse_phase",      "DisplayName":  "Phase",     "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_pulse_offset",     "DisplayName":  "Offset",    "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_pulse_amplitude",  "DisplayName":  "Amplitude", "ValueType": "float", "Value": 0.}]  
    StimForm["Step"]      = [{ "Name": "stim_step_phase",       "DisplayName":  "Phase",     "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_step_offset",      "DisplayName":  "Offset",    "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_step_amplitude",   "DisplayName":  "Amplitude", "ValueType": "float", "Value": 0.}]  
    #StimForm["Random"]    = [{ "Name": "stim_random_phase",     "DisplayName":  "Phase",     "ValueType": "float", "Value": 0.},\
    StimForm["Random"]    = [{ "Name": "stim_random_offset",    "DisplayName":  "Offset",    "ValueType": "float", "Value": 0.},\
                             { "Name": "stim_random_amplitude", "DisplayName":  "Amplitude", "ValueType": "float", "Value": 0.}]  

## Definition of graphical measures 

class Scalable:
    def __init__(self, ratio = 1, Target = -1):
        self.ratio = ratio 
        if Target == Plot_Target.Gui:
            self.brush = QBrush(QtCore.Qt.white)
    
    def ratio(self):
        return self.ratio
    
    def setRatio(self, ratio):
        self.ratio = ratio
               
    # DIN A4 
    def px_DinA4_WIDTH(self):               
        return  self.ratio * 2480
    
    def px_DinA4_HEIGTH(self):              
        return  self.ratio * 3508
    
    # DIN A3 
    def px_DinA3_WIDTH(self):               
        return  self.ratio * 3508
    
    def px_DinA3_HEIGTH(self):              
        return  self.ratio * 4962
    
    # ratio 60 degree rectangle
    def r_60deg(self):
        return 0.886
    
 
    ################################
    ## element
    ################################
    
    #  minimal width of element name 
    
    def px_ELEMENT_minWidth(self):
        return self.ratio * 90
    
    def px_ELEMENT_pinHeigth(self):
        return self.ratio * 10
    
    def px_ELEMENT_Border(self):
        return self.ratio * 2.5
    
    def px_ELEMENT_Light(self):
        return self.ratio 
    
    def px_ELEMENT_MediumLight(self):
        return 1.5 * self.ratio 
    
    def px_ELEMENT_pinLength(self):
        return self.ratio * 15
    
    def px_ELEMENT_Highlight(self):
        return self.ratio * 8
    
    # Simulation stuff
    def px_ELEMENT_PinSimulation(self):
        return self.ratio * 12
    
    def px_ELEMENT_PinSimulationWidth(self):
        return self.ratio * 4
    
    def px_ELEMENT_PinSimulation_x(self):
        return self.ratio * (-56)
    
    def px_ELEMENT_PinSimulation_Arrow(self):
        return self.ratio * 7
    
    # minimal wigth of color bar without element type
    
    def px_ELEMENT_minWidthColorBar(self):
        return self.ratio * 10
    
    #  minimal heigth of an element 
    
    def px_EMELENT_minHeigth(self):
        return self.ratio * 20
    
    def px_ELEMENT_stdPinDistance(self):
        return self.ratio * 20
    
    def px_ELEMENT_stdFontSize(self):
        return self.ratio * 8
    
    def px_ELEMENT_whiteSpace(self):
        return self.ratio * 4
    
    
    #################################
    ## connector
    #################################
    
    def px_CONNECTOR_rad(self):
        return self.ratio * 5
    
    def px_CONNECTOR_highlight(self):
        return self.ratio * 5
    
    def px_CONNECTOR_activeZone(self):
        return self.ratio * 4
    
    def px_CONNECTOR_line(self):
        return self.ratio * 1
    

    ################################
    ## plottable elemtary operator
    ################################
    
    def px_PLOTABLEELEMOPERATOR_size(self):
        return self.ratio * 30
    
    def px_PLOTABLEELEMOPERATOR_innerDiameter(self):
        return self.ratio * 1.7

    def px_PLOTABLEELEMOPERATOR_outerDiameter(self):
        return self.ratio * 10
    
    
    #################################
    ## Highlight
    #################################

    def px_HIGHLIGHT_border(self):
        return self.ratio * 2
    
# Template
    
class Template():
    Gui     = Scalable(1, Plot_Target.Gui)


templ = Scalable(0.3)    