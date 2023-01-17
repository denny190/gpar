#!/usr/bin/python3
import os
import re
import sys
import linecache

cwd = os.getcwd()

### TODO: NEED TO IMPLEMENT JOB NUMBERING TO KEEP TRACK OF VARIOUS ARRAYS THAT I NEED TO STITCH TOGETHER IN THE NED
### JOB NUMBERING WILL LIKELY HAVE SEPARATE TABLES FOR EACH TYPE OF INFO DUE TO VARYING AMOUNT OF ENTRIES PER JOB

# Initializing all options and setting them false
opt = False
freq = False
td = False

scf = False
coords = False
mulliken = False
bonds = False
angles = False

# Defining job identification strings
optString = "FOpt"
tdString = "TD-DFT"  # Not sure about this
freqString = "Freq"

# Defining archive indices arrays
archive_headers_array = []
archive_footers_array = []

# Opening file paths that are passed as arguments
path = cwd + "/tmp/runconfig.cfg.tmp"
runconfig = open(path, 'r')

runcfg_arr = []
for line in runconfig:
    runcfg_arr.append(line.strip())

# Getting options for current run


def getConfig(configfile):
    # Setting option variables as globals so they can be accessed and changed within this function
    global opt
    global freq
    global td
    global scf
    global coords
    global mulliken
    global bonds
    global angles

    options_array = []

    # Saves passed options in an array
    index_cfg_header = 0
    index_cfg_footer = configfile.index("--OPTIONS_END--")

    for line in range(index_cfg_header, index_cfg_footer):
        options_array.append(configfile[line])

    # Checks the state of each option (depending on its presence in options array) and changes its global value if its in the configfile
    if "opt=true" in options_array:
        opt = True
    if "freq=true" in options_array:
        freq = True
    if "td=true" in options_array:
        td = True

    if "scf=true" in options_array:
        scf = True
    if "coords=true" in options_array:
        coords = True
    if "mulliken=true" in options_array:
        mulliken = True
    if "bonds=true" in options_array:
        bonds = True
    if "angles=true" in options_array:
        angles = True

    return options_array  # CONSIDER REMOVING - RIGHT NOW ONLY DEBUG OUTPUT

# Filtering archives by job type


def filterLogs(configfile):

    selected_jobs = []
    global archive_headers_array
    global archive_footers_array

    global archive_head_begin
    global archive_head_end
    global archive_foot_begin
    global archive_foot_end

    # Loads the part of the config file that contains archive header and footer indices and filepaths
    archive_head_begin = configfile.index("ARCHIVE_HEADERS_START:")
    archive_head_end = configfile.index("ARCHIVE_HEADERS_END:")
    archive_headers_array = configfile[archive_head_begin + 1:archive_head_end]

    archive_foot_begin = configfile.index("ARCHIVE_FOOTERS_START:")
    archive_foot_end = configfile.index("ARCHIVE_FOOTERS_END:")
    archive_footers_array = configfile[archive_foot_begin + 1:archive_foot_end]

    # Checks presence of requested job in archive for each line in config header array
    for line in archive_headers_array:

        # Boolean that allows to pop filepath from config if it stays false
        found_match = False

        configline = line.split(":")
        file_path = configline[0]
        archive_head_index = configline[1]

        if (opt == True):
            if optString in linecache.getline(file_path, archive_head_index):
                selected_jobs.append(file_path)
                found_match = True

        elif (freq == True):
            if freqString in linecache.getline(file_path, archive_head_index):
                selected_jobs.append(file_path)
                found_match = True

        elif (td == True):
            if tdString in linecache.getline(file_path, archive_head_index):
                selected_jobs.append(file_path)
                found_match = True

        # Removes the archive entry from header array and corresponding index in footer array if no match found
        if (found_match == False):
            archive_footers_array.pop(archive_headers_array.index(line))
            archive_headers_array.pop(archive_headers_array.index(line))

        archive_head_begin = configfile.index("ARCHIVE_HEADERS_START:")
        archive_head_end = configfile.index("ARCHIVE_HEADERS_END:")
        archive_headers_array = configfile[archive_head_begin +
                                           1:archive_head_end]

        archive_foot_begin = configfile.index("ARCHIVE_FOOTERS_START:")
        archive_foot_end = configfile.index("ARCHIVE_FOOTERS_END:")
        archive_footers_array = configfile[archive_foot_begin +
                                           1:archive_foot_end]

