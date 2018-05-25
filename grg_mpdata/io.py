'''functions for reading and writing matpower data files'''

import argparse
import warnings
import re

from grg_mpdata.struct import Bus
from grg_mpdata.struct import BusName
from grg_mpdata.struct import Generator
from grg_mpdata.struct import GeneratorCost
from grg_mpdata.struct import Branch
from grg_mpdata.struct import DCLine
from grg_mpdata.struct import DCLineCost
from grg_mpdata.struct import Case

from grg_mpdata.exception import MPDataParsingError
from grg_mpdata.exception import MPDataValidationError
from grg_mpdata.exception import MPDataWarning

from collections import namedtuple
_Assignment = namedtuple('_Assignment', ['var', 'val'])


def _parse_cell(lines, index):
    return _parse_matlab_data(lines, index, '{', '}')

def _parse_matrix(lines, index):
    return _parse_matlab_data(lines, index, '[', ']')

def _parse_matlab_data(lines, index, start_char, end_char):
    last_index = len(lines)
    line_count = 0
    maxtrix = []
    columns = None

    # the first line defines the name of the matrix
    assert('=' in lines[index+line_count])
    matrix_assignment = lines[index+line_count].split('%')[0]
    matrix_assignment = matrix_assignment.strip()
    matrix_assignment_parts = matrix_assignment.split('=', 1)

    matrix_name = matrix_assignment_parts[0].strip()
    matrix_assignment_rhs = ''
    if len(matrix_assignment_parts) > 1:
        matrix_assignment_rhs = matrix_assignment_parts[1].strip()

    line_count += 1
    matrix_body_lines = [matrix_assignment_rhs]
    found_close_bracket = end_char in matrix_assignment_rhs

    while index + line_count < last_index and not found_close_bracket:
        line = lines[index+line_count].strip()

        if len(line) == 0 or line.startswith('%'):
            line_count += 1
            continue

        line = line.split('%')[0]

        if end_char in line:
            found_close_bracket = True

        if ';' in line:
            matrix_body_lines.append(line)
        else:
            matrix_body_lines.append(line + (';'))
        line_count += 1

    matrix_body = ' '.join(matrix_body_lines)
    matrix_body = matrix_body.strip().strip(start_char).replace(end_char+';', '').strip()
    matrix_body_rows = matrix_body.split(';')

    for row in matrix_body_rows:
        if len(row.split()) > 0:
            maxtrix.append(_split_line(row))
            if columns is not None:
                if columns != len(maxtrix[-1]):
                    raise MPDataParsingError('matlab matrix parsing error, '
                        'inconsistent number of items in each row.  Expected %d '
                        'given %d.' % (columns, len(maxtrix[-1])))
            else:
                columns = len(maxtrix[-1])

    return {'name': matrix_name, 'data': maxtrix, 'line_count': line_count}


single_quote_expr = re.compile('\'((\\.|[^\'])*?)\'')

def _split_line(mp_line):
    mp_line = mp_line.strip()
    #print(mp_line, single_quote_expr.match(mp_line))
    if single_quote_expr.match(mp_line):
        # splits a matpower string on white space while escaping text quoted with "'"
        # note that quotes will be stripped later, when data typing occurs

        #println(mp_line)
        tokens = []
        while len(mp_line) > 0 and single_quote_expr.match(mp_line):
            #println(mp_line)
            m = single_quote_expr.match(mp_line)

            if m.start(0) > 0:
                tokens.append(mp_line[:m.start(0)-1])
            
            tokens.append(m.group(0)) # replace(m.match, "\\'", "'")) # replace escaped quotes

            mp_line = mp_line[m.start(0)+len(m.group(0)):]

        if len(mp_line) > 0:
            tokens.append(mp_line)
        #print(tokens)

        items = []
        for token in tokens:
            if '\'' in token:
                items.append(token.strip().strip('\''))
            else:
                for part in token.split():
                    items.append(part.strip())
        #print(items)

        #return [strip(mp_line, '\'')]
        return items
    else:
        return mp_line.split()


def _extract_assignment_line(str):
    assert('=' in str)
    statement = str.split('%')[0]
    statement = statement.strip()
    if ';' in statement:
        statement = str.split(';')[0]
    assert(statement.count('=') == 1)
    parts = [x.strip() for x in statement.split('=', 1)]
    return _Assignment(*parts)


