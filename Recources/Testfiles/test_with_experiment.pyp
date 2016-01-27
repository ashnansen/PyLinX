new varElement TestVar_0 150 90 15
new varElement Variable_id4 150 140 15
new varElement Variable_id3 400.0 100.0 15
new basicOperator + 300.0 100.0 name=u"Operator_1"
new connector TestVar_0 Operator_1 idxInPin=1
new connector Variable_id4 Operator_1 idxInPin=0
new connector Operator_1 Variable_id3 idxInPin=0
set @mainController.bSimulationMode True
select TestVar_0
set TestVar_0. {'stim_sine_amplitude':1.0,'stim_sine_frequency':1.0,'stim_sine_phase':0.0,'stim_sine_offset':2.0}
select Variable_id4
set Variable_id4. {'stim_random_amplitude':0.2,'stim_random_offset':0.0}
select Variable_id3
new dataViewer 50 50
set ./Variable_id3.listSelectedDispObj [1]