# For each job inputted it finds the appropriate archive file, via the lineno specified in the config and cleans up the archive into a readable array


def _cleanArchiveForJob(configfile, job_no):

    # Loading start and end of archive for the specified job from the logfile so the archive can be accessed directly with linecache.
    job_header_entry = (
        (configfile[archive_head_begin + job_no]).split(":"))[1]
    job_footer_entry = (
        (configfile[archive_foot_begin + job_no]).split(":"))[1]
    path_to_file = ((configfile[archive_head_begin + job_no]).split(":"))[0]

    # DEBUG PRINTOUT
    print(job_footer_entry, job_footer_entry)

    # Acessing the logfile and loading lines within the range corresponding to the archive file
    job_archive = []
    for x in range(int(job_header_entry), int(job_footer_entry)):
        job_archive.append(linecache.getline(path_to_file, x))

    # Cleaning the archive entries into a readable form
    stripped_archive = [item.strip() for item in job_archive]
    clean_archive = ''.join(stripped_archive)
    split_archive = clean_archive.split("\\")
    split_archive = split_archive[2:]

    # DEBUG PRINTOUT
    print(split_archive)

    return split_archive

# Loads tables from config. TODO: Entries removed in filterLogs() have to be removed as well...


def _loadParamTables(configfile):

    opt_param_start = configfile.index("OPT_PARAMS_START:")
    opt_param_end = configfile.index("OPT_PARAMS_END:")
    opt_param_array = configfile[opt_param_start + 1: opt_param_end]

    mulliken_param_start = configfile.index("MULLIKEN_CHARGES_START:")
    mulliken_param_end = configfile.index("MULLIKEN_CHARGES_END:")
    mulliken_param_array = configfile[mulliken_param_start +
                                      1: mulliken_param_end]

    return opt_param_array, mulliken_param_array

# TODO: Using so many counters for iteration is a suboptimal and unreliable solution. I should find a different method.


