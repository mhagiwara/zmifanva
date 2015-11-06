#! /usr/bin/python

"""
Script to extract only lines s.t. x mod m == n, where x is the line number.
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=int, default=0, help='Line number starts from this number.')
    parser.add_argument('--mod', default=None, type=int, help='value of m (divisor)')
    parser.add_argument('-n', default=None, type=int, help='value of n (modulo)')
    args = parser.parse_args()

    x = args.base
    for line in sys.stdin:
        if x % args.mod == args.n:
            sys.stdout.write(line)
        x += 1

if __name__ == '__main__':
    main()
