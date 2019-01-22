#!/bin/bash

#F=("20180328_Spinup_8V" "20180328_Spindn_8V" "20180328_Spinup_16V" "20180328_Spindn_16V" "20180328_Spinup_24V" "20180328_Spindn_24V" "20180328_Spinup_32V" "20180328_Spindn_32V")
#F=("20180418_spinUp_08V" "20180418_spinDn_08V" "20180418_spinUp_16V" "20180418_spinDn_16V" "20180418_spinUp_24V" "20180418_spinDn_24V" "20180418_spinUp_32V" "20180418_spinDn_32V")
F=("20180418_spinUp_08V" "20180418_spinUp_16V" "20180418_spinUp_24V" "20180418_spinUp_32V")

for f in "${F[@]}"
do
    echo "Processing $f..."
    sudo python encoderDataProcess_spinUp.py $f
done
