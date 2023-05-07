import re
import sys
import argparse
from datetime import datetime
import numpy as np


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
        'end': re.compile(r'(?:Normal termination of Gaussian \d+ at )(.*)\.')
    }

    parsed = {'type': 'g16'}
    with infile as logfile:
        for line in logfile:
            line = line.strip()

            re_order = ['version', 'chk', 'route', 'input',
                        'hfenergy', 'opt', 'freq', 'hessian', 'tddft', 'force', 'end']

            for regex in re_order:
                try:
                    m = regexes[regex].search(line)
                except KeyError as e:
                    print('Key', e, 'not found in list of regular expressions.')
                    raise
                if m:
                    if regex == 'version':
                        parsed['version'] = next(
                            logfile).strip().replace(',', '')
                    elif regex == 'chk':
                        parsed['chk'] = m.group(1).replace('.chk', '') + '.chk'
                    elif regex == 'route':
                        parsed['route'] = [line[1:].strip()]
                        line = next(logfile).strip()
                        while line[0:3] != '---':
                            parsed['route'].append(line.strip())
                            line = next(logfile).strip()
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
                                    red_mass += next(
                                        logfile).strip().split()[3:]
                                    force_const += next(
                                        logfile).strip().split()[3:]
                                    ir_inten += next(
                                        logfile).strip().split()[3:]
                                    line = next(logfile)

                                    modes = []
                                    line = next(logfile).strip()
                                    while len(line.split()) > 3:
                                        modes.append(line.split())
                                        line = next(logfile).strip()
                                    modes = np.array(modes).astype(np.float)
                                    parsed['nm_atom_order'] = modes[:,
                                                                    1].astype(np.int).tolist()
                                    modes = np.hsplit(modes[:, 2:], 3)
                                    nmodes += [mode.tolist() for mode in modes]
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
                    elif regex == 'hessian':
                        parsed['hessian'] = parsed.setdefault('hessian', {})

                        if m.group(1):
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
                            venergy = float(line.split()[4])
                            osc_strength = float(line.split()[8][2:])
                            total_energy = None
                            contribs = []

                            line = next(logfile).strip()
                            while (line.split() and line.split()[0].isdigit()):
                                contrib = line.split()
                                del contrib[1]
                                contrib = [
                                    int(i) for i in contrib[:2]] + [float(contrib[2])]
                                contribs.append(contrib)
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
                    elif regex == 'end':
                        parsed['end'] = {'normal': True,
                                         'time': datetime.strptime(' '.join(m.group(1).split()),
                                                                   '%a %b %d %H:%M:%S %Y')}

                    break
    try:
        if parsed['opt']['success'] and not parsed['opt']['geom']:
            del parsed['opt']
    except KeyError:
        pass
    if 'end' not in parsed:
        parsed['end'] = {'normal': False}

    return parsed


def output(outputfile, parsed):
    print(parsed)


def main():
    args_parser = argparse.ArgumentParser(
        description='Process Gaussian 16 output files.')
    args_parser.add_argument('--file', '-f', type=argparse.FileType('r'))
    args_parser.add_argument('--output', '-o', type=argparse.FileType('w'))

    args = args_parser.parse_args()
    parsed = parse(args.file)
    output(args.output, parsed)


if __name__ == '__main__':
    main()

