#!/bin/bash

#F=("20180328_Spinup_8V" "20180328_Spindn_8V" "20180328_Spinup_16V" "20180328_Spindn_16V" "20180328_Spinup_24V" "20180328_Spindn_24V" "20180328_Spinup_32V" "20180328_Spindn_32V")
#F=("20180418_spinUp_08V" "20180418_spinDn_08V" "20180418_spinUp_16V" "20180418_spinDn_16V" "20180418_spinUp_24V" "20180418_spinDn_24V" "20180418_spinUp_32V" "20180418_spinDn_32V")
#F=("20180418_spinUp_08V" "20180418_spinUp_16V" "20180418_spinUp_24V" "20180418_spinUp_32V")
F=("20191105_1" "20191105_2" "20191105_3" "20191105_4" "20191105_5" "20191105_6" "20191105_7" "20191106_1" "20191106_2" "20191106_3" "20191106_4" "20191106_5" "20191106_6" "20191106_7")

for f in "${F[@]}"
do
    echo "Processing $f..."
    sudo python encoderDataProcess.py $f
done
