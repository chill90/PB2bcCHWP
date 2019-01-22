This directory contains files to be used for plotting encoder data taken using the Arduino

(0) location.py: stores the location of the encoder data, relative to this directory
    $masterDir

(1) encoderDataPlot.py: takes a run name to fine the data files created by 'encoderDataAnalyze.py' and generates plots at $masterDir/[Run Name]/Plots/
    Usage: python encoderDAQ.py [Run Name] [Number of seconds to collect data]
