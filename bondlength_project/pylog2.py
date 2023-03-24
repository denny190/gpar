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
    # check if the start line contains any of the job types
    if any(job_type in linecache.getline(logfile_path, start_line) for job_type in job_types):
    # read the job archive line by line
        while True:
            line = linecache.getline(logfile_path, current_line).strip()
            # check if the line contains any of the job types
            job_archive.append(line)
            # if the line ends with a backslash, continue to the next line
            if "\\@" in line:
                break
            # if the line doesn't end with a backslash, we've reached the end of the job archive
            else:
                current_line += 1
                continue
    
    ### clean up of archive to a nice list
    job_archive = ''.join(job_archive)
    job_archive = job_archive.split("\\")
        
    return job_archive

def extract_mulliken_charges(filepath, line_num):
    charges = []
    with open(filepath) as f:
        for i, line in enumerate(f):
            if i == line_num:
                for line in f:
                    if " Sum " in line:
                        break
                    atom_num, atom_type, atom_charge = line.split()
                    charges.append([atom_num, atom_type, atom_charge])
                break  # We found the table, stop parsing
    return charges

def extract_params(filepath, line_num):
   
    all_params = []
    with open(filepath) as f:
        current_line_no = line_num
        while True:
            current_line = linecache.getline(current_line_no)
            if "---" in current_line and current_line_no > (line_num + 4):
                break
            else:
                all_params.append(current_line)
                current_line_no += 1
            



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
optparam_file_path = "../logfiles/03_s1_opt.log"
optparam_line_no = "1027054"

# SCF

###

test_archive = extract_job_archive(arch_file_path, arch_line_no, "opt")
for line in test_archive: print(line)

test_mulliken = extract_mulliken_charges(mull_file_path, mull_line_no)
for line in test_mulliken: print(line)