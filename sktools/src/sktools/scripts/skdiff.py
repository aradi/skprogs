#!/usr/bin/env python3

'''
Reads two Slater-Koster files and compares the numerical values stored in them.
'''


import argparse
import numpy as np
from sktools import PACKAGE_VERSION
from sktools.oldskfile import OldSKFile


USAGE = \
    '''
    Reads two SK-files and compares the numerical values stored in them.
    '''


def parseargs(cmdlineargs):
    '''Parse the program arguments.'''

    parser = argparse.ArgumentParser(description=USAGE)

    parser.add_argument('--version', action='version',
                        version='sktools {}'.format(PACKAGE_VERSION))

    msg = 'SK-files to compare'
    parser.add_argument('skfile', nargs=2, help=msg)

    msg = 'compare atomic values as stored in homonuclear SK-files'
    parser.add_argument('-a', '--atomic', dest='homo', action='store_true',
                        default=False, help=msg)

    msg = 'skip a given number of lines'
    parser.add_argument('-s', '--skip', dest='nskip', type=int, default=0,
                        help=msg)

    return parser.parse_args(args=cmdlineargs)


def compare_atomic_data(sk1, sk2):
    '''Compares the atomic data stored in two homonuclear SK-file.'''

    onsite_diffs = abs(sk1.onsites - sk2.onsites)
    maxpos = np.argmax(onsite_diffs)
    print('Onsite:      {:12.3e} {:5d}'.format(onsite_diffs[maxpos], maxpos))
    hubbu_diffs = abs(sk1.hubbardus - sk2.hubbardus)
    maxpos = np.argmax(hubbu_diffs)
    print('Hubbards:    {:12.3e} {:5d}'.format(hubbu_diffs[maxpos], maxpos))
    print('Hubbard (s): {:12.3e}'.format(hubbu_diffs[-1]))
    occ_diffs = abs(sk1.occupations - sk2.occupations)
    maxpos = np.argmax(occ_diffs)
    print('Occupations: {:12.3e} {:5d}'.format(occ_diffs[maxpos], maxpos))


def compare_integral_tables(sk1, sk2, nstart):
    '''Compares integral tables in two SK-files.'''

    if abs(sk1.dr - sk2.dr) > 1e-8:
        print('Incompatible grid separation ({:.3f} vs {:.3f}).')
        return

    nr = min(sk1.nr, sk2.nr)
    if nstart > nr:
        print('Tables too short.')
        return

    hamdiff = abs(abs(sk1.hamiltonian[nstart:nr, :])
                  - abs(sk2.hamiltonian[nstart:nr, :]))

    maxpos = np.argmax(hamdiff)
    maxinds = np.unravel_index(maxpos, hamdiff.shape)

    print('Hamiltonian: {:12.3e} ({:4d},{:3d})'.format(
        hamdiff[maxinds], maxinds[0] + nstart, maxinds[1]))

    overdiff = abs(abs(sk1.overlap[nstart:nr, :])
                   - abs(sk2.overlap[nstart:nr, :]))
    maxpos = np.argmax(overdiff)
    maxinds = np.unravel_index(maxpos, overdiff.shape)

    print('Overlap:     {:12.3e} ({:4d},{:3d})'.format(
        overdiff[maxinds], maxinds[0] + nstart + 1, maxinds[1] + 1))


def main(cmdlineargs=None):
    '''Main driver routine.'''

    args = parseargs(cmdlineargs)

    sk1 = OldSKFile.fromfile(args.skfile[0], args.homo)
    sk2 = OldSKFile.fromfile(args.skfile[1], args.homo)

    if args.homo:
        print('*** Atomic data:''')
        compare_atomic_data(sk1, sk2)
        print()

    print('*** Integral tables:')
    compare_integral_tables(sk1, sk2, args.nskip)


if __name__ == '__main__':
    main()
