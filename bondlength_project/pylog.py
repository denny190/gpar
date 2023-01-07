#!/usr/bin/python3
import os
import re
import sys
import linecache

cwd = os.getcwd()

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


def _getJobInfo(configfile, path_to_file, job_no):

    job_header_entry = (
        (configfile[archive_head_begin + job_no]).split(":"))[1]
    job_footer_entry = (
        (configfile[archive_foot_begin + job_no]).split(":"))[1]
    print(job_footer_entry, job_footer_entry)

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

# Loads parameter tables. TODO: Entries removed in filterLogs() have to be removed as well...


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

    opt_param_array, mulliken_param_array = _loadParamTables(configfile)

    counter = 1
    for line in archive_headers_array:
        filepath = (line.split(":"))[0]
        archive = _getJobInfo(configfile, filepath, counter)
        counter += 1

    if (coords == True):

        for line in opt_param_array:

            opt_parameters = []

            linesplit = line.split(":")
            filepath = linesplit[0]
            param_begin = int(linesplit[1])

            print(filepath)

            counter = 3
            while True:
                counter += 1
                lineno = param_begin + counter
                temp_line = linecache.getline(filepath, lineno)
                opt_parameters.append(temp_line)

                if "--------------------------------------------------------------------------------" in temp_line and counter > 4:
                    # param_end = lineno

                    # DEBUG PRINTOUT
                    for elem in opt_parameters:
                        print(elem.strip())
                    break

                if counter > 1000:
                    print("ERROR while loading param array - Python script")
                    opt_parameters = []
                    break

    if (mulliken == True):

        for line in mulliken_param_array:

            mulliken_charges = []

            linesplit = line.split(":")
            filepath = linesplit[0]
            mulliken_begin = int(linesplit[1])

            print(filepath)

            counter = -1
            while True:
                counter += 1
                lineno = mulliken_begin + counter
                temp_line = linecache.getline(filepath, lineno)
                mulliken_charges.append(temp_line)

                if "Sum of Mulliken charges =" in temp_line:
                    sum_of_mulliken = temp_line
                    mulliken_charges.pop(1)
                    mulliken_charges.pop(counter - 1)
                    # mulliken_end = lineno

                    # DEBUG PRINTOUT
                    for elem in mulliken_charges:
                        print(elem.strip())

                    break

                if counter > 1000:
                    print("ERROR while loading mulliken charges - Python script")
                    break


# Retrieves options and locations from the config and returns arrays with which the rest of the script works
config_arr = getConfig(runcfg_arr)

# Filters logfiles by desired job types
selected_paths = filterLogs(runcfg_arr)

# Processes retrieved config and discerns what data to retrieve and what data to ignore based on the passed config
# Will probably have to pass a variable that specifies what to extract from each individual file in the following extractParams function
processData(runcfg_arr)

# Extracting parameters that are specified for each logfile individually - will probably be wrapped in a for cycle later on
# extractParams()

# Assembles the collected data in a user-readable csv output.
# assembleOutput()

# DEBUGPRINTS
