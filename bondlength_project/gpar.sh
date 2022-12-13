#!/bin/bash

cwd=$(pwd)
output_dir=$cwd/parser_out
tmp_dir=$cwd/tmp

mkdir -p $cwd/tmp $cwd/parser_out

opt=false
freq=false
td=false

scf=false
coords=false
mulliken=false
bonds=false
angles=false

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

#Takes user input - select jobs to include 
while :
do
    error=false

    echo "[PROMPT] Select job types you wish to include in your search (one or more selections possible, delimited by a space, ie. '1', or '1 2 3'). Type -1 to exit."
    echo "[-1] - Exit"
    echo "[0] - All"
    echo "[1] - opt"
    echo "[2] - freq=raman"
    echo "[3] - td"
    #echo "[x] - (reopt) Re-Optimization"

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

#Takes user input - select jobs to include 
while :
do
    error=false

    echo "[PROMPT] Select what information you wish to print out (one or more selections possible, delimited by a space, ie. '1', or '4 2 3'). Type -1 to exit."
    echo "[-1] - Exit"
    echo "[0] - All possible"
    echo "[1] - SCF energies"
    echo "[2] - Coordinates"
    echo "[3] - Bond lengths"
    echo "[4] - Angles and dihedrals"
    echo "[5] - Mulliken charges"

    read -a info_input

    for i in "${info_input[@]}"
    do
        if [[ $i == 0 ]]
        then
            scf=true
            coords=true
            bonds=true
            angles=true
            mulliken=true
            dipole=true
        elif [[ $i == 1 ]]
        then
            scf=true
        elif [[ $i == 2 ]]
        then
            coords=true
        elif [[ $i == 3 ]]
        then
            bonds=true
        elif [[ $i == 4 ]]
        then
            angles=true
        elif [[ $i == 5 ]]
        then
            mulliken=true
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

    if $scf
    then
        echo "[INFO] SCF energies selected"
        echo "scf=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $coords
    then
        echo "[INFO] Coordinates are selected"
        echo "coords=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $bonds
    then
        echo "[INFO] Bonds are selected"
        echo "bonds=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $angles
    then
        echo "[INFO] Angles and dihedrals are selected"
        echo "angles=true" >> $tmp_dir/runconfig.cfg.tmp
    fi
    if $mulliken
    then
        echo "[INFO] Mulliken charges are selected"
        echo "mulliken=true" >> $tmp_dir/runconfig.cfg.tmp
    fi

    if [[ $error == false ]]
    then
        break
    fi
done

echo "--OPTIONS_END--" >> $tmp_dir/runconfig.cfg.tmp

echo "ARCHIVE_HEADERS_START:"  >> $tmp_dir/runconfig.cfg.tmp
for f in $(cat $tmp_dir/paths.txt.tmp)
do
    grep -n -F -H "1\1" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
done
echo "ARCHIVE_HEADERS_END:" >> $tmp_dir/runconfig.cfg.tmp

echo "ARCHIVE_FOOTERS_START:" >> $tmp_dir/runconfig.cfg.tmp
for f in $(cat $tmp_dir/paths.txt.tmp)
do
    grep -n -F -H "\\@" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
done
echo "ARCHIVE_FOOTERS_END:" >> $tmp_dir/runconfig.cfg.tmp

if $coords || $angles
then
    echo "OPT_PARAMS_START:" >> $tmp_dir/runconfig.cfg.tmp
    for f in $(cat $tmp_dir/paths.txt.tmp)
    do
        grep -n -F -H "!   Optimized Parameters   !" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
    done
    echo "OPT_PARAMS_END:" >> $tmp_dir/runconfig.cfg.tmp
fi

if $scf
then
    echo "SCF_DONE_START:" >> $tmp_dir/runconfig.cfg.tmp
    for f in $(cat $tmp_dir/paths.txt.tmp)
    do 
        grep -n -F -H "SCF Done" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
    done
    echo "SCF_DONE_END:" >> $tmp_dir/runconfig.cfg.tmp
fi

if $mulliken
then
    echo "MULLIKEN_CHARGES_START:" >> $tmp_dir/runconfig.cfg.tmp
    for f in $(cat $tmp_dir/paths.txt.tmp)
    do
        grep -n -F -H "Mulliken charges:" $f | cut -f1,2 -d: >> $tmp_dir/runconfig.cfg.tmp
    done
    echo "MULLIKEN_CHARGES_END:" >> $tmp_dir/runconfig.cfg.tmp
fi

###run the python script
python $cwd/pylog.py $tmp_dir/runconfig.cfg.tmp $tmp_dir/paths.txt.tmp > $cwd/parser_out/debugout.txt