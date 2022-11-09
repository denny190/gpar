#!/bin/bash

# Specify current path and create dir for tmp files
cwd=$(pwd)
output_dir=$cwd/bond_out
tmp_dir=$cwd/tmp

mkdir -p $cwd/tmp $cwd/bond_out

# Specify bonds?

# Takes user input. If everything is ok exits loop and continues execution. If not, prompts user again until input correct or user quits
while :
do
	echo "[PROMPT] Input the path of your directory in which .log files (or subdirs with .log files) are located. Type -1 to exit."
	read -e path_input

	if test -d "$path_input" 
	then
		echo "[INFO] Succesfully located $path_input."

		find $path_input -name *.log > $tmp_dir/paths.txt.tmp

		num_logfiles=$(wc -l < $tmp_dir/paths.txt.tmp)
		echo "[INFO] Found $num_logfiles log files."

		if [ $num_logfiles -eq 0 ]
		then
			echo "[ERROR] No logfiles found. Try again."
			continue
		fi
		
		break

	elif [ $path_input -eq -1 ]
	then
		echo "[EOF] EXITING."
		exit 0

	else
		echo "[ERROR] Could not locate $path_input" 
	fi
done

# Specify what jobs to take geom from? (ie. only opt jobs)
### NOT NECESSARY NOW
job_type="FOpt"
[ ! -e $tmp_dir/selected_job_paths.txt.tmp ] || rm $tmp_dir/selected_job_paths.txt.tmp

# For loop to go to each file, extract information and coordinates into a separate file for each functional
for line in $(cat $tmp_dir/paths.txt.tmp)
	do
	# Extract filename from path
	file_name="$(basename "$line")"

	# Checks whether the log file is for an OPT job - if not, skips the iteration
	if grep -q $job_type $line
	then
		echo "$line" >> $tmp_dir/selected_job_paths.txt.tmp

		#Start python code that parses each log file
		python logparser.py $line $file_name
		
	else
		continue
	fi

done

