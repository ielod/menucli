#!/usr/bin/python2
from __future__ import print_function

import argparse
import sys

from menucli import menu


def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch daily offer from restaurant\'s Facebook page in CLI')
    subparsers = parser.add_subparsers(dest='command',
                                       help='Possible commands')
    list_parser = subparsers.add_parser('list', help='List configured restaurants')
    list_parser.add_argument('-d', '--detailed', dest='detailed', action='store_const',
                             const=True, default=False,
                             help='Display the list with the description')
    show_parser = subparsers.add_parser('show', help='Show a daily offer')
    show_parser.add_argument('restaurant', help='The restaurant\'s name')
    show_parser.add_argument('--oneline', dest='oneline', action='store_const',
                             const=True, default=False,
                             help='Display menu in one line')
    return parser.parse_args()


def main():
    args = parse_arguments()
    try:
        menucli = menu.MenuCLI()
        if args.command == 'show':
            print(menucli.show(args.restaurant, args.oneline))
        elif args.command == 'list':
            print(menucli.list(args.detailed))
    except menu.MenuException as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
