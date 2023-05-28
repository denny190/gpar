#!/usr/bin/python3

import argparse
import os
import re
import sys
from datetime import datetime

def print_dict(dictionary, indent=0):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            print(' ' * indent + str(key) + ':')
            print_dict(value, indent + 4)
        elif isinstance(value, list):
            print(' ' * indent + str(key) + ':')
            for item in value:
                if isinstance(item, dict):
                    print_dict(item, indent + 4)
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
        'route': re.compile(r'^#'),
        'hfenergy': re.compile(r'^SCF Done:'),
        'input': re.compile(r'^Symbolic Z-matrix:'),
        'tddft': re.compile(r'Convergence achieved on expansion vectors.'),
        'tddft_root_info': re.compile(r'^(This state)|^(Total Energy)|^(Copying)'),
        'freq': re.compile(r'^Harmonic frequencies \(cm\*\*-1\)'),
        'hessian': re.compile(r'^(The second derivative matrix:)|^(ITU=  0)'),
        'opt': re.compile(r'Stationary point found.'),
        'force': re.compile(r'Center     Atomic                   Forces'),
        'cpu_time': re.compile(r'^Job cpu time:'),
        'termination': re.compile(r'(?:Normal termination of Gaussian \d+ at )(.*)\.')
    }

    parsed = {'type': 'g16'}
    with infile as logfile:
        for line in logfile:
            line = line.strip()

            #TODO: Implement option passing from .sh script HERE
            re_order = ['version', 'chk', 'route', 'input','hfenergy', 'opt', 'freq', 'hessian', 'tddft', 'force', 'termination']

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
                    elif regex == 'route':
                        parsed['route'] = [line[1:].strip()]
                        try:
                            line = next(logfile).strip()
                            while line[0:3] != '---':
                                parsed['route'].append(line.strip())
                                line = next(logfile).strip()
                        except StopIteration:
                            pass
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
                        parsed['energy'] = float(line.split()[4])
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
                        continue
                        freq = True
                        while line.split()[0] != '1':
                            line = next(logfile).strip()
                            if not line:
                                freq = False
                                break
                        if freq:
                            while line.split():
                                freq_parsed = line.split()
                                symm, freq, red_mass, force_const, ir_inten, raman_act, depolar_P, depolar_U, nmodes = [], [], [], [], [], [], [], [], []
                                line = next(logfile).strip()
                                while (len(line.split()) > 3 or not line.replace(' ', '').isdigit()):
                                    symm = symm + line.split()
                                    freq += next(logfile).strip().split()[2:]
                                    red_mass += next(logfile).strip().split()[3:]
                                    force_const += next(logfile).strip().split()[3:]
                                    ir_inten += next(logfile).strip().split()[3:]
                                    raman_act += next(logfile).strip().split()[3:]
                                    depolar_P += next(logfile).strip().split()[3:]
                                    depolar_U += next(logfile).strip().split()[3:]
                                    line = next(logfile).strip()
                                    
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
                                        'raman_activity': float(raman_act[mode]),
                                        'mode': nmodes[mode]
                                    }
                    elif regex == 'hessian':
                        parsed['hessian'] = parsed.setdefault('hessian', {})

                        if match.group(1):
                            line = next(logfile).strip()
                            raw_matrix = []
                            while not line.startswith('ITU='):
                                line = next(logfile).strip()
                                submatrix = []
                                while (isfloat(line.split()[-1]) and
                                       not line.startswith('ITU=')):
                                    submatrix.append([float(i)
                                                      for i in line.split()[1:]])
                                    line = next(logfile).strip()
                                raw_matrix.append(submatrix)
                            matrix = raw_matrix[0]
                            for submatrix in raw_matrix[1:]:
                                for i, v in enumerate(reversed(submatrix)):
                                    matrix[-i-1] += v
                            parsed['hessian']['matrix'] = matrix

                        parsed['hessian']['eigenvalues'] = []
                        line = next(logfile).strip()
                        while line.startswith('Eigenvalues ---'):
                            parsed['hessian']['eigenvalues'] += [
                                float(i) for i in line.split()[2:]]
                            line = next(logfile).strip()
                    elif regex == 'tddft':
                        parsed['tddft'] = {}
                        for _ in range(4):
                            next(logfile)
                        line = next(logfile).strip()
                        while (line.split() and 'electric dipole moments' not in line):
                            line = next(logfile).strip()
                        next(logfile)

                        parsed['tddft'] = {'electric_dipole_moments': []}
                        line = next(logfile).strip()
                        while (line.split() and line.split()[0].isdigit()):
                            parsed['tddft']['electric_dipole_moments'].append(
                                line.split()[1:])
                            line = next(logfile).strip()

                        while (line[0:3] != '***' and 'Excitation energies and oscillator strengths:' not in line):
                            line = next(logfile).strip()
                        next(logfile)
                        line = next(logfile).strip()
                        parsed['tddft']['excited_states'] = []
                        
                        while line.startswith('Excited State'):
                            break
                            venergy = float(line.split()[4])
                            osc_strength = float(line.split()[8][2:])
                            total_energy = None
                            contribs = []

                            line = next(logfile).strip()
                            while (line.split() and line.split()[0].isdigit()):
                                #TODO: Fix Excited States!
                                print(line)
                                contrib = line.split()
                                del contrib[1]

                                if len(contrib) >= 3:
                                    contrib = [
                                        int(float(i)) for i in contrib[:2]] + [float(contrib[2])]
                                    contribs.append(contrib)
                                else:
                                    line = next(logfile).strip()
                                    break  # Added break condition

                                line = next(logfile).strip()
                            root_match = regexes['tddft_root_info'].search(
                                line)
                            while root_match:
                                if root_match.group(2):
                                    total_energy = float(line.split()[4])
                                line = next(logfile).strip()
                                root_match = regexes['tddft_root_info'].search(
                                    line)

                            parsed['tddft']['excited_states'].append({
                                'excitation_energy': venergy,
                                'oscillator_strength': osc_strength,
                                'contributions': contribs,
                                'total_energy': total_energy
                            })

                            line = next(logfile).strip()
                    elif regex == 'force':
                        line = next(logfile)
                        line = next(logfile)
                        parsed['force'] = []

                        line = next(logfile).strip()
                        while line[0:3] != '---':
                            parsed['force'].append([int(i) for i in line.split()[
                                                   0:2]] + [float(i) for i in line.split()[2:]])
                            line = next(logfile).strip()
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
path = cwd + "/tmp/paths.txt.tmp"
logpaths = open(path, 'r')

log_files = []
for line in logpaths:
    log_files.append(line.strip())

for file in log_files:
    with open(file, 'r') as logfile:
        print(parse(logfile))
        #print_dict(parse(logfile))
        

