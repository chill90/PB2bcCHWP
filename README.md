This is a repository for managing the PB2b and PB2c CHWP code.

There are two rules when it comes to using this repository:
  1. Only use it for code maintenance. Do not upload data, PDF files, etc. here as they will overload the repo
  2. Keep the repo clean and organized. When you add a file, please think carefully about where to put it. Add a sub-directory if you think it’s merited based on the structure that’s already in place, and discuss with your colleagues if you want to change the organization scheme. Just don’t put the files into the repo willy-nilly.

The repo is divided into several areas:
  1. DAQ — includes readout code for thermometry, the CHWP encoder, Keithly boxes, the Honeywell magnetometer, etc
  2. Control — includes control code for sending commands to power supplies, motor controllers, etc.
  3. Analyze — includes code to analyze data, such as taking FFTs, smoothing data, etc.
  4. Calculate — includes code to calculate quantities such as thermal conductivity, torques, power dissipations, thermal time constants, etc.
  5. Plot — includes code to make plots. Again, please do not add plots or data to this repo. Only use it to maintain the scripts that handle the data and make the plots.

Contact Charles Hill (chill@lbl.gov) to become a contributor to this repo.

*** Start-up ***
Before starting to use this repository, please run

source config.sh

which will set up the environment.
