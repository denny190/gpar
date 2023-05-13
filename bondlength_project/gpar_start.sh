#!/bin/bash

cwd=$(pwd)
output_dir=$cwd/parser_out
tmp_dir=$cwd/tmp

[ ! -e $tmp_dir/runconfig.cfg.tmp ] || rm $tmp_dir/runconfig.cfg.tmp
[ ! -e $tmp_dir/runconfig.cfg.tmp ] || rm $tmp_dir/selected_job_paths.txt.tmp

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
		echo "[EXITING]"
		exit 0

	else
		echo "[ERROR] Could not locate $path_input" 
	fi
done