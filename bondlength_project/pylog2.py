#!/usr/bin/python3

import re
import os

def get_job_type(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(r'#\w+\s+(\w+)', line)
            if match:
                return match.group(1)
        return None

def get_functional(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(r'#\w+\s+(\w+)\s*\/', line)
            if match:
                return match.group(1)
        return None

def get_basis_set(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(r'#\w+\s+\w+\s*=\s*(\w+)', line)
            if match:
                return match.group(1)
        return None

def get_optimized_coordinates(log_file):
    with open(log_file, 'r') as f:
        coordinate_section = False
        coordinates = []
        for line in f:
            if 'Standard orientation:' in line:
                coordinate_section = True
                next(f) # skip the header row
            elif coordinate_section and len(line.split()) == 6:
                atom, x, y, z, *_ = line.split()
                coordinates.append((atom, x, y, z))
            elif coordinate_section and '-------------------------' in line:
                coordinate_section = False
        return coordinates

def get_scf_energies(log_file):
    with open(log_file, 'r') as f:
        energies = []
        for line in f:
            match = re.search(r'SCF Done:.*\s+(-\d+\.\d+)', line)
            if match:
                energies.append(float(match.group(1)))
        return energies

def get_mulliken_charges(log_file):
    with open(log_file, 'r') as f:
        charge_section = False
        charges = {}
        for line in f:
            if 'Mulliken charges:' in line:
                charge_section = True
                next(f) # skip the header row
            elif charge_section and len(line.split()) == 4:
                atom, _, _, charge = line.split()
                charges[atom] = float(charge)
            elif charge_section and 'Sum of Mulliken charges' in line:
                charge_section = False
        return charges

def parse_log_files(log_files):
    results = []
    for log_file in log_files:
        job_type = get_job_type(log_file)
        functional = get_functional(log_file)
        basis_set = get_basis_set(log_file)
        optimized_coordinates = get_optimized_coordinates(log_file)
        scf_energies = get_scf_energies(log_file)
        mulliken_charges = get_mulliken_charges(log_file)
        results.append({'file': log_file, 'job_type': job_type, 'functional': functional, 
                        'basis_set': basis_set, 'optimized_coordinates': optimized_coordinates,
                        'scf_energies': scf_energies, 'mulliken_charges': mulliken_charges})
    return results

# Example usage

cwd = os.getcwd()
path = cwd + "/tmp/paths.txt.tmp"
logpaths = open(path, 'r')

log_files = []
for line in logpaths:
    log_files.append(line.strip())

results = parse_log_files(log_files)

for result in results:
    print(f'File: {result["file"]}')
    print(f'Job type: {result["job_type"]}')
    print(f'Functional: {result["functional"]}')
    print(f'Basis set: {result["basis_set"]}')
    print(f'SCF Energies: {result["scf_energies"]}')
    print(f'Optimized Coordinates {result["optimized_coordinates"]}')
          