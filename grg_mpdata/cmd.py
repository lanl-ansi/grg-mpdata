'''functions for analyzing and transforming matpower data files'''

import argparse

from grg_mpdata.io import parse_mp_case_file

def compare_component_lists(list_1, list_2, comp_name, index_name = 'index'):
    '''compares two lists and prints the differences to stdout.  Objects in the
    lists are assumed to have an identification attribute.

    Args:
        list_1 (list): the first list
        list_2 (list): the second list
        comp_name (string): the name of components being compared
        index_name (string): the name of the object identification attribute
    Returns (int):
        returns the number of items that differed in the two lists
    '''

    if list_1 == None and list_2 == None:
        return 0

    if list_1 == None and list_2 != None:
        print('case 1 does not have %s but case 2 does' % (comp_name))
        return len(list_2)

    if list_1 != None and list_2 == None:
        print('case 1 has %s but case 2 does not' % (comp_name))
        return len(list_1)

    if not len(list_1) == len(list_2):
        print('%s counts: %s %s' % (comp_name, len(list_1), len(list_2)))
        return abs(len(list_1) - len(list_2))
    else:
        diff_count = 0
        for index in range(0, len(list_1)):
            comp_1 = list_1[index]
            comp_2 = list_2[index]
            if not comp_1 == comp_2:
                print('different %s (%d): %d %d' % (comp_name, index, 
                    getattr(comp_1, index_name), getattr(comp_1, index_name)))
                print('case 1: %s' % str(comp_1))
                print('case 2: %s' % str(comp_2))
                print('')
                diff_count += 1
        return diff_count


def diff(case_1, case_2):
    '''Compares two :class:`grg_mpdata.struct.Case` objects and prints the 
    differences to stdout.

    Args:
        case_1: the first Matpower case
        case_2: the second Matpower case
    Returns (int):
        returns the number of items that differed in the two cases
    '''

    diff_count = 0
    if not case_1 == case_2:
        if not case_1.name == case_2.name:
            print('names: %s %s' % (case_1.name, case_2.name))
            diff_count += 1
        if not case_1.version == case_2.version:
            print('versions: %s %s' % (case_1.version, case_2.version))
            diff_count += 1
        if not case_1.baseMVA == case_2.baseMVA:
            print('base mvas: %s %s' % (case_1.baseMVA, case_2.baseMVA))
            diff_count += 1

        if not case_1.bus == case_2.bus:
            diff_count += compare_component_lists(
                case_1.bus, case_2.bus, 'bus', 'bus_i')

        if not case_1.gen == case_2.gen:
            diff_count += compare_component_lists(
                case_1.gen, case_2.gen, 'gen')

        if not case_1.gencost == case_2.gencost:
            diff_count += compare_component_lists(
                case_1.gencost, case_2.gencost, 'gencost')

        if not case_1.branch == case_2.branch:
            diff_count += compare_component_lists(
                case_1.branch, case_2.branch, 'branch')

        if not case_1.dcline == case_2.dcline:
            diff_count += compare_component_lists(
                case_1.dcline, case_2.dcline, 'dcline')

    else:
        print('the files are identical')

    return diff_count

def eq(case_1, case_2):
    if case_1 == case_2:
        print('the case file data structures are identical')
        case_1_str = case_1.to_matpower()
        case_2_str = case_2.to_matpower()
        if case_1_str == case_2_str:
            print('the matpower strings are identical')
            return True
        else:
            print('the matpower encodings differ, this is most likely an '
                'implementation bug')
    else:
        print('the case files differ')
    return False


def build_cmd_parser():
    parser = argparse.ArgumentParser(
        description='''grg_mpdata.cmd provides tools for analyzing and
            transforming Matpower network datasets.''',

        epilog='''Please file bugs at...''',
    )

    subparsers = parser.add_subparsers(help='sub-commands', dest='cmd')

    parser_eq = subparsers.add_parser('eq', help = 'tests if two case files '
        'are equal')
    parser_eq.add_argument('file_1', help='a matpower data file (.m)')
    parser_eq.add_argument('file_2', help='a matpower data file (.m)')

    parser_diff = subparsers.add_parser('diff', help = 'presents the '
        'differences between two case files')
    parser_diff.add_argument('file_1', help='a matpower data file (.m)')
    parser_diff.add_argument('file_2', help='a matpower data file (.m)')

    #parser.add_argument('--foo', help='foo help')
    version = __import__('grg_mpdata').__version__
    parser.add_argument('-v', '--version', action='version', \
        version='grg_mpdata.cmd (version '+version+')')

    return parser


def main(args):
    '''reads a matpower case files and processes them based on command
    line arguments.

    Args:
        args: an argparse data structure
    '''

    if args.cmd == 'eq':
        case_1 = parse_mp_case_file(args.file_1)
        case_2 = parse_mp_case_file(args.file_2)

        return eq(case_1, case_2)

    if args.cmd == 'diff':
         case_1 = parse_mp_case_file(args.file_1)
         case_2 = parse_mp_case_file(args.file_2)

         return diff(case_1, case_2)


if __name__ == '__main__':
    import sys
    parser = build_cmd_parser()
    main(parser.parse_args())