def parse_mp_case_file(mpFileName):
    '''opens the given path and parses it as matpower data

    Args:
        mpFileName(str): path to the a matpower data file
    Returns:
        Case: a grg_mpdata case
    '''
    with open(mpFileName, 'r') as mpFile:
        lines = mpFile.readlines()
    return parse_mp_case_lines(lines)


def parse_mp_case_str(mpString):
    '''parses a given string as matpower data

    Args:
        mpString(str): a matpower data file as a string
    Returns:
        Case: a grg_mpdata case
    '''
    return parse_mp_case_lines(mpString.split('\n'))


def parse_mp_case_lines(mpLines):
    '''parses a list of strings as matpower data

    Args:
        mpLines(list): the list of matpower data strings
    Returns:
        Case: a grg_mpdata case
    '''

    version = None
    name = None
    baseMVA = None

    bus = None
    gen = None
    branch = None
    gencost = None
    dcline = None
    dclinecost = None
    bus_name = None

    parsed_matrixes = []

    last_index = len(mpLines)
    index = 0
    while index < last_index:
        line = mpLines[index].strip()
        if len(line) == 0 or line.startswith('%'):
            index += 1
            continue

        if 'function mpc' in line:
            name = _extract_assignment_line(line).val
        elif 'mpc.version' in line:
            version = _extract_assignment_line(line).val
        elif 'mpc.baseMVA' in line:
            baseMVA = float(_extract_assignment_line(line).val)
        elif '[' in line:
            matrix = _parse_matrix(mpLines, index)
            parsed_matrixes.append(matrix)
            index += matrix['line_count']-1
        elif '{' in line:
            matrix = _parse_cell(mpLines, index)
            parsed_matrixes.append(matrix)
            index += matrix['line_count']-1
        index += 1

    for parsed_matrix in parsed_matrixes:
        if parsed_matrix['name'] == 'mpc.bus':
            bus = [Bus(*data) for data in parsed_matrix['data']]

        elif parsed_matrix['name'] == 'mpc.gen':
            gen = [Generator(index, *data)
                   for index, data in enumerate(parsed_matrix['data'])]

        elif parsed_matrix['name'] == 'mpc.branch':
            branch = [Branch(index, *data)
                      for index, data in enumerate(parsed_matrix['data'])]

        elif parsed_matrix['name'] == 'mpc.dcline':
            dcline = [DCLine(index, *data) 
                for index, data in enumerate(parsed_matrix['data'])]

        elif parsed_matrix['name'] == 'mpc.gencost':
            gencost = []
            for index, data in enumerate(parsed_matrix['data']):
                gencost.append(GeneratorCost(index, *data[:4], cost=data[4:]))

        elif parsed_matrix['name'] == 'mpc.dclinecost':
            dclinecost = []
            for index, data in enumerate(parsed_matrix['data']):
                dclinecost.append(DCLineCost(index, *data[:4], cost=data[4:]))

        elif parsed_matrix['name'] == 'mpc.bus_name':
            bus_name = [BusName(index, *data) 
                for index, data in enumerate(parsed_matrix['data'])]

        else:
            warnings.warn('unrecognized data matrix named \'%s\': data was '
                'ignored' % parsed_matrix['name'], MPDataWarning)

    case = Case(name, version, baseMVA, bus, gen, branch, gencost, dcline, dclinecost, bus_name)

    case.validate()

    return case


# from datetime import date, datetime
# date_tag = date.today().strftime('%d - %B - %Y')

def write_mp_case_file(output_file_location, case):
    '''writes a matpower case file

    Args:
        output_file_location (str): the path of the file to write
        case (Case): the data structure to write out
    '''

    output_file = open(output_file_location, 'w')
    output_file.write(case.to_matpower())
    output_file.close()


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description='''grg_mpdata.%(prog)s is a tool for processing Matpower 
            network data.''',

        epilog='''Please file bugs at...''',
    )

    parser.add_argument('file', help='a matpower file to parse (.m)')
    
    version = __import__('grg_mpdata').__version__
    parser.add_argument('-v', '--version', action='version', \
        version='grg_mpdata.%(prog)s (version '+version+')')

    return parser


# Note main(argv) used here instead of main(), to enable easy unit testing
def main(args):
    '''reads a matpower case file from a command line
    arguments and prints the parsed file to stdout

    Args:
        args: an argparse data structure
    '''

    case = parse_mp_case_file(args.file)
    print('Internal representation:')
    print(case)
    print('')

    print('Matpower representation:')
    print(case.to_matpower())
    print('')


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())
