#!/bin/bash

# This script extracts various information from Gaussian log files
# Usage: ./gaussian_parser.sh [-h] [-j] [-f] [-b] [-c] [-e] [-q] <path>

# Print help message
function print_help {
    echo "Usage: ./gaussian_parser.sh [-h] [-j] [-f] [-b] [-c] [-e] [-q] <path>"
    echo "Options:"
    echo "  -h  Print this help message"
    echo "  -j  Extract job type"
    echo "  -f  Extract functional"
    echo "  -b  Extract basis set"
    echo "  -c  Extract optimized coordinates"
    echo "  -e  Extract SCF energies"
    echo "  -q  Extract Mulliken charges"
    echo "  path  Directory path to search for log files"
}

# Check command-line arguments
if [[ $# -lt 2 ]]; then
    echo "Error: Invalid number of arguments"
    print_help
    exit 1
fi

# Parse command-line options
while getopts ":hjfbceq" opt; do
    case ${opt} in
        h )
            print_help
            exit 0
            ;;
        j )
            job_type=true
            ;;
        f )
            functional=true
            ;;
        b )
            basis_set=true
            ;;
        c )
            optimized_coords=true
            ;;
        e )
            scf_energies=true
            ;;
        q )
            mulliken_charges=true
            ;;
        \? )
            echo "Error: Invalid option -$OPTARG" 1>&2
            print_help
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))

# Check if at least one option was specified
if [[ -z ${job_type} && -z ${functional} && -z ${basis_set} && -z ${optimized_coords} && -z ${scf_energies} && -z ${mulliken_charges} ]]; then
    echo "Error: At least one option must be specified"
    print_help
    exit 1
fi

# Check if the specified path exists
if [[ ! -d $1 ]]; then
    echo "Error: Directory not found: $1"
    print_help
    exit 1
fi

# Search for log files and extract information
for log_file in $(find $1 -name '*.log' -type f); do
    if [[ -f ${log_file} ]]; then
        if [[ ${job_type} ]]; then
            echo "Job type: $(grep -m 1 -i "jobtype" ${log_file} | awk '{print $2}')"
        fi
        if [[ ${functional} ]]; then
            echo "Functional: $(grep -m 1 -i "functional" ${log_file} | awk '{print $2}')"
        fi
        if [[ ${basis_set} ]]; then
            echo "Basis set: $(grep -m 1 -i "basis functions" ${log_file} | awk '{print $4,$5}')"
        fi
        if [[ ${optimized_coords} ]]; then
            echo "Optimized coordinates:"
            grep -A 100 -m 1 -i "optimized parameters" ${log_file} | tail -n +3 | head -n -1 | awk '{print $2,$3,$4}'
        fi
        if [[ ${scf_energies} ]]; then
            echo "SCF energies:"
            grep -i "scf energy" ${log_file} | awk '{print $4}'
        fi
        if [[ ${mulliken_charges} ]]; then
            echo "Mulliken charges:"
            grep -A 100 -m 1 -i "mulliken atomic charges" ${log_file} | tail -n +3 | head -n -1 | awk '{print $2,$3}'
        fi
        echo ""
    fi
done