Program for processing and graphing load curves
	Extracts final temperature (time -> infinity) of each power step by an exponential fit

Dependencies:
	python3, numpy, scipy, matplotlib (for graphing only)

Processing:
	$python3 process.py temperature_file power_file
	Outputs (in a subdirectory called 'process' within the input file (data) directory):
		result_tempfile_powerfile.csv -> Detailed curve fitting results file
		power_temp_tempfile_powerfile.txt -> Power vs. final temperature(s) file

        *'None' or empty entries for segments that fail to be fitted
        *Input files must be in the same directory
        

Graphing:
	$python3 graph.py result_file power_temp_file
	Outputs:
		matplotlib pyplot windows (saved in 'graph' subdirectory directory of the data directory) showing for each channel processed:
		Temperature vs. time (both experimental data and fitted curve)
		Power vs. final temperature
                
	*Do not change the relative path between result_file and its associated temperature_file if you want the experimental data plotted.
        *Possible to only save images or plot by setting SAVE and DISPLAY variables in the script
		
Demo:
	A sample data set is included in data/, to process and graph it:
	$python3 process.py
	$python3 graph.py

