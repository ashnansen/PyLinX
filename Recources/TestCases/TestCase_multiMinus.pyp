new varElement TestVar_0 150 90 15 refName="TestVar_0"
new varElement Variable_id4 150 140 15 refName="Variable_id4_1" 
new varElement Variable_id4 400.0 100.0 15 refName="Variable_id4_2"
new basicOperator + 300.0 100.0 name=u"Operator_1"
new connector TestVar_0 Operator_1 idxInPin=1
new connector Variable_id4_1 Operator_1 idxInPin=0
new connector Operator_1 Variable_id4_2 idxInPin=0
select Operator_1
del 6_id6 5_id5 Operator_1 4_id4
new basicOperator - 280.0 90.0
select Variable_id4_2
set @.xy (10.0,0.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (10.0,0.0) -p
select Operator_minus_id8
set @.xy (10.0,0.0) -p
set @.xy (0.0,10.0) -p
set @.xy (10.0,0.0) -p
select
new connector 0 idxOutPinConnectorPloting=0
set @latent/8_id8.connectInfo ("Operator_minus_id8",-1)
new connector 1 idxOutPinConnectorPloting=0
set @latent/10_id10.connectInfo ("Operator_minus_id8",-2)
select 10_id10
set ./10_id10.listPoints [110.0,-30.0]
set ./10_id10.listPoints [100.0,-30.0]
set ./10_id10.listPoints [90.0,-30.0]
select
new connector 7 idxOutPinConnectorPloting=0
set @latent/PX_PlottableProxyElement.xy (357,88)
select Variable_id4_2
set @latent/PX_PlottableProxyElement.xy (402,88)
set @.xy (10.0,0.0) -p
set @.xy (0.0,10.0) -p
set @.xy (10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (20.0,0.0) -p
select
set @latent/12_id12.connectInfo ("Variable_id4_2",-1)
select Variable_id4_2
set @.xy (0.0,10.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (0.0,10.0) -p
set @.xy (0.0,10.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (0.0,10.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (0.0,10.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (-20.0,0.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (10.0,0.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (0.0,-10.0) -p
set @.xy (-10.0,0.0) -p
set @.xy (-10.0,0.0) -p
select
new basicOperator - 580.0 110.0
new connector 2 idxOutPinConnectorPloting=0
set @latent/15_id15.connectInfo ("Operator_minus_id15",-1)
new varElement Variable_id18 320.0 190.0 15
new connector 17 idxOutPinConnectorPloting=0
set @latent/PX_PlottableProxyElement.xy (469,183)
set @latent/18_id18.connectInfo ("Operator_minus_id15",-2)
new varElement Variable_id21 720.0 110.0 15
new connector 14 idxOutPinConnectorPloting=0
set @latent/21_id21.connectInfo ("Variable_id21_id20",-1)
new basicOperator - 850.0 120.0
new connector 20 idxOutPinConnectorPloting=0
set @latent/24_id24.connectInfo ("Operator_minus_id24",-1)
new varElement Variable_id27 590.0 210.0 15
new connector 26 idxOutPinConnectorPloting=0
set @latent/27_id27.connectInfo ("Operator_minus_id24",-2)
new varElement Variable_id30 1000.0 120.0 15
new connector 23 idxOutPinConnectorPloting=0
set @latent/30_id30.connectInfo ("Variable_id30_id29",-1)
set @mainController.bSimulationMode True
