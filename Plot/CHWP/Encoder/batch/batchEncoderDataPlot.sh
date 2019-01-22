#!/bin/bash

F=("20180418_spinUp_08V" "20180418_spinUp_16V" "20180418_spinUp_24V" "20180418_spinUp_32V")

for f in "${F[@]}"
do
    echo "Processing $f..."
    sudo python encoderDataPlot_spinUpDn.py $f
done
