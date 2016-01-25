#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''querv

Usage:
  querv ship new <name>...
  querv ship <name> move <x> <y> [--speed=<kn>]
  querv ship shoot <x> <y>
  querv mine (set|remove) <x> <y> [--moored|--drifting]
  querv -h | --help
  querv --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.
'''

from __future__ import unicode_literals, print_function
from docopt import docopt

__version__ = "0.1.0"
__author__ = "Jesse Butcher"
__license__ = "MIT"


def main():
    '''Main entry point for the querv CLI.'''
    args = docopt(__doc__, version=__version__)
    print(args)

if __name__ == '__main__':
    main()