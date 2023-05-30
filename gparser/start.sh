#!/usr/bin/python3

cwd=$(pwd)
output_dir=$cwd/parser_out

# Takes user input. If everything is ok exits loop and continues execution. If not, prompts user again until input correct or user quits
while :
do
	echo "[PROMPT] Input the path of your directory in which .log files (or subdirs with .log files) are located. Type -1 to exit."
	read -e path_input
 
	if test -d "$path_input" 
	then
		echo "[INFO] Succesfully located $path_input."

		find $path_input -name *.log > paths.txt.tmp
		num_logfiles=$(wc -l < paths.txt.tmp)

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

    echo "[PROMPT] Do you wish to output to console or parser_out/output.txt file?"
    echo "[-1] - Exit"
    echo "[0] - Console"
    echo "[1] - File"

    read -a info_input

    for i in "${info_input[@]}"
    do
        if [[ $i == 0 ]]
        then
            echo "[INFO] Running 0"
            python parser.py $paths
        elif [[ $i == 1 ]]
        then
            echo "[INFO] Running 1"
            mkdir -p $cwd/parser_out
            python parser.py $paths > $output_dir/output.txt
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

    if [[ $error == false ]]
    then
        break
    fi
done

#rm *.tmp