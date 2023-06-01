#!/usr/bin/python3

import argparse
import os
import re
import sys
from datetime import datetime

print_order = ['type', 'version', 'chk', 'input', 'archive', 'hfenergy', 'opt', 'force', 'termination']

def print_dict(dictionary, indent=1, order=print_order):
    if order is not None:
        sorted_keys = sorted(dictionary.keys(), key=lambda x: order.index(x) if x in order else len(order))
    else:
        sorted_keys = dictionary.keys()

    for key in sorted_keys:
        value = dictionary[key]
        if isinstance(value, dict):
            print(' ' * indent + str(key) + ':')
            print_dict(value, indent + 4, order)
        elif isinstance(value, list):
            print(' ' * indent + str(key) + ':')
            for item in value:
                if isinstance(item, dict):
                    print_dict(item, indent + 4, order)
                else:
                    print(' ' * (indent + 4) + str(item))
        else:
            print(' ' * indent + str(key) + ': ' + str(value))


###
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse(infile):
    regexes = {
        'version': re.compile(r'Cite this work as:'),
        'chk': re.compile(r'^%chk=(\S+)'),
        'archive': re.compile(r'^1\\1'),
         #'geometry': re.compile(r''), #BONDS, ANGLES AND DIHEDRALS
         #'mulliken':
        'hfenergy': re.compile(r'^SCF Done:'),
        'input': re.compile(r'^Symbolic Z-matrix:'),
        'freq': re.compile(r'^Harmonic frequencies \(cm\*\*-1\)'),
        'opt': re.compile(r'Stationary point found.'),
        'force': re.compile(r'Center     Atomic                   Forces'),
        'cpu_time': re.compile(r'^Job cpu time:'),
        'termination': re.compile(r'Normal termination of Gaussian \d+ at (.*)\.')
    }

    parsed = {'type': 'g16'}

    with infile as logfile:
        for line in logfile:
            line = line.strip()

            #TODO: Implement option passing from .sh script HERE
            re_order = ['version', 'chk', 'input', 'archive', 'hfenergy', 'opt', 'force', 'termination']

            for regex in re_order:
                try:
                    match = regexes[regex].search(line)
                except KeyError as e:
                    print('Key', e, 'not found in list of regular expressions.')
                    raise
                if match:
                    if regex == 'version':
                        parsed['version'] = next(
                            logfile).strip().replace(',', '')
                        
                    elif regex == 'chk':
                        parsed['chk'] = match.group(1).replace('.chk', '') + '.chk'

                    elif regex == 'archive':
                        archive_array = []
                        archive_array.append(line[1:].strip())
                        try:
                            line = next(logfile).strip()
                            while True:
                                archive_array.append(line.strip())
                                if '@' in line:
                                    break
                                line = next(logfile).strip()
                                                                
                        except StopIteration:
                            pass
                        
                        joined_archive = ''.join(archive_array)
                        clean_archive = joined_archive.split("\\")
                        
                        #List comprehensions to remove bulky DipoleDeriv= and PolarDeriv= printouts that clutter the final output
                        clean_archive = [x for x in clean_archive if "DipoleDeriv=" not in x and "PolarDeriv=" not in x and len(x) <= 1000]

                        try:
                            parsed['archive'] = parsed['archive'] + clean_archive
                        except:
                            parsed['archive'] = clean_archive

                    elif regex == 'input':
                        line = next(logfile).strip()
                        parsed['input'] = {'charge': line.split()[2], 'multi': line.split()[5],
                                           'geom': []}

                        line = next(logfile).strip()
                        while line.split():
                            parsed['input']['geom'].append(
                                line.split())
                            line = next(logfile).strip()

                    elif regex == 'hfenergy':
                        parsed['hfenergy'] = float(line.split()[4])

                    elif regex == 'opt':
                        parsed['opt'] = {'success': True, 'geom': []}
                        geom = True

                        line = next(logfile).strip()
                        if (not line) or (line[0:4] == 'Grad'):
                            geom = False
                        if geom:
                            while ('Center     Atomic      Atomic             Coordinates (Angstroms)' not in line):
                                line = next(logfile).strip()
                            line = next(logfile)
                            line = next(logfile)

                            line = next(logfile).strip()
                            while line[0:3] != '---':
                                parsed['opt']['geom'].append(
                                    [int(i) for i in line.split()[0:3]] + [float(i) for i in line.split()[3:]])
                                line = next(logfile).strip()

                    elif regex == 'freq':
                        freq = True

                        while line.split()[0] != '1':
                            line = next(logfile).strip()
                            if not line:
                                freq = False
                                break

                        if freq:
                            while line.split():
                                freq_parsed = line.split()
                                symm, freq, red_mass, force_const, ir_inten, nmodes = [], [], [], [], [], []
                                line = next(logfile).strip()
                                while (len(line.split()) > 3 or not line.replace(' ', '').isdigit()):
                                    symm = symm + line.split()
                                    freq += next(logfile).strip().split()[2:]
                                    red_mass += next(logfile).strip().split()[3:]
                                    force_const += next(logfile).strip().split()[3:]
                                    ir_inten += next(logfile).strip().split()[3:]
                                    line = next(logfile)
                                    
                                    ###TODO: Fix Normal Modes!
                                    modes = []
                                    line = next(logfile).strip()
                                    while len(line.split()) > 3:
                                        modes.append([float(x) for x in line.split() if x.replace('.', '', 1).isdigit()])
                                        line = next(logfile).strip() 
                                    parsed['nm_atom_order'] = [int(mode[1]) for mode in modes if len(mode) > 1]
                                    
                                    modes = [mode[2:] for mode in modes]
                                    nmodes += [modes[i:i + 3] for i in range(0, len(modes), 3)]

                                    freq_parsed += line.split()
                                    if not line:
                                        break
                                    line = next(logfile).strip()

                                parsed['freq'] = freq_parsed
                                for mode in range(len(freq_parsed)):
                                    parsed['freq'][mode] = {
                                        'symmetry': symm[mode],
                                        'freq': float(freq[mode]),
                                        'reduced_mass': float(red_mass[mode]),
                                        'force_constant': float(force_const[mode]),
                                        'ir_intensity': float(ir_inten[mode]),
                                        'mode': nmodes[mode]
                                    }
        
                    elif regex == 'force':
                        line = next(logfile)
                        line = next(logfile)
                        parsed['force'] = []

                        line = next(logfile).strip()
                        while line[0:3] != '---':
                            parsed['force'].append([int(i) for i in line.split()[
                                                   0:2]] + [float(i) for i in line.split()[2:]])
                            line = next(logfile).strip()#

                    elif regex == 'mulliken':
                        pass

                    elif regex == 'cpu_time':
                        cpu_time = line.split()[3:]
                        parsed['cpu_time'] = float(cpu_time[0])*24*60*60 + \
                            float(cpu_time[2])*60*60 + \
                            float(cpu_time[4])*60 + float(cpu_time[8])
                        
                    elif regex == 'termination':
                        parsed['termination'] = {'normal': True,
                                         'time': datetime.strptime(' '.join(match.group(1).split()),
                                                                   '%a %b %d %H:%M:%S %Y')}

                    break
    try:
        if parsed['opt']['success'] and not parsed['opt']['geom']:
            del parsed['opt']

    except KeyError:
        pass

    if 'termination' not in parsed:
        parsed['termination'] = {'normal': False}
    
    return parsed
###

# Example usage
cwd = os.getcwd()
path = cwd + "/paths.txt.tmp"
logpaths = open(path, 'r')

log_files = []
for line in logpaths:
    log_files.append(line.strip())

for file in log_files:
    print("############################################\n" + file + "\n############################################")

    with open(file, 'r') as logfile:
        #parse(logfile)
        #print(parse(logfile))
        print_dict(parse(logfile))
        
