#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The command-line script that is part of `pngglitch`."""

import os
import random
import argparse

from pngglitch import GlitchedPNGFile


def parse_args():
    """Interface to the command-line."""

    def insert_index_into_filename(filename):
        """Turns "a.png" into "a.%d.png"."""
        pre, _dot, suff = filename.rpartition('.')
        return pre + '.%d.' + suff

    def make_scrambled_filename(infile):
        """Returns a filename like "c40ac12baa3be95c.png"."""
        outfile = infile
        while os.path.isfile(outfile):
            randint = random.randint(0, 16**16 - 1)
            outfile = format(randint, '016x') + '.png'
        return outfile

    # Parse the incoming parameters.
    parser = argparse.ArgumentParser(
        description='Create glitch effects in PNG files '
        'by actually corrupting them.', )
    parser.add_argument(
        '--outfile',
        '-o',
        dest='outfile',
        action='store',
        type=str,
        help='Naming pattern for the output files. '
        'Defaults to "<infile>.%%d.png" if --num is '
        'specified and to "<infile>.corrupt.png" '
        'otherwise.',
    )
    parser.add_argument(
        '--num',
        '-N',
        dest='number',
        action='store',
        default=1,
        metavar='N',
        type=int,
        help='Number of output files. If not specified, '
        'one output file will be created.',
    )
    parser.add_argument(
        '-R',
        dest='randomize',
        action='store_true',
        default=False,
        help=format(random.randint(0, 16**16 - 1), '016x'),
    )
    parser.add_argument(
        '--amount',
        '-a',
        dest='amount',
        metavar='INT',
        action='store',
        type=int,
        default=100,
        help='Describes how many byte should be affected '
        'in total. Defaults to 100.',
    )
    parser.add_argument(
        '--mean',
        '-m',
        dest='mean',
        metavar='INT',
        action='store',
        type=int,
        default=20,
        help='Mean glitch size in bytes. Defaults to 20.',
    )
    parser.add_argument(
        '--deviation',
        '-d',
        dest='dev',
        metavar='INT',
        action='store',
        type=int,
        default=5,
        help='Standard deviation of glitch size in bytes. '
        'Defaults to 5.',
    )
    parser.add_argument(
        'infile',
        metavar='INFILE',
        action='store',
        type=str,
        help='PNG file to be corrupted.',
    )
    args = parser.parse_args()

    # Sanitize output filename.
    if args.outfile is None:
        if args.number > 1:
            # multi-file output
            args.outfile = insert_index_into_filename(args.infile)
        elif args.randomize:
            # single-file output, random name.
            args.outfile = make_scrambled_filename(args.infile)
        else:
            # single-file output, normal name.
            args.outfile = args.infile.rpartition('.')[0] + '.corrupt.png'
    elif args.number > 1:
        # catch ill-formatted multifile patterns
        try:
            args.outfile % 1
        except TypeError:
            args.outfile = insert_index_into_filename(args.outfile)
    else:
        # if single-file output name is a pattern, insert 1.
        try:
            args.outfile = args.outfile % 1
        except TypeError:
            pass
    return args


def main():
    """The main function."""
    args = parse_args()
    infile = GlitchedPNGFile(args.infile)
    outfiles = infile.glitch_file(
        copies=args.number,
        glitch_amount=args.amount,
        glitch_size=args.mean,
        glitch_dev=args.dev,
    )
    if args.number > 1:
        for i, outfile in enumerate(outfiles):
            outfile.write(args.outfile % i)
    else:
        outfiles.next().write(args.outfile)


if __name__ == '__main__':
    main()
