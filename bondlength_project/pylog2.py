import os
import sys
import re
import linecache
import time

######

cwd = os.getcwd()

path = cwd + "/tmp/runconfig.cfg.tmp"
runconfig = open(path, 'r')

runcfg_arr = []
for line in runconfig:
    runcfg_arr.append(line.strip())

######

def extract_job_archive(logfile_path, start_line, job_types):
    job_archive = []
    current_line = start_line
    # read the job archive line by line
    while True:
        line = linecache.getline(logfile_path, current_line).strip()
        # check if the line contains any of the job types
        if any(job_type in line for job_type in job_types):
            job_archive.append(line)
            # if the line ends with a backslash, continue to the next line
            if line.endswith("\\"):
                current_line += 1
                continue
            # if the line doesn't end with a backslash, we've reached the end of the job archive
            else:
                break
        current_line += 1
    return job_archive

def extract_mulliken_charges(logfile_path, start_line):
    mulliken_charges = []
    current_line = start_line
    while True:
        line = linecache.getline(logfile_path, current_line)
        # check if the line contains Mulliken charges
        if "Mulliken charges:" in line:
            # read the next line to get the atomic numbers
            atomic_nums_line = linecache.getline(logfile_path, current_line + 1)
            atomic_nums = [int(x) for x in atomic_nums_line.split()]
            # read the following lines to get the charges
            charges = []
            for i in range(len(atomic_nums)):
                charge_line = linecache.getline(logfile_path, current_line + 2 + i)
                charges.append(float(charge_line.split()[-1]))
            # combine the atomic numbers and charges into a list of tuples
            mulliken_charges += list(zip(atomic_nums, charges))
        current_line += 1
        # check if we've reached the end of the file
        if line == '':
            break
    return mulliken_charges

###

## TEST ENTRIES:

# Archive Entries
# Start: ../logfiles/03_s1_opt.log:1027947
# End: ../logfiles/03_s1_opt.log:1027971
arch_file_path = "../logfiles/03_s1_opt.log"
arch_line_no = 1027947

# Mulliken Charges
# Start: ../logfiles/03_s1_opt.log:1027730
mull_file_path = "../logfiles/03_s1_opt.log"
mull_line_no = 1027730

# Opt Params
# Start: ../logfiles/03_s1_opt.log:1027054

# SCF

###