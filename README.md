This is a repository for managing files within Akito Kusaka and Toki Suzuki’s CMB research group at Lawrence Berkeley National Laboratory.

This repo is meant to preserve code written by the group and to easily distribute those codes between computers in the labs and offices. It is also meant to make code updates more straightforward to both store and share using the functionality of Git.

There are two rules when it comes to using this repository:
  1. Only use it for code maintenance. Do not upload data, PDF files, etc. here as they will overload the repo
  2. Keep the repo clean and organized. When you add a file, please think carefully about where to put it. Add a sub-directory if you think it’s merited based on the structure that’s already in place, and discuss with your colleagues if you want to change the organization scheme. Just don’t put the files into the repo willy-nilly.

The repo is divided into several areas:
  1. DAQ — includes readout code for thermometry, the CHWP encoder, Keithly boxes, the Honeywell magnetometer, etc
  2. Control — includes control code for sending commands to power supplies, motor controllers, etc.
  3. Analyze — includes code to analyze data, such as taking FFTs, smoothing data, etc.
  4. Calculate — includes code to calculate quantities such as thermal conductivity, torques, power dissipations, thermal time constants, etc.
  5. Plot — includes code to make plots. Again, please do not add plots or data to this repo. Only use it to maintain the scripts that handle the data and make the plots.

Contact Charles Hill (chill@lbl.gov) or Akito Kusaka (akusaka@lbl.gov) to become a contributor to this repo. 

Git push responsibly :)
  

