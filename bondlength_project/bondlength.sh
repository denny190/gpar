#!/bin/bash

# Specify current path and create dir for tmp files
cwd=$(pwd)
output_dir=$cwd/bond_out
tmp_dir=$cwd/tmp

mkdir -p $cwd/tmp $cwd/bond_out

# ?? Specify bonds?

# Specify dir in which all .log or subdirs with .log files are located
echo "[PROMPT] Input the path of your directory in which .log files (or subdirs with .log files) are located. Type -1 to exit."
read -e searched_dir

###Checking whether the inputted file exists. 
###Prevention of submitting non-existent files in case of typos etc.
	###	THIS IS WRONG!!
until test -d "$searched_dir" || [ $searched_dir == -1 ]
do
	echo "[ERROR] Could not locate '~/$searched_dir'."
	echo "[PROMPT] Input the path of your directory in which .log files (or subdirs with .log files) are located. Type -1 to exit."
	read -e searched_dir
done

if [ $searched_dir == -1 ]; then
	echo "[EOF] EXITING."
	exit 0
fi
# Save paths of selected .log files in a paths.txt.tmp file
find $inpDir -name *.log > paths.txt.tmp
path_file=$tmp_dir/paths.txt.tmp

num_logfiles=$(wc -l < $tmp_dir/paths.txt.tmp)
echo "[INFO] Found $num_logfiles log files."

# If no files were found exit (sort this out so user can make another attempt if = 0
if [ $num_logfiles == 0 ]; then
	echo "[EOF] No log files found. EXITING."
	exit 1
fi

# Specify what jobs to take geom from? (ie. only opt jobs)
### NOT NECESSARY NOW
job_type="FOpt"

# For loop to go to each file, extract information and coordinates into a separate file for each functional
for line in $path_file; do

	# Checks whether the log file is for an OPT job - if not, skips the iteration
	if grep -q $job_type $line; then
		$line > $tmp_dir/selected_job_paths.txt.tmp
	else
		continue
	fi
	
	#logparser.py $line $

done

# Calculate bond lengths

# Group data from same functionals together

# Optionally calculate differences in bond lengths