def processData(configfile):

    # Loading linenos of appropriate parameter tables
    opt_param_array, mulliken_param_array = _loadParamTables(configfile)

    # For each job (iterated through via counter), access their archive (with linenos from configfile)
    counter = 1
    for line in archive_headers_array:
        filepath = (line.split(":"))[0]
        archive = _cleanArchiveForJob(configfile, counter)
        counter += 1

    # If flag coords is true then run the pipeline to extract coordinate info from the Optimized Parameters table
    if (bonds == True) or (angles == True) or (dihedrals == True):

        all_params = []

        for line in opt_param_array:

            opt_parameters = []

            # Get job path and lineno of the table in the logfile
            linesplit = line.split(":")
            filepath = linesplit[0]
            param_begin = int(linesplit[1])

            # Use linecache to access the opt_param tabl            print(all_params)e until the end of table is encounetered
            # Counter is set to 4 to skip the header and counter needs to be larger >4 to skip the --- denominator at the beggining of the table
            counter = 4
            while True:
                lineno = param_begin + counter
                temp_line = linecache.getline(filepath, lineno)
                opt_parameters.append(temp_line)

                if "--------------------------------------------------------------------------------" in temp_line and counter > 4:
                    # param_end = lineno
                    break

                # WIP error statement
                if counter > 1000:
                    print("ERROR while loading param array - Python script")
                    opt_parameters = []
                    break

                counter += 1

            all_params.append(opt_parameters)

        # Getting indices of R, A and D entries in the param table
        # index_R = []
        # index_A = []
        # index_D = []
        # for line in all_params[job_no]:
        #     counter = 0
        #     while True:
        #         if "R(" not in all_params[job_no][counter]:
        #             index_R[job_no] = counter
        #             counter += 1
        #         else:
        #             index_R[job_no] = counter + 1
        #             break

        #     counter = 0
        #     while True:
        #         if "A(" not in all_params[job_no][counter]:
        #             index_A[job_no] = counter
        #             counter += 1
        #         else:
        #             index_A[job_no] = counter + 1
        #             break

        #     counter = 0
        #     while True:
        #         if "D(" not in all_params[job_no][counter]:
        #             index_D[job_no] = counter
        #             counter += 1
        #         else:
        #             index_D[job_no] = counter + 1
        #             break

        # if (bonds == True):
        #     bond_list = []
        #     params_list = []
        #     counter = 1
        #     while "R(" in all_params[counter]:
        #         params_line = (lines[lines.index(line) + counter].split(" "))
        #         params_line = [item.strip(' ') for item in params_line]
        #         params_line = [item for item in params_line if item.strip()]

        #         params_list.append(params_line)
        #         bleft_index = params_line[2].index("(")
        #         bright_index = params_line[2].index(")")

        #         bond_list.append(
        #             params_line[2][bleft_index + 1: bright_index] + "," + params_line[3])
        #         counter += 1

    # If flag mulliken is true extract mulliken charges from file
    if (mulliken == True):

        all_mullikens = []

        for line in mulliken_param_array:

            mulliken_charges = []

            linesplit = line.split(":")
            filepath = linesplit[0]
            mulliken_begin = int(linesplit[1])

            counter = 0
            while True:
                lineno = mulliken_begin + counter
                temp_line = linecache.getline(filepath, lineno)
                mulliken_charges.append(temp_line)

                if "Sum of Mulliken charges =" in temp_line:
                    sum_of_mulliken = temp_line
                    mulliken_charges.pop(1)
                    mulliken_charges.pop(counter - 1)
                    # mulliken_end = lineno
                    break

                if counter > 1000:
                    print("ERROR while loading mulliken charges - Python script")
                    break

                counter += 1

            mulliken_charges = [item.strip() for item in mulliken_charges]
            all_mullikens.append(mulliken_charges)

    return all_params, all_mullikens


def assembleOutput(para, mull):
    
    concat_mull = []
    for x in range(len(mull[0])):
        for y in range(len(mull)):
            concat_mull.append(mull[y][x])

    concat_para = []
    for x in range(len(para[0])):
        for y in range(len(para)):
            concat_para.append(para[y][x])
    
    ### TODO: IMPLEMENT JOB NO TRACKER
    ### TODO: IMPLEMENT FUNCTION THAT CLEANS UP PARAM ARRAY
    jobno = 3
    with open("parser_out/output.csv", 'w') as output:
        while True:
            if len(concat_mull) > 0:
                str_to_write = concat_mull[0]
                for x in range(1, jobno):
                    str_to_write = str_to_write + "," + str(concat_mull[x])
                output.write(str_to_write + ",\n") 
                concat_mull = concat_mull[jobno:]
            else:
                break

# Retrieves options and locations from the config and returns arrays with which the rest of the script works
config_arr = getConfig(runcfg_arr)

# Filters logfiles by desired job types
selected_paths = filterLogs(runcfg_arr)

# Processes retrieved config and discerns what data to retrieve and what data to ignore based on the passed config
# Will probably have to pass a variable that specifies what to extract from each individual file in the following extractParams function
all_param_array, all_mulliken_array = processData(runcfg_arr)

# Assembles the collected data in a user-readable csv output.
assembleOutput(all_param_array, all_mulliken_array)

# DEBUGPRINTS
