#!/bin/bash

python plotMotorCurrentWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/CurrentWaveform_08V.txt
python plotMotorCurrentWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/CurrentWaveform_16V.txt
python plotMotorCurrentWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/CurrentWaveform_24V.txt
python plotMotorCurrentWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/CurrentWaveform_32V.txt

python plotMotorVoltageWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/VoltageWaveform_08V.txt
python plotMotorVoltageWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/VoltageWaveform_16V.txt
python plotMotorVoltageWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/VoltageWaveform_24V.txt
python plotMotorVoltageWaveforms.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/VoltageWaveform_32V.txt

python plotMotorPowerDissipation.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/PowerRMS.txt
python plotMotorCurrent.py ../../Data/CAPMAP_Run03_20180316/Data/MotorWaveform/CurrentRMS.txt
