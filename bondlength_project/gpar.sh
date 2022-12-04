#!/bin/bash

cwd=$(pwd)
output_dir=$cwd/parser_out
tmp_dir=$cwd/tmp

mkdir -p $cwd/tmp $cwd/parser_out

opt=false
freq=false
td=false

[ ! -e $tmp_dir/runconfig.cfg.tmp ] || rm $tmp_dir/runconfig.cfg.tmp

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

#Takes user input - select jobs to include 
while :
do
    error=false

    echo "[PROMPT] Select job types you wish to include in your search (one or more selections possible, delimited by a space, ie. '1', or '1 2 3'). Type -1 to exit."
    echo "[-1] - Exit"
    echo "[0] - All"
    echo "[1] - (Opt) Optimization"
    echo "[2] - (Freq) Frequency"
    echo "[3] - (TD) UV-Vis"

    read -a job_input

    for i in "${job_input[@]}"
    do
        if [[ $i == 0 ]]
        then
            opt=true 
            freq=true
            td=true
        elif [[ $i == 1 ]]
        then
            opt=true
        elif [[ $i == 2 ]]
        then
            freq=true
        elif [[ $i == 3 ]]
        then
            td=true
        elif [[ $i == -1 ]]
        then
            echo "[EXITING]"
            exit 0
        else
            echo "[ERROR] '$i' is not a valid selection"
            error=true
            continue
        fi
    done

    if $opt
    then
        echo "[INFO] Opt jobs are selected"
        echo "opt=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $freq
    then
        echo "[INFO] Freq jobs are selected"
        echo "freq=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $td
    then
        echo "[INFO] TD jobs are selected"
        echo "td=true" >> $tmp_dir/runconfig.cfg.tmp
    fi

    if [[ $error == false ]]
    then
        break
    fi

done

###USER SELECT OF WHAT INFORMATION TO EXTRACT


###WRAP THESE IN SOME CONDITIONS FOR SELECTED JOBS AND INFORMATION TYPE
echo "ARCHIVE_HEADERS:"  >> $tmp_dir/runconfig.cfg.tmp
for f in $(cat $tmp_dir/paths.txt.tmp)
do
    grep -n -F -H "1\1" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
done
echo "END!" >> $tmp_dir/runconfig.cfg.tmp

echo "ARCHIVE_FOOTERS:" >> $tmp_dir/runconfig.cfg.tmp
for f in $(cat $tmp_dir/paths.txt.tmp)
do
    grep -n -F -H "\\@" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
done
echo "END!" >> $tmp_dir/runconfig.cfg.tmp

echo "OPT_PARAMS:" >> $tmp_dir/runconfig.cfg.tmp
for f in $(cat $tmp_dir/paths.txt.tmp)
do
    grep -n -F -H "!   Optimized Parameters   !" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
done
echo "END!" >> $tmp_dir/runconfig.cfg.tmp
