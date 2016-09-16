# This is a test commentary
###########################

new varElement TestVar_0 150 90 15 refName="TestVar_0"
new varElement Variable_id4 150 140 15 refName="Variable_id4_1" 
new varElement Variable_id4 400.0 100.0 15 refName="Variable_id4_2"
new basicOperator + 300.0 100.0 name=u"Operator_1"
new connector TestVar_0 Operator_1 idxInPin=-1
new connector Variable_id4_1 Operator_1 idxInPin=-2
new connector Operator_1 Variable_id4_2 idxInPin=-1
new varElement Variable_id8 140.0 190.0 15
select Variable_id8_id7
set @.xy (10.0,0.0) -p
new basicOperator * 300.0 200.0
new varElement Variable_id10 150.0 250.0 15
new varElement Variable_id11 410.0 200.0 15
select
new connector 7 idxOutPinConnectorPloting=0
set @latent/11_id11.connectInfo ("Operator_mult_id9",-1)
new connector 9 idxOutPinConnectorPloting=0
set @latent/13_id13.connectInfo ("Operator_mult_id9",-2)
new connector 8 idxOutPinConnectorPloting=0
set @latent/15_id15.connectInfo ("Variable_id11_id10",-1)
new basicOperator - 530.0 100.0
select Operator_minus_id18
set @.xy (10.0,0.0) -p
set @.xy (0.0,10.0) -p
select
new connector 2 idxOutPinConnectorPloting=0
set @latent/18_id18.connectInfo ("Operator_minus_id18",-1)
new connector 10 idxOutPinConnectorPloting=0
set @latent/20_id20.connectInfo ("Operator_minus_id18",-2)
select 20_id20
set ./20_id20.listPoints [80.0,-80.0]
new varElement Variable_id23 650.0 110.0 15
select
new connector 17 idxOutPinConnectorPloting=0
set @latent/23_id23.connectInfo ("Variable_id23_id22",-1)
set @mainController.bSimulationMode True
new signalFile D:/Projekte/PyLinX/Aptana-Projekte/PyLinX2/Recources/Testdata/Testdata1.mf4
set @objects/variables/TestVar_0.signalMapped var5|Signal_id36
set @objects/variables/Variable_id4.signalMapped Variable_id4|Signal_id36
